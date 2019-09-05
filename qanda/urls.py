from django.urls import path
from . import views

app_name = 'qanda'

urlpatterns = [
    path('ask', views.AskQuestionView.as_view(), name='AskQuestionView'),
]
