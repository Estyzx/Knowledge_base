from django.urls import path
from . import views, api_views

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
    path('list/soil', views.SoilTypeList.as_view(), name='soil_list'),
    path('detail/soil/<int:id>/delete', views.SoilTypeDelete.as_view(), name='soil_delete'),
    path('detail/pest/<int:id>', views.PestDetail.as_view(), name='pest_detail'),
    path('detail/pest/<int:id>/edit', views.PestEdit.as_view(), name='pest_edit'),
    path('detail/pest/<int:id>/delete', views.PestDelete.as_view(), name='pest_delete'),
    path('list/pest', views.PestList.as_view(), name='pest_list'),
    path('favorite', views.FavoriteVariety.as_view(), name='favorite'),
    
    # 专家审核功能路由
    path('review/pending', views.PendingReviewListView.as_view(), name='pending_review'),
    path('review/history', views.ReviewHistoryListView.as_view(), name='review_history'),
    path('review/variety/<int:id>', views.VarietyReviewView.as_view(), name='review_variety'),
    path('review/tech/<int:id>', views.PlantingTechReviewView.as_view(), name='review_tech'),
    path('review/pest/<int:id>', views.PestReviewView.as_view(), name='review_pest'),
    path('review/soil/<int:id>', views.SoilTypeReviewView.as_view(), name='review_soil'),
    
    # 审核相关API端点
    path('api/review-history/<str:content_type>/<int:content_id>/', api_views.review_history_api, name='review_history_api'),
    path('api/review/<str:content_type>/<int:content_id>/', api_views.quick_review_api, name='quick_review_api'),
    
    # 添加天气API端点
    path('api/weather/', api_views.weather_api, name='weather_api'),
]