from supabase_client import get_supabase_client

def sign_up_user(email: str, password: str):
    supabase = get_supabase_client()
    # This will create a new user in your Supabase authentication
    response = supabase.auth.sign_up(
        {
            "email": email,
            "password": password,
        }
    )
    return response

def sign_in_user(email: str, password: str):
    supabase = get_supabase_client()
    response = supabase.auth.sign_in(
        {
            "email": email,
            "password": password,
        }
    )
    return response