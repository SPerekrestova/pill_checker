from django.urls import path

from MedsRecognition import medication_views
from MedsRecognition import auth_views

urlpatterns = [
    path("", medication_views.index, name="index"),
    path("signup/", auth_views.supabase_signup_view, name="signup"),
    path("login/", auth_views.supabase_login_view, name="login"),
    path("logout/", auth_views.supabase_logout_view, name="logout"),
    path("upload/", medication_views.upload_image, name="upload"),
    path("dashboard/", medication_views.user_dashboard, name="dashboard"),
    path("update_profile/", auth_views.update_profile, name="update_profile"),
]
