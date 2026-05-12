from django.urls import path
from . import views

urlpatterns = [
    path("ask/", views.ask, name="rag-ask"),
    path("history/", views.history, name="rag-history"),
    path("history/<int:pk>/", views.history_detail, name="rag-history-detail"),
]
