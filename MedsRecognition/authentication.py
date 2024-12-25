import os
import jwt
from django.contrib.auth.models import AnonymousUser
from rest_framework import authentication, exceptions


class SupabaseAuthentication(authentication.BaseAuthentication):
    """
    Custom DRF authentication class that:
    1. Reads the "Authorization: Bearer <token>" header
    2. Verifies the JWT
    3. Returns a user or raises an exception
    """

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None  # No credentials, DRF will treat as "unauthenticated"

        try:
            # auth_header format: "Bearer <token>"
            prefix, token = auth_header.split(' ')
            if prefix.lower() != 'bearer':
                raise exceptions.AuthenticationFailed('Invalid token prefix')

            # Depending on your Supabase config, you may:
            # 1. Use a public key or secret from environment
            # 2. Or retrieve it from Supabase using a JWKS endpoint if configured
            # For simplicity, let's assume you have a JWT secret:
            SUPABASE_JWT_SECRET = os.getenv('SUPABASE_JWT_SECRET', 'replace_me')

            decoded_token = jwt.decode(
                token,
                SUPABASE_JWT_SECRET,
                algorithms=["HS256"]
            )

            # If decoding succeeds, token is valid. You can fetch user details
            # from 'decoded_token'. E.g., "sub" might contain user_id or email:
            user_id = decoded_token.get('sub', None)

            # Option 1: If you want to match against a Django user model:
            # from django.contrib.auth import get_user_model
            # User = get_user_model()
            # user = User.objects.get(pk=user_id)  # or lookup by email

            # For a simple example, just return an AnonymousUser
            user = AnonymousUser()

            # The second value returned from authenticate is the "auth" object (token)
            return (user, token)

        except (ValueError, jwt.PyJWTError, exceptions.AuthenticationFailed) as e:
            raise exceptions.AuthenticationFailed(str(e))