from django.urls import path
from . import views

urlpatterns = [
    # Estado del servidor RAG (sin auth — para el widget de React)
    path("health/", views.health, name="rag-health"),
    # Consulta principal
    path("ask/", views.ask, name="rag-ask"),
    # Historial del usuario
    path("history/", views.history, name="rag-history"),
    path("history/<int:pk>/", views.history_detail, name="rag-history-detail"),
]
