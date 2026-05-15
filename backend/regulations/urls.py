from django.urls import path
from . import views

urlpatterns = [
    path("ask/", views.ask, name="rag-ask"),
    path("health/", views.health, name="rag-health"),
    path("history/", views.history, name="rag-history"),
    path("history/<int:pk>/", views.history_detail, name="rag-history-detail"),
    path("history/clear/", views.clear_history, name="rag-history-clear"),
]
