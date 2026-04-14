import logging
from typing import Any

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class PlayerDetector:
    """Detecta personas con YOLO y retorna la más confiable."""

    def __init__(self, model_path: str | None = None, conf_threshold: float = 0.45):
        self.model_path = model_path or "yolov8n.pt"
        self.conf_threshold = conf_threshold
        self._model: Any = None

    @property
    def model(self):
        if self._model is None:
            try:
                from ultralytics import YOLO
            except ImportError as exc:
                raise RuntimeError(
                    "Ultralytics no esta instalado. Agrega 'ultralytics' a tus dependencias."
                ) from exc

            logger.info("Cargando modelo YOLO desde %s", self.model_path)
            self._model = YOLO(self.model_path)
        return self._model

    def detect(self, image: np.ndarray) -> dict:
        result = {
            "success": False,
            "crop": None,
            "bbox": None,
            "confidence": None,
            "all_detections": [],
            "error": None,
        }

        if image is None or image.size == 0:
            result["error"] = "Imagen vacia o invalida"
            return result

        try:
            results = self.model(image, conf=self.conf_threshold, classes=[0], verbose=False)
        except Exception as exc:
            result["error"] = f"Error en inferencia YOLO: {exc}"
            logger.error(result["error"])
            return result

        if not results or len(results[0].boxes) == 0:
            result["error"] = "No se detecto ningun jugador en la imagen"
            return result

        detections = []
        for box in results[0].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            detections.append(
                {
                    "bbox": [x1, y1, x2, y2],
                    "confidence": round(float(box.conf[0]), 4),
                }
            )
        result["all_detections"] = detections

        best = max(detections, key=lambda item: item["confidence"])
        x1, y1, x2, y2 = best["bbox"]
        height, width = image.shape[:2]
        pad = 10
        x1 = max(0, x1 - pad)
        y1 = max(0, y1 - pad)
        x2 = min(width, x2 + pad)
        y2 = min(height, y2 + pad)

        result["success"] = True
        result["bbox"] = [x1, y1, x2, y2]
        result["confidence"] = best["confidence"]
        result["crop"] = image[y1:y2, x1:x2]
        return result

    @staticmethod
    def draw_annotations(image: np.ndarray, detections: list[dict]) -> np.ndarray:
        annotated = image.copy()
        for detection in detections:
            x1, y1, x2, y2 = detection["bbox"]
            confidence = detection["confidence"]
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 200, 50), 2)
            cv2.putText(
                annotated,
                f"jugador {confidence:.2f}",
                (x1, max(y1 - 8, 0)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 200, 50),
                2,
            )
        return annotated
