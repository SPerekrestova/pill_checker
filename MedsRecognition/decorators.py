from django.shortcuts import redirect
from functools import wraps
from MedsRecognition.models import Profile

def supabase_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        supabase_user = request.session.get('supabase_user')
        if not supabase_user:
            return redirect('login')
        try:
            request.auth_user = Profile.objects.get(id=supabase_user['id'])
        except Profile.DoesNotExist:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view