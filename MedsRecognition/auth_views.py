import io

from PIL import Image
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import logout

from MedsRecognition.auth_service import sign_up_user, sign_in_user
from MedsRecognition.decorators import supabase_login_required
from MedsRecognition.forms import ProfileUpdateForm
from MedsRecognition.models import Profile


def supabase_signup_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        username = request.POST.get('username', email)

        try:
            result = sign_up_user(email, password)
            if result and result.user:
                # Create a profile for the new user
                Profile.objects.create(user_id=result.user.id, display_name=username)
                messages.success(request, "Signed up successfully. Please log in.")
                return render(request, 'recognition/login.html')
            else:
                messages.error(request, "Sign-up failed. Check your email/password.")
        except Exception as e:
            messages.error(request, f"Sign-up error: {e}")

    return render(request, 'recognition/signup.html')


def supabase_login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            result = sign_in_user(email, password)
            if result and hasattr(result, 'user'):
                request.session['supabase_user'] = result.user.id
                request.user = result.user

                # Ensure the profile exists
                Profile.objects.get_or_create(user_id=result.user.id, defaults={'display_name': email})

                messages.success(request, "Successfully logged in!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid credentials or login failed.")
        except Exception as e:
            messages.error(request, f"Supabase login error: {e}")
    return render(request, 'recognition/login.html')


def supabase_logout_view(request):
    logout(request)
    return render(request, 'recognition/logout.html')


@supabase_login_required
def update_profile(request):
    profile = Profile.objects.get(user_id=request.user.id)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('dashboard')
    else:
        form = ProfileUpdateForm(instance=profile)
    return render(request, 'recognition/update_profile.html', {'form': form})