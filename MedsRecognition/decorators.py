from django.shortcuts import redirect
from functools import wraps

def supabase_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'supabase_user' not in request.session:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view