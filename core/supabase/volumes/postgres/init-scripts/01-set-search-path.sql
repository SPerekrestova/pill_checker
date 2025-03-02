-- Set search_path to include auth schema
ALTER DATABASE postgres SET search_path TO "$user", public, extensions, auth;
