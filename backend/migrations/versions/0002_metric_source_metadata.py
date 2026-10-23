"""Store provenance separately for property, tax, rent, PHA, and market metrics.

Revision ID: 0002_metric_source_metadata
Revises: 0001_property_pipeline
"""
from alembic import op
import sqlalchemy as sa


revision = "0002_metric_source_metadata"
down_revision = "0001_property_pipeline"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "properties",
        sa.Column(
            "source_metadata",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
    )


def downgrade():
    op.drop_column("properties", "source_metadata")
