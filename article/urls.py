from django.urls import path
from .views import *

app_name = 'article'
urlpatterns = [
    path('create/',PlantingTechCreateView.as_view(), name='create'),
    path('<int:pk>/', PlantingTechDetailView.as_view(), name='detail'),
    path('list', PlantingTechListView.as_view(), name='list'),
]