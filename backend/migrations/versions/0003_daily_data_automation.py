"""Add configurable daily source ingestion and sync history.

Revision ID: 0003_daily_data_automation
Revises: 0002_metric_source_metadata
"""
from alembic import op
import sqlalchemy as sa


revision = "0003_daily_data_automation"
down_revision = "0002_metric_source_metadata"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "data_feeds",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("connector", sa.String(length=32), nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("config", sa.JSON(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_data_feeds_id", "data_feeds", ["id"], unique=False)

    op.create_table(
        "data_feed_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("data_feed_id", sa.Integer(), nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("external_key", sa.String(length=64), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["data_feed_id"], ["data_feeds.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["property_id"], ["properties.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "data_feed_id", "external_key", name="uq_data_feed_record_external"
        ),
    )
    op.create_index(
        "ix_data_feed_records_id", "data_feed_records", ["id"], unique=False
    )
    op.create_index(
        "ix_data_feed_records_property_id",
        "data_feed_records",
        ["property_id"],
        unique=False,
    )

    op.create_table(
        "sync_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("trigger", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("scheduled_date", sa.Date(), nullable=True),
        sa.Column("active_slot", sa.String(length=32), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_results", sa.JSON(), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scheduled_date", name="uq_sync_run_scheduled_date"),
        sa.UniqueConstraint("active_slot", name="uq_sync_run_active_slot"),
    )
    op.create_index("ix_sync_runs_id", "sync_runs", ["id"], unique=False)


def downgrade():
    op.drop_index("ix_sync_runs_id", table_name="sync_runs")
    op.drop_table("sync_runs")
    op.drop_index("ix_data_feed_records_property_id", table_name="data_feed_records")
    op.drop_index("ix_data_feed_records_id", table_name="data_feed_records")
    op.drop_table("data_feed_records")
    op.drop_index("ix_data_feeds_id", table_name="data_feeds")
    op.drop_table("data_feeds")
