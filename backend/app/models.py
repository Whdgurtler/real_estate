from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .db import Base


def utc_now():
    return datetime.now(timezone.utc)


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(300), nullable=False)
    city = Column(String(120), nullable=False)
    state = Column(String(2), nullable=False, index=True)
    zip_code = Column(String(10), nullable=True, index=True)
    county = Column(String(120), nullable=True)
    county_fips = Column(String(5), nullable=True, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    source_type = Column(String(32), nullable=False, default="conventional", index=True)
    source_name = Column(String(200), nullable=True)
    source_url = Column(Text, nullable=True)
    source_metadata = Column(JSON, nullable=False, default=dict)

    asking_price = Column(Float, nullable=True)
    estimated_repairs = Column(Float, nullable=True)
    bedrooms = Column(Integer, nullable=True)
    bathrooms = Column(Float, nullable=True)
    square_feet = Column(Integer, nullable=True)
    year_built = Column(Integer, nullable=True)

    annual_property_tax = Column(Float, nullable=True)
    assessed_value = Column(Float, nullable=True)
    tax_rate_percent = Column(Float, nullable=True)
    annual_insurance_estimate = Column(Float, nullable=True)
    insurance_source = Column(String(200), nullable=True)

    expected_market_rent_monthly = Column(Float, nullable=True)
    hud_fmr_monthly = Column(Float, nullable=True)
    pha_payment_standard_monthly = Column(Float, nullable=True)
    pha_name = Column(String(200), nullable=True)
    pha_id = Column(String(32), nullable=True)
    pha_program_status = Column(String(20), nullable=False, default="unknown")
    voucher_waitlist_status = Column(String(20), nullable=False, default="unknown")
    open_voucher_count = Column(Integer, nullable=True)

    population_current = Column(Integer, nullable=True)
    population_previous = Column(Integer, nullable=True)
    population_growth_percent = Column(Float, nullable=True)
    population_data_year = Column(Integer, nullable=True)
    violent_crime_rate_per_100k = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

    evidence = relationship(
        "DataEvidence",
        back_populates="property",
        cascade="all, delete-orphan",
        order_by="DataEvidence.id",
    )


class DataEvidence(Base):
    __tablename__ = "data_evidence"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    metric = Column(String(80), nullable=False, index=True)
    value = Column(Text, nullable=False)
    source_name = Column(String(200), nullable=False)
    source_url = Column(Text, nullable=True)
    confidence = Column(String(20), nullable=False, default="user_provided")
    observed_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    property = relationship("Property", back_populates="evidence")


class DataFeed(Base):
    __tablename__ = "data_feeds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    connector = Column(String(32), nullable=False)
    source_category = Column(String(32), nullable=False, default="other")
    source_type = Column(String(32), nullable=False)
    county_fips = Column(String(5), nullable=True, index=True)
    config = Column(JSON, nullable=False)
    enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)


class DataFeedRecord(Base):
    __tablename__ = "data_feed_records"
    __table_args__ = (
        UniqueConstraint("data_feed_id", "external_key", name="uq_data_feed_record_external"),
    )

    id = Column(Integer, primary_key=True, index=True)
    data_feed_id = Column(Integer, ForeignKey("data_feeds.id", ondelete="CASCADE"), nullable=False)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    external_key = Column(String(64), nullable=False)
    last_seen_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)


class SyncRun(Base):
    __tablename__ = "sync_runs"

    id = Column(Integer, primary_key=True, index=True)
    trigger = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default="queued")
    scheduled_date = Column(Date, nullable=True, unique=True)
    active_slot = Column(String(32), nullable=True, unique=True)
    started_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    source_results = Column(JSON, nullable=False, default=list)
    error = Column(Text, nullable=True)
