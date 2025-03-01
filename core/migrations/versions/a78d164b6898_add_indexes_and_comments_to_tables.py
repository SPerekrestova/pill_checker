"""Add indexes and comments to tables

Revision ID: a78d164b6898
Revises: 57b1e3499f7a
Create Date: 2025-02-24 21:42:12.574900

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a78d164b6898"
down_revision: Union[str, None] = "57b1e3499f7a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "medication",
        "profile_id",
        existing_type=sa.BIGINT(),
        comment="ID of the profile this medication belongs to",
        existing_nullable=False,
    )
    op.alter_column(
        "medication",
        "title",
        existing_type=sa.VARCHAR(length=255),
        comment="Name or title of the medication",
        existing_nullable=True,
    )
    op.alter_column(
        "medication",
        "scan_date",
        existing_type=postgresql.TIMESTAMP(),
        comment="Date when the medication was scanned",
        existing_nullable=True,
    )
    op.alter_column(
        "medication",
        "active_ingredients",
        existing_type=sa.TEXT(),
        comment="List of active ingredients in text format",
        existing_nullable=True,
    )
    op.alter_column(
        "medication",
        "scanned_text",
        existing_type=sa.TEXT(),
        comment="Raw text extracted from the medication scan",
        existing_nullable=True,
    )
    op.alter_column(
        "medication",
        "dosage",
        existing_type=sa.VARCHAR(length=255),
        comment="Dosage information",
        existing_nullable=True,
    )
    op.alter_column(
        "medication",
        "prescription_details",
        existing_type=postgresql.JSON(astext_type=sa.Text()),
        comment="Additional prescription details in JSON format",
        existing_nullable=True,
    )
    op.create_index("idx_medication_profile_id", "medication", ["profile_id"], unique=False)
    op.create_index("idx_medication_scan_date", "medication", ["scan_date"], unique=False)
    op.create_index("idx_medication_title", "medication", ["title"], unique=False)
    op.alter_column(
        "profile",
        "user_id",
        existing_type=sa.UUID(),
        comment="UUID of the associated Supabase user",
        existing_nullable=False,
    )
    op.alter_column(
        "profile",
        "display_name",
        existing_type=sa.TEXT(),
        comment="Display name of the user",
        existing_nullable=True,
    )
    op.alter_column(
        "profile",
        "bio",
        existing_type=sa.TEXT(),
        comment="User's biography or description",
        existing_nullable=True,
    )
    op.create_index("idx_profile_display_name", "profile", ["display_name"], unique=False)
    op.alter_column(
        "uploadedimage",
        "image",
        existing_type=sa.VARCHAR(length=255),
        comment="Name or identifier of the uploaded image",
        existing_nullable=False,
    )
    op.alter_column(
        "uploadedimage",
        "uploaded_at",
        existing_type=postgresql.TIMESTAMP(),
        comment="Timestamp when the image was uploaded",
        existing_nullable=True,
    )
    op.alter_column(
        "uploadedimage",
        "file_path",
        existing_type=sa.TEXT(),
        comment="Path where the image is stored in the system",
        existing_nullable=True,
    )
    op.create_index("idx_uploadedimage_uploaded_at", "uploadedimage", ["uploaded_at"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("idx_uploadedimage_uploaded_at", table_name="uploadedimage")
    op.alter_column(
        "uploadedimage",
        "file_path",
        existing_type=sa.TEXT(),
        comment=None,
        existing_comment="Path where the image is stored in the system",
        existing_nullable=True,
    )
    op.alter_column(
        "uploadedimage",
        "uploaded_at",
        existing_type=postgresql.TIMESTAMP(),
        comment=None,
        existing_comment="Timestamp when the image was uploaded",
        existing_nullable=True,
    )
    op.alter_column(
        "uploadedimage",
        "image",
        existing_type=sa.VARCHAR(length=255),
        comment=None,
        existing_comment="Name or identifier of the uploaded image",
        existing_nullable=False,
    )
    op.drop_index("idx_profile_display_name", table_name="profile")
    op.alter_column(
        "profile",
        "bio",
        existing_type=sa.TEXT(),
        comment=None,
        existing_comment="User's biography or description",
        existing_nullable=True,
    )
    op.alter_column(
        "profile",
        "display_name",
        existing_type=sa.TEXT(),
        comment=None,
        existing_comment="Display name of the user",
        existing_nullable=True,
    )
    op.alter_column(
        "profile",
        "user_id",
        existing_type=sa.UUID(),
        comment=None,
        existing_comment="UUID of the associated Supabase user",
        existing_nullable=False,
    )
    op.drop_index("idx_medication_title", table_name="medication")
    op.drop_index("idx_medication_scan_date", table_name="medication")
    op.drop_index("idx_medication_profile_id", table_name="medication")
    op.alter_column(
        "medication",
        "prescription_details",
        existing_type=postgresql.JSON(astext_type=sa.Text()),
        comment=None,
        existing_comment="Additional prescription details in JSON format",
        existing_nullable=True,
    )
    op.alter_column(
        "medication",
        "dosage",
        existing_type=sa.VARCHAR(length=255),
        comment=None,
        existing_comment="Dosage information",
        existing_nullable=True,
    )
    op.alter_column(
        "medication",
        "scanned_text",
        existing_type=sa.TEXT(),
        comment=None,
        existing_comment="Raw text extracted from the medication scan",
        existing_nullable=True,
    )
    op.alter_column(
        "medication",
        "active_ingredients",
        existing_type=sa.TEXT(),
        comment=None,
        existing_comment="List of active ingredients in text format",
        existing_nullable=True,
    )
    op.alter_column(
        "medication",
        "scan_date",
        existing_type=postgresql.TIMESTAMP(),
        comment=None,
        existing_comment="Date when the medication was scanned",
        existing_nullable=True,
    )
    op.alter_column(
        "medication",
        "title",
        existing_type=sa.VARCHAR(length=255),
        comment=None,
        existing_comment="Name or title of the medication",
        existing_nullable=True,
    )
    op.alter_column(
        "medication",
        "profile_id",
        existing_type=sa.BIGINT(),
        comment=None,
        existing_comment="ID of the profile this medication belongs to",
        existing_nullable=False,
    )
    # ### end Alembic commands ###
