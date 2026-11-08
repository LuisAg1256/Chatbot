from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chat_api, name='api_chat'),
    path('dilemmas/', views.dilemmas_api, name='api_dilemmas'),
    path('corpus/', views.corpus_api, name='api_corpus'),
    path('feedback/', views.feedback_api, name='api_feedback'),
]
