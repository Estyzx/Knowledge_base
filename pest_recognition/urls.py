from django.urls import path
from . import views

app_name = 'pest_recognition'

urlpatterns = [
    path('', views.recognition_view, name='upload'),
    path('history/', views.HistoryListView.as_view(), name='history'),
    path('history/<int:pk>/', views.HistoryDetailView.as_view(), name='result_detail'),
    path('api/recognize/', views.api_recognize, name='api_recognize'),
]
