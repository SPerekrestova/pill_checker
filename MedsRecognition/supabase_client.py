import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()  # if you’re using a .env file

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://<random-id>.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "your-anon-key")

def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)