-- Initial schema for PillChecker database

-- Create profiles table
CREATE TABLE profiles (
    id uuid references auth.users not null COMMENT 'UUID of the associated Supabase user',
    username text unique COMMENT 'Display name of the user',
    bio TEXT COMMENT 'User''s biography or description',
    created_at TIMESTAMP,
    updated_at TIMESTAMP,

    primary key (id),
    unique(username),
    constraint username_length check (char_length(username) >= 3)
);

-- Create index on profiles
CREATE UNIQUE INDEX ix_profile_user_id ON profiles (user_id);
CREATE INDEX idx_profile_display_name ON profiles (display_name);

alter table profiles enable row level security;

create policy "Public profiles are viewable by the owner."
  on profiles for select
  using ( auth.uid() = id );

create policy "Users can insert their own profile."
  on profiles for insert
  with check ( auth.uid() = id );

create policy "Users can update own profile."
  on profiles for update
  using ( auth.uid() = id );

-- Set up Realtime
begin;
  drop publication if exists supabase_realtime;
  create publication supabase_realtime;
commit;
alter publication supabase_realtime add table profiles;

-- Create medications table
CREATE TABLE medications (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    profile_id BIGINT NOT NULL COMMENT 'ID of the profile this medication belongs to',
    title VARCHAR(255) COMMENT 'Name or title of the medication',
    scan_date TIMESTAMP COMMENT 'Date when the medication was scanned',
    active_ingredients TEXT COMMENT 'List of active ingredients in text format',
    scanned_text TEXT COMMENT 'Raw text extracted from the medication scan',
    dosage VARCHAR(255) COMMENT 'Dosage information',
    prescription_details JSON COMMENT 'Additional prescription details in JSON format',
    scan_url text COMMENT 'URL of the uploaded medication scan',
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES profiles(id)
);

-- Create indexes on medications
CREATE INDEX idx_medications_profile_id ON medications (profile_id);
CREATE INDEX idx_medications_scan_date ON medications (scan_date);
CREATE INDEX idx_medications_title ON medications (title);

-- Set up Storage
insert into storage.buckets (id, name)
values ('scans', 'scans');

create policy "Scaned images are publicly accessible."
  on storage.objects for select
  using ( bucket_id = 'scans' );

create policy "Anyone can upload a scan."
  on storage.objects for insert
  with check ( bucket_id = 'scans' );

create policy "Anyone can update a scan."
  on storage.objects for update
  with check ( bucket_id = 'scans' );
