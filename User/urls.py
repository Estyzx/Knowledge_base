from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.CustomRegisterView.as_view(), name='register'),
    path('profile/<int:pk>/', views.user_detail, name='user_detail'),
    path('profile/edit/', views.UserProfileEditView.as_view(), name='edit_profile'),
]