from datetime import datetime
import ipaddress
import re
from typing import Literal
from urllib.parse import parse_qsl, urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .jurisdictions import county_jurisdictions


SourceType = Literal[
    "conventional",
    "tax_sale",
    "code_enforcement",
    "foreclosure",
    "pre_foreclosure",
    "other",
]
ProgramStatus = Literal["confirmed", "not_found", "unknown"]
WaitlistStatus = Literal["open", "closed", "unknown"]
Confidence = Literal[
    "user_provided",
    "user_estimate",
    "official_record",
    "official_estimate",
    "provider_estimate",
    "unknown",
]
DataFeedConnector = Literal["socrata", "arcgis", "json_api"]
DataFeedTarget = Literal["property_leads", "property_enrichment"]
DataFeedCategory = Literal[
    "assessor",
    "tax_sale",
    "code_enforcement",
    "foreclosure",
    "pre_foreclosure",
    "crime",
    "population",
    "pha",
    "other",
]
PRIORITY_COUNTY_FIPS = frozenset(
    jurisdiction["county_fips"] for jurisdiction in county_jurisdictions()
)
IngestiblePropertyField = Literal[
    "address",
    "city",
    "state",
    "zip_code",
    "county",
    "county_fips",
    "latitude",
    "longitude",
    "asking_price",
    "estimated_repairs",
    "bedrooms",
    "bathrooms",
    "square_feet",
    "year_built",
    "annual_property_tax",
    "assessed_value",
    "tax_rate_percent",
    "annual_insurance_estimate",
    "expected_market_rent_monthly",
    "hud_fmr_monthly",
    "pha_payment_standard_monthly",
    "pha_name",
    "pha_id",
    "pha_program_status",
    "voucher_waitlist_status",
    "open_voucher_count",
    "population_current",
    "population_previous",
    "population_growth_percent",
    "violent_crime_rate_per_100k",
]


class EvidenceSourceInput(BaseModel):
    source_name: str = Field(min_length=1, max_length=200)
    source_url: str | None = Field(default=None, max_length=2000)
    confidence: Confidence = "user_provided"


class DataFeedCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    connector: DataFeedConnector
    target: DataFeedTarget = "property_leads"
    source_category: DataFeedCategory = "other"
    source_type: SourceType
    county_fips: str | None = Field(default=None, pattern=r"^\d{5}$")
    field_mapping: dict[IngestiblePropertyField, str]
    enabled: bool = True
    confidence: Confidence = "official_record"
    domain: str | None = Field(default=None, max_length=255)
    dataset_id: str | None = Field(default=None, max_length=32)
    query_url: str | None = Field(default=None, max_length=2000)
    where: str | None = Field(default=None, max_length=2000)
    max_records: int = Field(default=1000, ge=1, le=5000)
    record_id_field: str | None = Field(default=None, max_length=200)
    records_path: str | None = Field(default=None, max_length=200)
    query_params: dict[str, str] = Field(default_factory=dict)
    auth_env_var: str | None = Field(default=None, pattern=r"^[A-Z][A-Z0-9_]{1,100}$")
    auth_query_param: str | None = Field(
        default=None, pattern=r"^[A-Za-z][A-Za-z0-9_]{0,99}$"
    )

    @field_validator(
        "name",
        "domain",
        "dataset_id",
        "query_url",
        "record_id_field",
        "records_path",
        "auth_query_param",
        "county_fips",
    )
    @classmethod
    def trim_optional_strings(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else None

    @model_validator(mode="after")
    def validate_connector_configuration(self):
        if not self.field_mapping:
            raise ValueError("At least one field mapping is required")
        if self.target == "property_leads":
            if not {"address", "city", "state"}.issubset(self.field_mapping):
                raise ValueError("Lead feed mapping must include address, city, and state")
        else:
            matches_by_fips = "county_fips" in self.field_mapping or self.county_fips is not None
            matches_by_zip = {"zip_code", "state"}.issubset(self.field_mapping)
            matches_by_county = {"county", "state"}.issubset(self.field_mapping)
            if not (matches_by_fips or matches_by_zip or matches_by_county):
                raise ValueError(
                    "Enrichment feeds must map county_fips, zip_code plus state, or county plus state"
                )
            metric_fields = set(self.field_mapping) - {
                "county_fips",
                "zip_code",
                "state",
                "county",
            }
            area_metrics = {
                "population_current",
                "population_previous",
                "population_growth_percent",
                "violent_crime_rate_per_100k",
                "hud_fmr_monthly",
                "pha_payment_standard_monthly",
                "pha_name",
                "pha_id",
                "pha_program_status",
                "voucher_waitlist_status",
                "open_voucher_count",
                "expected_market_rent_monthly",
            }
            if not metric_fields:
                raise ValueError("Enrichment feeds must map at least one metric to update")
            if not metric_fields.issubset(area_metrics):
                raise ValueError(
                    "Enrichment feeds may only map area-level population, crime, rent, or PHA metrics"
                )
        if self.county_fips:
            if self.county_fips not in PRIORITY_COUNTY_FIPS:
                raise ValueError("County FIPS must identify a county in a prioritized state")
        if self.connector == "socrata":
            if not self.domain or not self.dataset_id:
                raise ValueError("Socrata sources require a domain and dataset ID")
            if not all(character.isalnum() or character in ".-" for character in self.domain):
                raise ValueError("Socrata domain may only contain a hostname")
            if self.domain.startswith(".") or self.domain.endswith(".") or ".." in self.domain:
                raise ValueError("Socrata domain must be a valid hostname")
            _validate_public_https_url(f"https://{self.domain}")
            if not self.dataset_id.replace("-", "").isalnum():
                raise ValueError("Socrata dataset ID contains invalid characters")
        elif self.connector == "arcgis":
            if not self.query_url:
                raise ValueError("ArcGIS sources require a FeatureServer layer URL")
            _validate_public_https_url(self.query_url)
        else:
            if not self.query_url:
                raise ValueError("JSON API sources require an endpoint URL")
            _validate_public_https_url(self.query_url)
        if self.where and any(ord(character) < 32 for character in self.where):
            raise ValueError("Source filter contains invalid control characters")
        sensitive_parameter = re.compile(
            r"(?:api[_-]?key|access[_-]?token|auth|password|secret|token)",
            re.IGNORECASE,
        )
        if any(sensitive_parameter.search(key) for key in self.query_params):
            raise ValueError(
                "Do not store credentials in query parameters; use auth_env_var instead"
            )
        if self.auth_query_param and not self.auth_env_var:
            raise ValueError("auth_query_param requires auth_env_var")
        return self


class DataFeedEnabledUpdate(BaseModel):
    enabled: bool


def _validate_public_https_url(value: str) -> None:
    parsed = urlparse(value)
    hostname = (parsed.hostname or "").lower().rstrip(".")
    try:
        port = parsed.port
    except ValueError as error:
        raise ValueError("Source URL has an invalid port") from error
    if (
        parsed.scheme != "https"
        or not hostname
        or parsed.username
        or parsed.password
        or parsed.fragment
        or hostname == "localhost"
        or hostname.endswith(".localhost")
        or hostname.endswith(".local")
        or port not in (None, 443)
    ):
        raise ValueError("Source URL must be a public HTTPS URL without credentials or fragments")
    if any(
        re.search(
            r"(?:api[_-]?key|access[_-]?token|auth|password|secret|token)",
            key,
            re.IGNORECASE,
        )
        for key, _ in parse_qsl(parsed.query)
    ):
        raise ValueError("Do not store credentials in source URLs; use auth_env_var instead")
    try:
        ip = ipaddress.ip_address(hostname)
    except ValueError:
        return
    if not ip.is_global:
        raise ValueError("Source URL must not use a private or non-routable IP address")


class PropertyCreate(BaseModel):
    address: str = Field(min_length=1, max_length=300)
    city: str = Field(min_length=1, max_length=120)
    state: str = Field(min_length=2, max_length=2)
    zip_code: str | None = Field(default=None, max_length=10)
    county: str | None = Field(default=None, max_length=120)
    county_fips: str | None = Field(default=None, pattern=r"^\d{5}$")
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)

    source_type: SourceType = "conventional"
    source_name: str | None = Field(default=None, max_length=200)
    source_url: str | None = Field(default=None, max_length=2000)
    source_metadata: dict[str, EvidenceSourceInput] = Field(default_factory=dict)

    asking_price: float | None = Field(default=None, gt=0)
    estimated_repairs: float | None = Field(default=None, ge=0)
    bedrooms: int | None = Field(default=None, ge=0, le=30)
    bathrooms: float | None = Field(default=None, ge=0, le=30)
    square_feet: int | None = Field(default=None, ge=0)
    year_built: int | None = Field(default=None, ge=1600, le=2200)

    annual_property_tax: float | None = Field(default=None, ge=0)
    assessed_value: float | None = Field(default=None, ge=0)
    tax_rate_percent: float | None = Field(default=None, ge=0, le=25)
    annual_insurance_estimate: float | None = Field(default=None, ge=0)
    insurance_source: str | None = Field(default=None, max_length=200)

    expected_market_rent_monthly: float | None = Field(default=None, ge=0)
    hud_fmr_monthly: float | None = Field(default=None, ge=0)
    pha_payment_standard_monthly: float | None = Field(default=None, ge=0)
    pha_name: str | None = Field(default=None, max_length=200)
    pha_id: str | None = Field(default=None, max_length=32)
    pha_program_status: ProgramStatus = "unknown"
    voucher_waitlist_status: WaitlistStatus = "unknown"
    open_voucher_count: int | None = Field(default=None, ge=0)

    population_current: int | None = Field(default=None, ge=0)
    population_previous: int | None = Field(default=None, ge=0)
    population_growth_percent: float | None = Field(default=None, ge=-100, le=1000)
    population_data_year: int | None = Field(default=None, ge=1900, le=2200)
    violent_crime_rate_per_100k: float | None = Field(default=None, ge=0)

    @field_validator("state")
    @classmethod
    def normalize_state(cls, value: str) -> str:
        value = value.strip().upper()
        if len(value) != 2 or not value.isalpha():
            raise ValueError("State must be a two-letter abbreviation")
        return value

    @field_validator("address", "city")
    @classmethod
    def trim_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank")
        return value


class PropertyRead(PropertyCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    evidence: list["EvidenceRead"] = []


class EvidenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    metric: str
    value: str
    source_name: str
    source_url: str | None
    confidence: str
    observed_at: datetime


class UnderwritingAssumptions(BaseModel):
    vacancy_rate_percent: float = Field(default=5, ge=0, le=100)
    maintenance_rate_percent: float = Field(default=8, ge=0, le=100)
    management_rate_percent: float = Field(default=8, ge=0, le=100)
    yield_weight: float = Field(default=0.55, ge=0, le=1)
    growth_weight: float = Field(default=0.25, ge=0, le=1)
    safety_weight: float = Field(default=0.20, ge=0, le=1)

    @model_validator(mode="after")
    def weights_must_have_positive_total(self):
        if self.yield_weight + self.growth_weight + self.safety_weight <= 0:
            raise ValueError("At least one score weight must be greater than zero")
        return self
