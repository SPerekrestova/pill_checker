from django.urls import path

from MedsRecognition import views

urlpatterns = [
    path('upload/', views.upload_image, name='upload'),
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('signup/', views.supabase_signup_view, name='signup'),
    path('accounts/login/', views.supabase_login_view, name='login'),
]