from django.shortcuts import redirect
from django.urls import path
from MedsRecognition import views

urlpatterns = [
    path('', lambda request: redirect('upload_image', permanent=False)),
    path('upload/', views.upload_image, name='upload_image'),
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('signup/', views.supabase_signup_view, name='signup'),
    path('login/', views.supabase_login_view, name='login'),
]