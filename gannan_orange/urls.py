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
    path('detail/tech/<int:id>', views.PlantingTechDetail.as_view(), name='tech_detail'),
    path('detail/tech/<int:id>/edit', views.PlantingTechEdit.as_view(), name='tech_edit'),
    path('detail/tech/<int:id>/delete', views.PlantingTechDelete.as_view(), name='tech_delete'),
    path('create/tech', views.PlantingTechCreate.as_view(), name='tech_create'),
    path('detail/soil/<int:id>', views.SoilTypeDetail.as_view(), name='soil_detail'),
    path('detail/soil/<int:id>/edit', views.SoilTypeEdit.as_view(), name='soil_edit'),


]