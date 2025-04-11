from django.urls import path
from . import views

app_name = 'article'

urlpatterns = [
    path('', views.PlantingTechListView.as_view(), name='list'),
    path('<int:pk>/', views.PlantingTechDetailView.as_view(), name='detail'),
    path('create/', views.PlantingTechCreateView.as_view(), name='create'),
    path('edit/<int:pk>/', views.PlantingTechEditView.as_view(), name='edit'),
    path('delete/<int:pk>/', views.PlantingTechDeleteView.as_view(), name='delete'),
    path('favorite/<int:pk>/', views.favorite_article, name='favorite'),
    path('comment/delete/<int:pk>/', views.comment_delete, name='comment_delete'),
]