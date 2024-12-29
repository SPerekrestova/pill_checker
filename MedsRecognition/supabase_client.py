import os

from dotenv import load_dotenv
from supabase import create_client, Client


def get_supabase_client() -> Client:
    load_dotenv(dotenv_path='MedsRecognition/.env')
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    return create_client(url, key)