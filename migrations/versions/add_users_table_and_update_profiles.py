"""Add users table and update profiles

Revision ID: add_users_profiles
Revises: consolidated_schema
Create Date: 2025-11-17 18:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "add_users_profiles"
down_revision: Union[str, None] = "consolidated_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table for FastAPI-Users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("hashed_password", sa.String(length=1024), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=True, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=True, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # Add user_id column to profiles table
    op.add_column(
        "profiles",
        sa.Column("user_id", postgresql.UUID(), nullable=True),
    )

    # For existing profiles, we'll need to handle this manually or set them to NULL initially
    # In a production migration, you'd want to create corresponding users first

    # Make user_id NOT NULL after data migration
    # op.alter_column("profiles", "user_id", nullable=False)

    # Add foreign key constraint
    op.create_foreign_key(
        "fk_profiles_user_id", "profiles", "users", ["user_id"], ["id"], ondelete="CASCADE"
    )

    # Create index on user_id
    op.create_index("idx_profile_user_id", "profiles", ["user_id"], unique=True)


def downgrade() -> None:
    # Drop foreign key and index from profiles
    op.drop_index("idx_profile_user_id", table_name="profiles")
    op.drop_constraint("fk_profiles_user_id", "profiles", type_="foreignkey")
    op.drop_column("profiles", "user_id")

    # Drop users table
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
