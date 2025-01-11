from django.urls import path

from MedsRecognition import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_image, name='upload'),
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('signup/', views.supabase_signup_view, name='signup'),
    path('login/', views.supabase_login_view, name='login'),
    path('logout/', views.supabase_logout_view, name='logout'),
    path('update_profile/', views.update_profile, name='update_profile'),
]