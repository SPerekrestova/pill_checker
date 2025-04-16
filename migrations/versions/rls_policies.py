"""Add RLS policies for Supabase roles

Revision ID: add_rls_policies
Revises: consolidated_schema
Create Date: 2025-03-01 22:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_rls_policies"
down_revision: Union[str, None] = "consolidated_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable Row Level Security on tables
    op.execute("ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE medications ENABLE ROW LEVEL SECURITY;")

    # Create policies for profiles table

    # Policy for users to select their own profile
    op.execute(
        """
        CREATE POLICY select_own_profile ON profiles
        FOR SELECT USING (
            auth.uid() = id
        );
    """
    )

    # Policy for users to update their own profile
    op.execute(
        """
        CREATE POLICY update_own_profile ON profiles
        FOR UPDATE USING (
            auth.uid() = id
        );
    """
    )

    # Policy for users to insert their own profile with proper ID
    op.execute(
        """
        CREATE POLICY insert_own_profile ON profiles
        FOR INSERT WITH CHECK (
            auth.uid() = id
        );
    """
    )

    # Create policies for medications table

    # Policy for users to select their own medications
    op.execute(
        """
        CREATE POLICY select_own_medications ON medications
        FOR SELECT USING (
            auth.uid() = profile_id
        );
    """
    )

    # Policy for users to insert their own medications
    op.execute(
        """
        CREATE POLICY insert_own_medications ON medications
        FOR INSERT WITH CHECK (
            auth.uid() = profile_id
        );
    """
    )

    # Policy for users to update their own medications
    op.execute(
        """
        CREATE POLICY update_own_medications ON medications
        FOR UPDATE USING (
            auth.uid() = profile_id
        );
    """
    )

    # Policy for users to delete their own medications
    op.execute(
        """
        CREATE POLICY delete_own_medications ON medications
        FOR DELETE USING (
            auth.uid() = profile_id
        );
    """
    )

    # Grant permissions to roles

    # authenticated users can use all tables with RLS applied
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON profiles TO authenticated;")
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON medications TO authenticated;")
    op.execute("GRANT USAGE, SELECT ON SEQUENCE medications_id_seq TO authenticated;")

    # anonymous users have no access to these tables by default

    # Force RLS for all roles except supabase_admin (which bypasses RLS)
    op.execute("ALTER TABLE profiles FORCE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE medications FORCE ROW LEVEL SECURITY;")

    # Create policy to allow supabase_admin to bypass RLS
    op.execute(
        """
        CREATE POLICY supabase_admin_access_profiles ON profiles
        TO supabase_admin
        USING (true);
    """
    )

    op.execute(
        """
        CREATE POLICY supabase_admin_access_medications ON medications
        TO supabase_admin
        USING (true);
    """
    )

    # Create policy to allow service_role to bypass RLS
    op.execute(
        """
        CREATE POLICY service_role_access_profiles ON profiles
        TO service_role
        USING (true);
    """
    )

    op.execute(
        """
        CREATE POLICY service_role_access_medications ON medications
        TO service_role
        USING (true);
    """
    )


def downgrade() -> None:
    # Remove all policies
    op.execute("DROP POLICY IF EXISTS select_own_profile ON profiles;")
    op.execute("DROP POLICY IF EXISTS update_own_profile ON profiles;")
    op.execute("DROP POLICY IF EXISTS insert_own_profile ON profiles;")
    op.execute("DROP POLICY IF EXISTS supabase_admin_access_profiles ON profiles;")
    op.execute("DROP POLICY IF EXISTS service_role_access_profiles ON profiles;")

    op.execute("DROP POLICY IF EXISTS select_own_medications ON medications;")
    op.execute("DROP POLICY IF EXISTS insert_own_medications ON medications;")
    op.execute("DROP POLICY IF EXISTS update_own_medications ON medications;")
    op.execute("DROP POLICY IF EXISTS delete_own_medications ON medications;")
    op.execute(
        "DROP POLICY IF EXISTS supabase_admin_access_medications ON medications;"
    )
    op.execute("DROP POLICY IF EXISTS service_role_access_medications ON medications;")

    # Revoke permissions
    op.execute("REVOKE SELECT, INSERT, UPDATE, DELETE ON profiles FROM authenticated;")
    op.execute(
        "REVOKE SELECT, INSERT, UPDATE, DELETE ON medications FROM authenticated;"
    )
    op.execute(
        "REVOKE USAGE, SELECT ON SEQUENCE medications_id_seq FROM authenticated;"
    )

    # Disable Row Level Security
    op.execute("ALTER TABLE profiles DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE medications DISABLE ROW LEVEL SECURITY;")
