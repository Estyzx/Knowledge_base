from django.urls import path
from . import views

app_name = 'orange'
urlpatterns = [
    path('', views.HomePage.as_view(), name='home'),
    path('list', views.VarietyList.as_view(), name='list'),
    path('detail/<int:id>', views.VarietyDetail.as_view(), name='detail'),
    path('detail/<int:id>/edit', views.VarietyEdit.as_view(), name='edit'),
    path('create', views.VarietyCreate.as_view(), name='creat'),
    # path('detail/<int:id>/delete', views.VarietyDelete.as_view(), name='delete'),

    path('list/tech', views.PlantingTechList.as_view(), name='tech_list'),
    path('detail/tech/<int:id>', views.PlantingTechDetail.as_view(), name='tech_detail')

]