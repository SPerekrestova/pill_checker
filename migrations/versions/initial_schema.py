"""Consolidated schema

Revision ID: consolidated_schema
Revises:
Create Date: 2025-02-25 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "consolidated_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create profiles table
    op.create_table(
        "profiles",
        sa.Column(
            "id",
            postgresql.UUID(),
            primary_key=True,
            nullable=False,
            comment="UUID of the associated Supabase user",
        ),
        sa.Column(
            "username",
            sa.Text(),
            nullable=True,
            unique=True,
            comment="Display name of the user",
        ),
        sa.Column("bio", sa.Text(), nullable=True, comment="User's biography or description"),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
        sa.CheckConstraint("char_length(username) >= 3", name="username_length"),
    )
    op.create_index("ix_profile_user_id", "profiles", ["id"], unique=True)
    op.create_index("idx_profile_display_name", "profiles", ["username"])

    # Create medications table
    op.create_table(
        "medications",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column(
            "profile_id",
            postgresql.UUID(),
            nullable=False,
            comment="ID of the profile this medication belongs to",
        ),
        sa.Column(
            "title",
            sa.String(length=255),
            nullable=True,
            comment="Name or title of the medication",
        ),
        sa.Column(
            "scan_date",
            sa.TIMESTAMP(),
            nullable=True,
            comment="Date when the medication was scanned",
        ),
        sa.Column(
            "active_ingredients",
            sa.Text(),
            nullable=True,
            comment="List of active ingredients in text format",
        ),
        sa.Column(
            "scanned_text",
            sa.Text(),
            nullable=True,
            comment="Raw text extracted from the medication scan",
        ),
        sa.Column("dosage", sa.String(length=255), nullable=True, comment="Dosage information"),
        sa.Column(
            "prescription_details",
            sa.JSON(),
            nullable=True,
            comment="Additional prescription details in JSON format",
        ),
        sa.Column(
            "scan_url",
            sa.Text(),
            nullable=True,
            comment="URL of the uploaded medication scan",
        ),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(["profile_id"], ["profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_medications_profile_id", "medications", ["profile_id"], unique=False)
    op.create_index("idx_medications_scan_date", "medications", ["scan_date"], unique=False)
    op.create_index("idx_medications_title", "medications", ["title"], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index("idx_medications_title", table_name="medications")
    op.drop_index("idx_medications_scan_date", table_name="medications")
    op.drop_index("idx_medications_profile_id", table_name="medications")
    op.drop_table("medications")

    op.drop_index("idx_profile_display_name", table_name="profiles")
    op.drop_index("ix_profile_user_id", table_name="profiles")
    op.drop_table("profiles")

    # Note: We are not including the scanned_images table as it's not in the SQL script
