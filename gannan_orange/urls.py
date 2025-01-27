from django.urls import path
from . import views

app_name = 'orange'
urlpatterns = [
    path('', views.HomePage.as_view(), name='home'),
    path('list', views.VarietyList.as_view(), name='list')
]