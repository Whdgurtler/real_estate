"""Support authorized, recurring downloadable source feeds.

Revision ID: 0005_downloadable_source_feeds
Revises: 0004_county_scoped_data_feeds
"""
from alembic import op
import sqlalchemy as sa


revision = "0005_downloadable_source_feeds"
down_revision = "0004_county_scoped_data_feeds"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "data_feeds",
        sa.Column(
            "refresh_interval_days",
            sa.Integer(),
            nullable=False,
            server_default="7",
        ),
    )
    op.add_column(
        "data_feeds",
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "data_feed_source_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("data_feed_id", sa.Integer(), nullable=False),
        sa.Column("record_key", sa.String(length=64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["data_feed_id"],
            ["data_feeds.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "data_feed_id",
            "record_key",
            name="uq_data_feed_source_record_key",
        ),
    )
    op.create_index(
        "ix_data_feed_source_records_id",
        "data_feed_source_records",
        ["id"],
        unique=False,
    )
    op.create_index(
        "ix_data_feed_source_records_data_feed_id",
        "data_feed_source_records",
        ["data_feed_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        "ix_data_feed_source_records_data_feed_id",
        table_name="data_feed_source_records",
    )
    op.drop_index(
        "ix_data_feed_source_records_id",
        table_name="data_feed_source_records",
    )
    op.drop_table("data_feed_source_records")
    op.drop_column("data_feeds", "last_synced_at")
    op.drop_column("data_feeds", "refresh_interval_days")
