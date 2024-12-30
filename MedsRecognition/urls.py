from django.contrib.auth.views import LogoutView
from django.urls import path

from MedsRecognition import views

urlpatterns = [
    #path('', lambda request: redirect('upload_image', permanent=False)),
    path('upload/', views.upload_image, name='upload'),
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('signup/', views.supabase_signup_view, name='signup'),
    path('accounts/login/', views.supabase_login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]