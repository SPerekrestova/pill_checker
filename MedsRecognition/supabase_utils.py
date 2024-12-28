from django.conf import settings
from supabase import create_client, Client

def get_supabase_client() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)