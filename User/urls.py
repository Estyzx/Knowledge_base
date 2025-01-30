from django.contrib.auth import views as auth_views
from django.urls import path
from .views import CustomLoginView,CustomRegisterView
app_name = 'user'


urlpatterns = [
    path('login',CustomLoginView.as_view(), name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('register',CustomRegisterView.as_view(), name='register'),
]