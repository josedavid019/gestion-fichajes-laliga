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
            roboflow_api_key=getattr(settings, "ROBOFLOW_API_KEY", None),
            roboflow_project_id=getattr(settings, "ROBOFLOW_PROJECT_ID", None),
            roboflow_version=getattr(settings, "ROBOFLOW_MODEL_VERSION", None),
            roboflow_confidence=getattr(settings, "ROBOFLOW_CONFIDENCE", 0.6),
            video_sample_seconds=getattr(settings, "VISION_VIDEO_SAMPLE_SECONDS", 1.0),
            video_max_frames=getattr(settings, "VISION_VIDEO_MAX_FRAMES", 8),
            include_crops_in_response=getattr(settings, "VISION_INCLUDE_CROPS", False),
            enable_enrichment=getattr(settings, "VISION_ENABLE_ENRICHMENT", True),
        )
    return _pipeline


class AnalyzePlayerView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        media_file = (
            request.FILES.get("image")
            or request.FILES.get("video")
            or request.FILES.get("media")
            or request.FILES.get("file")
        )
        if not media_file:
            return Response(
                {
                    "error": (
                        "Se requiere un archivo en 'image', 'video', 'media' o 'file'"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        media_type = _resolve_media_type(media_file)
        max_size = 50 * 1024 * 1024 if media_type == "video" else 10 * 1024 * 1024
        if media_file.size > max_size:
            return Response(
                {
                    "error": (
                        "El video no puede superar los 50 MB"
                        if media_type == "video"
                        else "La imagen no puede superar los 10 MB"
                    )
                },
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )

        player_name_hint = request.data.get("name", "").strip() or None

        try:
            pipeline = get_pipeline()
            file_bytes = media_file.read()
            if media_type == "video":
                result = pipeline.run_video(
                    file_bytes,
                    player_name_hint=player_name_hint,
                )
            else:
                result = pipeline.run(
                    file_bytes,
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

        face_status = (
            result.get("vision_analysis", {})
            .get("face_recognition", {})
            .get("status")
        )
        if face_status == "service_unconfigured":
            return Response(
                {"error": "Roboflow no esta configurado en el backend"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

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
                "version": "1.1.0",
                "endpoints": {
                    "analyze_player": "/api/vision/analyze-player/ [POST image|video]",
                    "health": "/api/vision/health/ [GET]",
                },
            }
        )


def _resolve_media_type(uploaded_file) -> str:
    content_type = (getattr(uploaded_file, "content_type", "") or "").lower()
    name = (getattr(uploaded_file, "name", "") or "").lower()
    if content_type.startswith("video/") or name.endswith(
        (".mp4", ".mov", ".avi", ".mkv", ".webm")
    ):
        return "video"
    return "image"
