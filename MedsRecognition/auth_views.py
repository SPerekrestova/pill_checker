import logging

from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import render, redirect

from MedsRecognition.auth_service import sign_up_user, sign_in_user
from MedsRecognition.decorators import supabase_login_required
from MedsRecognition.forms import ProfileUpdateForm
from MedsRecognition.models import Profile

logger = logging.getLogger(__name__)


def supabase_signup_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        request.POST.get("username", email)

        try:
            result = sign_up_user(email, password)
            if result and hasattr(result, "user"):
                request.session["supabase_user"] = result.user.id
                request.user = result.user

                Profile.objects.create(user_id=result.user.id, defaults={"display_name": email})
                messages.success(request, "Signed up successfully. Please log in.")
                return render(request, "recognition/login.html")
            else:
                messages.error(request, "Sign-up failed. Check your email/password.")
        except Exception as e:
            messages.error(request, f"Sign-up error: {e}")

    return render(request, "recognition/signup.html")


def supabase_login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            result = sign_in_user(email, password)
            if result and hasattr(result, "user"):
                request.session["supabase_user"] = result.user.id
                request.user = result.user

                # Ensure the profile exists
                Profile.objects.get_or_create(
                    user_id=result.user.id, defaults={"display_name": email}
                )

                messages.success(request, "Successfully logged in!")
                return redirect("dashboard")
            else:
                messages.error(request, "Invalid credentials or login failed.")
        except Profile.DoesNotExist:
            messages.error(request, "Profile does not exist.")
            logger.error("Profile does not exist for user: %s", email)
        except Exception as e:
            messages.error(request, f"Supabase login error: {e}")
            logger.exception("Supabase login error for user: %s", email)
    return render(request, "recognition/login.html")


def supabase_logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")  # Redirect to the login page after logging out
    return render(request, "recognition/logout.html")


@supabase_login_required
def update_profile(request):
    profile = request.auth_user
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("dashboard")
    else:
        form = ProfileUpdateForm(instance=profile)
    return render(request, "recognition/update_profile.html", {"form": form})
