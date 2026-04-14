import logging

from django.conf import settings
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .pipeline import VisionPipeline

logger = logging.getLogger(__name__)

_pipeline: VisionPipeline | None = None


def get_pipeline() -> VisionPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = VisionPipeline(
            football_api_key=getattr(settings, "APISPORTS_FOOTBALL_KEY", None)
            or getattr(settings, "RAPIDAPI_FOOTBALL_KEY", None),
            thesportsdb_api_key=getattr(settings, "THESPORTSDB_API_KEY", None),
            yolo_model_path=getattr(settings, "YOLO_MODEL_PATH", None),
            yolo_confidence=getattr(settings, "YOLO_CONFIDENCE", 0.45),
            tesseract_cmd=getattr(settings, "TESSERACT_CMD", None),
            include_crops_in_response=getattr(settings, "VISION_INCLUDE_CROPS", False),
            enable_enrichment=getattr(settings, "VISION_ENABLE_ENRICHMENT", True),
        )
    return _pipeline


class AnalyzePlayerView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        image_file = request.FILES.get("image")
        if not image_file:
            return Response(
                {"error": "Se requiere el campo 'image' con la imagen del jugador"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        max_size = 10 * 1024 * 1024
        if image_file.size > max_size:
            return Response(
                {"error": "La imagen no puede superar los 10 MB"},
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )

        player_name_hint = request.data.get("name", "").strip() or None

        try:
            result = get_pipeline().run(
                image_file.read(),
                player_name_hint=player_name_hint,
            )
        except Exception as exc:
            logger.exception("Error en pipeline de vision: %s", exc)
            return Response(
                {"error": f"Error interno del modulo de vision: {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if result.get("meta", {}).get("error"):
            return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        yolo_ok = (
            result.get("vision_analysis", {})
            .get("yolo", {})
            .get("player_detected", False)
        )
        return Response(
            result,
            status=status.HTTP_200_OK if yolo_ok else status.HTTP_206_PARTIAL_CONTENT,
        )


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                "status": "ok",
                "module": "vision",
                "version": "1.0.0",
                "endpoints": {
                    "analyze_player": "/api/vision/analyze-player/ [POST]",
                    "health": "/api/vision/health/ [GET]",
                },
            }
        )
