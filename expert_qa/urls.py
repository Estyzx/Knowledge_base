from django.urls import path
from . import views

app_name = 'expert_qa'

urlpatterns = [
    path('questions/', views.question_list, name='question_list'),
    path('question/<int:pk>/', views.question_detail, name='question_detail'),
    path('ask/', views.ask_question, name='ask_question'),
    path('ask/<int:expert_id>/', views.ask_question, name='ask_expert'),
    path('answer/<int:question_id>/', views.post_answer, name='post_answer'),
    path('accept/<int:answer_id>/', views.accept_answer, name='accept_answer'),
    path('experts/', views.expert_list, name='expert_list'),
    path('expert/<int:expert_id>/', views.expert_detail, name='expert_detail'),
    path('verify/<int:expert_id>/', views.verify_expert, name='verify_expert'),
    path('follow-up/<int:pk>/', views.follow_up_question, name='follow_up_question'),
    path('vote/question/<int:pk>/', views.vote_question, name='vote_question'),
    path('vote/answer/<int:answer_id>/', views.vote_answer, name='vote_answer'),
]