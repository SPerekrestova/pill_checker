from django.shortcuts import redirect
from django.urls import path
from django.contrib.auth.views import LogoutView
from MedsRecognition import views

urlpatterns = [
    path('', lambda request: redirect('upload_image', permanent=False)),
    path('upload/', views.upload_image, name='upload_image'),
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('signup/', views.supabase_signup_view, name='signup'),
    path('login/', views.supabase_login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]