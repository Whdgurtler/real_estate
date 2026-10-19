from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


SourceType = Literal["conventional", "tax_sale", "code_enforcement", "other"]
ProgramStatus = Literal["confirmed", "not_found", "unknown"]
WaitlistStatus = Literal["open", "closed", "unknown"]


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
