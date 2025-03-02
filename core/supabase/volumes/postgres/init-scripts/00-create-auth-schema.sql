-- Create auth schema
CREATE SCHEMA IF NOT EXISTS auth;

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON SCHEMA auth TO postgres;

-- Drop the enum from public schema if it exists
DROP TYPE IF EXISTS public.factor_type;

-- Create all enum types that GoTrue needs for its migrations
DO $$
BEGIN
    -- factor_type enum
    IF NOT EXISTS (SELECT 1 FROM pg_type JOIN pg_namespace ON pg_type.typnamespace = pg_namespace.oid WHERE typname = 'factor_type' AND nspname = 'auth') THEN
        CREATE TYPE auth.factor_type AS ENUM ('totp', 'webauthn', 'phone');
    END IF;

    -- factor_status enum
    IF NOT EXISTS (SELECT 1 FROM pg_type JOIN pg_namespace ON pg_type.typnamespace = pg_namespace.oid WHERE typname = 'factor_status' AND nspname = 'auth') THEN
        CREATE TYPE auth.factor_status AS ENUM ('verified', 'unverified');
    END IF;

    -- aal_level enum
    IF NOT EXISTS (SELECT 1 FROM pg_type JOIN pg_namespace ON pg_type.typnamespace = pg_namespace.oid WHERE typname = 'aal_level' AND nspname = 'auth') THEN
        CREATE TYPE auth.aal_level AS ENUM ('aal1', 'aal2', 'aal3');
    END IF;

    -- code_challenge_method enum
    IF NOT EXISTS (SELECT 1 FROM pg_type JOIN pg_namespace ON pg_type.typnamespace = pg_namespace.oid WHERE typname = 'code_challenge_method' AND nspname = 'auth') THEN
        CREATE TYPE auth.code_challenge_method AS ENUM ('s256', 'plain');
    END IF;

    -- one_time_token_type enum
    IF NOT EXISTS (SELECT 1 FROM pg_type JOIN pg_namespace ON pg_type.typnamespace = pg_namespace.oid WHERE typname = 'one_time_token_type' AND nspname = 'auth') THEN
        CREATE TYPE auth.one_time_token_type AS ENUM ('confirmation_token', 'reauthentication_token', 'recovery_token', 'email_change_token_new', 'email_change_token_current', 'phone_change_token');
    END IF;
END
$$;
