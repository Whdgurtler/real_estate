"""Scope data feeds to priority counties and source categories.

Revision ID: 0004_county_scoped_data_feeds
Revises: 0003_daily_data_automation
"""
from alembic import op
import sqlalchemy as sa


revision = "0004_county_scoped_data_feeds"
down_revision = "0003_daily_data_automation"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "data_feeds",
        sa.Column(
            "source_category",
            sa.String(length=32),
            nullable=False,
            server_default="other",
        ),
    )
    op.add_column(
        "data_feeds",
        sa.Column("county_fips", sa.String(length=5), nullable=True),
    )
    op.create_index(
        "ix_data_feeds_county_fips",
        "data_feeds",
        ["county_fips"],
        unique=False,
    )


def downgrade():
    op.drop_index("ix_data_feeds_county_fips", table_name="data_feeds")
    op.drop_column("data_feeds", "county_fips")
    op.drop_column("data_feeds", "source_category")
