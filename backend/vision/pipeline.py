import logging

import cv2
import numpy as np

from .api_enricher import PlayerEnricher
from .face_identifier import FaceIdentifier
from .ocr_extractor import OCRExtractor
from .player_detector import PlayerDetector
from .response_builder import consolidate
from .video_analyzer import VideoAnalyzer

logger = logging.getLogger(__name__)

PLAYER_SEARCH_MAP = {
    "lamine-yamal": {"name": "Lamine Yamal", "team": "Barcelona"},
    "luiz-junior": {"name": "luiz junior", "team": "Villarreal"},
    "marc-bernal": {"name": "Marc Bernal", "team": "Barcelona"},
    "valentin-rosier": {"name": "Valentin Rosier", "team": "Leganes"},
    "victor-garcia": {"name": "Victor Garcia", "team": None},
    "vinicius-junior": {"name": "Vinicius Junior", "team": "Real Madrid"},
    "jude-bellingham": {"name": "Jude Bellingham", "team": "Real Madrid"},
}


class VisionPipeline:
    def __init__(
        self,
        football_api_key: str | None = None,
        thesportsdb_api_key: str | None = None,
        yolo_model_path: str | None = None,
        yolo_confidence: float = 0.45,
        tesseract_cmd: str | None = None,
        roboflow_api_key: str | None = None,
        roboflow_project_id: str | None = None,
        roboflow_version: str | None = None,
        roboflow_confidence: float = 0.6,
        video_sample_seconds: float = 1.0,
        video_max_frames: int = 8,
        include_crops_in_response: bool = False,
        enable_enrichment: bool = True,
    ):
        self.detector = PlayerDetector(
            model_path=yolo_model_path,
            conf_threshold=yolo_confidence,
        )
        self.ocr = OCRExtractor(tesseract_cmd=tesseract_cmd)
        self.face_identifier = FaceIdentifier(
            roboflow_api_key=roboflow_api_key,
            roboflow_project_id=roboflow_project_id,
            roboflow_version=roboflow_version,
            min_confidence=roboflow_confidence,
        )
        self.enricher = (
            PlayerEnricher(
                football_api_key=football_api_key,
                thesportsdb_api_key=thesportsdb_api_key,
            )
            if enable_enrichment
            else None
        )
        self.include_crops = include_crops_in_response
        self.enable_enrichment = enable_enrichment
        self.video_analyzer = VideoAnalyzer(
            pipeline=self,
            sample_seconds=video_sample_seconds,
            max_frames=video_max_frames,
        )

    @staticmethod
    def bytes_to_image(raw: bytes) -> np.ndarray | None:
        try:
            buffer = np.frombuffer(raw, dtype=np.uint8)
            return cv2.imdecode(buffer, cv2.IMREAD_COLOR)
        except Exception as exc:
            logger.error("No se pudo decodificar la imagen: %s", exc)
            return None

    def run(self, image_bytes: bytes, player_name_hint: str | None = None) -> dict:
        image = self.bytes_to_image(image_bytes)
        if image is None:
            return _error_response("No se pudo decodificar la imagen proporcionada")

        return self.run_image_array(image, player_name_hint=player_name_hint)

    def run_video(self, video_bytes: bytes, player_name_hint: str | None = None) -> dict:
        return self.video_analyzer.analyze(
            video_bytes,
            player_name_hint=player_name_hint,
        )

    def run_image_array(
        self,
        image: np.ndarray,
        player_name_hint: str | None = None,
        media_type: str = "image",
    ) -> dict:
        if image is None or image.size == 0:
            return _error_response("No se pudo decodificar la imagen proporcionada")

        h, w = image.shape[:2]
        logger.info("Iniciando analisis de imagen: %dx%d pixeles", w, h)

        detection = self.detector.detect(image)
        face_image = detection.get("crop") if detection.get("success") else image
        face_result = self.face_identifier.identify(
            face_image,
            player_name_hint=player_name_hint,
        )

        try:
            ocr_result = self.ocr.extract(image)
        except Exception as exc:
            logger.warning("OCR no disponible: %s", exc)
            from .ocr_extractor import OCRResult

            ocr_result = OCRResult(
                raw_text="",
                player_name=None,
                team_name=None,
                jersey_number=None,
            )

        face_name = (face_result.get("best_match") or {}).get("label")
        mapped_player = _map_face_label(face_name)
        if mapped_player and face_result.get("best_match"):
            face_result["best_match"] = {
                **face_result["best_match"],
                "raw_label": face_name,
                "label": mapped_player["name"],
            }
        if face_result.get("predictions"):
            face_result["predictions"] = [
                {
                    **prediction,
                    "raw_label": prediction.get("label"),
                    "label": (_map_face_label(prediction.get("label")) or {}).get(
                        "name",
                        prediction.get("label"),
                    ),
                }
                for prediction in face_result["predictions"]
            ]

        search_name = (
            player_name_hint
            or (mapped_player or {}).get("name")
            or ocr_result.player_name
        )
        team_name = (
            (mapped_player or {}).get("team")
            or ocr_result.team_name
        )
        enrichment = {}
        if self.enable_enrichment and self.enricher and search_name:
            enrichment = self.enricher.enrich(search_name, team_name)
        elif self.enable_enrichment:
            enrichment = {
                "enrichment_errors": ["Nombre de jugador no disponible para busqueda"],
            }

        return consolidate(
            detection=detection,
            face=face_result,
            ocr=ocr_result,
            enrichment=enrichment,
            original_image=image,
            media_type=media_type,
            identity_source=_resolve_identity_source(
                player_name_hint=player_name_hint,
                face_name=face_name,
                ocr_name=ocr_result.player_name,
            ),
            include_crops=self.include_crops,
        )


def _error_response(message: str) -> dict:
    return {
        "meta": {"error": True, "message": message},
        "player_profile": None,
        "statistics": None,
        "market_value": None,
        "league_info": None,
        "vision_analysis": None,
    }


def _resolve_identity_source(
    player_name_hint: str | None,
    face_name: str | None,
    ocr_name: str | None,
) -> str | None:
    if player_name_hint:
        return "request_hint"
    if face_name:
        return "face_recognition"
    if ocr_name:
        return "ocr"
    return None


def _map_face_label(label: str | None) -> dict | None:
    if not label:
        return None
    normalized = label.lower().strip().replace("_", "-").replace(" ", "-")
    return PLAYER_SEARCH_MAP.get(normalized)
