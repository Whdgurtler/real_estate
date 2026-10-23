"""Create the initial property pipeline schema.

Revision ID: 0001_property_pipeline
Revises:
"""
from alembic import op
import sqlalchemy as sa


revision = "0001_property_pipeline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "properties",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("address", sa.String(length=300), nullable=False),
        sa.Column("city", sa.String(length=120), nullable=False),
        sa.Column("state", sa.String(length=2), nullable=False),
        sa.Column("zip_code", sa.String(length=10), nullable=True),
        sa.Column("county", sa.String(length=120), nullable=True),
        sa.Column("county_fips", sa.String(length=5), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("source_name", sa.String(length=200), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("asking_price", sa.Float(), nullable=True),
        sa.Column("estimated_repairs", sa.Float(), nullable=True),
        sa.Column("bedrooms", sa.Integer(), nullable=True),
        sa.Column("bathrooms", sa.Float(), nullable=True),
        sa.Column("square_feet", sa.Integer(), nullable=True),
        sa.Column("year_built", sa.Integer(), nullable=True),
        sa.Column("annual_property_tax", sa.Float(), nullable=True),
        sa.Column("assessed_value", sa.Float(), nullable=True),
        sa.Column("tax_rate_percent", sa.Float(), nullable=True),
        sa.Column("annual_insurance_estimate", sa.Float(), nullable=True),
        sa.Column("insurance_source", sa.String(length=200), nullable=True),
        sa.Column("expected_market_rent_monthly", sa.Float(), nullable=True),
        sa.Column("hud_fmr_monthly", sa.Float(), nullable=True),
        sa.Column("pha_payment_standard_monthly", sa.Float(), nullable=True),
        sa.Column("pha_name", sa.String(length=200), nullable=True),
        sa.Column("pha_id", sa.String(length=32), nullable=True),
        sa.Column("pha_program_status", sa.String(length=20), nullable=False),
        sa.Column("voucher_waitlist_status", sa.String(length=20), nullable=False),
        sa.Column("open_voucher_count", sa.Integer(), nullable=True),
        sa.Column("population_current", sa.Integer(), nullable=True),
        sa.Column("population_previous", sa.Integer(), nullable=True),
        sa.Column("population_growth_percent", sa.Float(), nullable=True),
        sa.Column("population_data_year", sa.Integer(), nullable=True),
        sa.Column("violent_crime_rate_per_100k", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_properties_id", "properties", ["id"], unique=False)
    op.create_index("ix_properties_state", "properties", ["state"], unique=False)
    op.create_index("ix_properties_zip_code", "properties", ["zip_code"], unique=False)
    op.create_index("ix_properties_county_fips", "properties", ["county_fips"], unique=False)
    op.create_index("ix_properties_source_type", "properties", ["source_type"], unique=False)

    op.create_table(
        "data_evidence",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("metric", sa.String(length=80), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("source_name", sa.String(length=200), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("confidence", sa.String(length=20), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["property_id"], ["properties.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_data_evidence_id", "data_evidence", ["id"], unique=False)
    op.create_index("ix_data_evidence_metric", "data_evidence", ["metric"], unique=False)

    if op.get_bind().dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
        op.execute("ALTER TABLE properties ADD COLUMN location geometry(Point, 4326)")
        op.execute(
            """
            CREATE FUNCTION sync_property_location() RETURNS trigger AS $$
            BEGIN
                IF NEW.latitude IS NULL OR NEW.longitude IS NULL THEN
                    NEW.location = NULL;
                ELSE
                    NEW.location = ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326);
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql
            """
        )
        op.execute(
            """
            CREATE TRIGGER sync_property_location_trigger
            BEFORE INSERT OR UPDATE OF latitude, longitude ON properties
            FOR EACH ROW EXECUTE FUNCTION sync_property_location()
            """
        )
        op.execute(
            "CREATE INDEX ix_properties_location ON properties USING GIST (location)"
        )


def downgrade():
    if op.get_bind().dialect.name == "postgresql":
        op.execute("DROP TRIGGER IF EXISTS sync_property_location_trigger ON properties")
        op.execute("DROP FUNCTION IF EXISTS sync_property_location()")
        op.execute("DROP INDEX IF EXISTS ix_properties_location")
    op.drop_index("ix_data_evidence_metric", table_name="data_evidence")
    op.drop_index("ix_data_evidence_id", table_name="data_evidence")
    op.drop_table("data_evidence")
    op.drop_index("ix_properties_source_type", table_name="properties")
    op.drop_index("ix_properties_county_fips", table_name="properties")
    op.drop_index("ix_properties_zip_code", table_name="properties")
    op.drop_index("ix_properties_state", table_name="properties")
    op.drop_index("ix_properties_id", table_name="properties")
    op.drop_table("properties")
