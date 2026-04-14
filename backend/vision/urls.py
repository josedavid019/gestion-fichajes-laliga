from django.urls import path

from .views import AnalyzePlayerView, HealthCheckView

urlpatterns = [
    path("analyze-player/", AnalyzePlayerView.as_view(), name="analyze_player"),
    path("health/", HealthCheckView.as_view(), name="vision_health"),
]
