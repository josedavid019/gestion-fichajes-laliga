import logging

import cv2
import numpy as np

from .api_enricher import PlayerEnricher
from .ocr_extractor import OCRExtractor
from .player_detector import PlayerDetector
from .response_builder import consolidate

logger = logging.getLogger(__name__)


class VisionPipeline:
    def __init__(
        self,
        football_api_key: str | None = None,
        thesportsdb_api_key: str | None = None,
        yolo_model_path: str | None = None,
        yolo_confidence: float = 0.45,
        tesseract_cmd: str | None = None,
        include_crops_in_response: bool = False,
        enable_enrichment: bool = True,
    ):
        self.detector = PlayerDetector(
            model_path=yolo_model_path,
            conf_threshold=yolo_confidence,
        )
        self.ocr = OCRExtractor(tesseract_cmd=tesseract_cmd)
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

        # 1. Verificación de tamaño inicial
        h, w = image.shape[:2]
        logger.info("Iniciando análisis de imagen: %dx%d píxeles", w, h)

        # 2. Detección visual (YOLO)
        detection = self.detector.detect(image)

        # 3. Extracción de texto (OCR) — opcional
        try:
            ocr_result = self.ocr.extract(image)
        except Exception as exc:
            logger.warning(
                "OCR no disponible (Control de Aplicaciones bloqueó pandas): %s", exc
            )
            # Usar objeto dummy si hay error
            from .ocr_extractor import OCRResult

            ocr_result = OCRResult(
                raw_text="", player_name=None, team_name=None, jersey_number=None
            )

        search_name = player_name_hint or ocr_result.player_name
        team_name = ocr_result.team_name
        enrichment = {}
        if self.enable_enrichment and self.enricher and search_name:
            enrichment = self.enricher.enrich(search_name, team_name)
        elif self.enable_enrichment:
            enrichment = {
                "enrichment_errors": ["Nombre de jugador no disponible para busqueda"],
            }

        return consolidate(
            detection=detection,
            ocr=ocr_result,
            enrichment=enrichment,
            original_image=image,
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
