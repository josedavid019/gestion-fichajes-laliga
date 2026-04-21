import base64
import logging
from difflib import SequenceMatcher

import cv2
import numpy as np
import requests

logger = logging.getLogger(__name__)


class FaceIdentifier:
    AMBIGUOUS_PAIR = set()

    def __init__(
        self,
        roboflow_api_key: str | None = None,
        roboflow_project_id: str | None = None,
        roboflow_version: str | None = None,
        roboflow_base_url: str = "https://classify.roboflow.com",
        min_confidence: float = 0.6,
    ):
        self.roboflow_api_key = roboflow_api_key
        self.roboflow_project_id = roboflow_project_id
        self.roboflow_version = roboflow_version
        self.roboflow_base_url = roboflow_base_url.rstrip("/")
        self.min_confidence = min_confidence
        self._cascade = None

    @property
    def cascade(self):
        if self._cascade is None:
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            self._cascade = cv2.CascadeClassifier(cascade_path)
        return self._cascade

    @property
    def is_enabled(self) -> bool:
        return bool(
            self.roboflow_api_key and self.roboflow_project_id and self.roboflow_version
        )

    def detect_faces(self, image: np.ndarray) -> list[dict]:
        if image is None or image.size == 0:
            return []

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(40, 40),
        )
        results = []
        for (x, y, w, h) in faces:
            results.append(
                {
                    "bbox": [int(x), int(y), int(x + w), int(y + h)],
                    "crop": image[y : y + h, x : x + w],
                }
            )
        return results

    def identify(
        self,
        image: np.ndarray,
        player_name_hint: str | None = None,
    ) -> dict:
        result = {
            "success": False,
            "method": None,
            "faces_detected": 0,
            "face_boxes": [],
            "best_match": None,
            "predictions": [],
            "status": "no_face",
            "error": None,
        }

        faces = self.detect_faces(image)
        result["faces_detected"] = len(faces)
        result["face_boxes"] = [face["bbox"] for face in faces]

        if not faces:
            result["error"] = "No se detectaron rostros"
            return result

        if not self.is_enabled:
            result["method"] = "face_detection_only"
            result["status"] = "service_unconfigured"
            result["error"] = "Roboflow no configurado"
            return result

        all_predictions: list[dict] = []
        best_match = None
        for index, face in enumerate(faces):
            try:
                predictions = self._classify_face(face["crop"])
            except Exception as exc:
                logger.warning("Fallo clasificando rostro %s: %s", index, exc)
                continue

            for prediction in predictions:
                confidence = prediction["confidence"]
                if player_name_hint:
                    confidence = round(
                        self._boost_hint(
                            confidence,
                            player_name_hint,
                            prediction["label"],
                        ),
                        4,
                    )
                candidate = {
                    "label": prediction["label"],
                    "confidence": confidence,
                    "face_index": index,
                    "bbox": face["bbox"],
                }
                all_predictions.append(candidate)

                if confidence >= self.min_confidence and (
                    best_match is None or confidence > best_match["confidence"]
                ):
                    best_match = candidate

        result["predictions"] = sorted(
            all_predictions,
            key=lambda item: item["confidence"],
            reverse=True,
        )[:5]

        result["method"] = "roboflow_face_classification"
        top_predictions = result["predictions"][:2]
        ambiguous = self._is_ambiguous_pair(top_predictions)
        if best_match:
            if ambiguous:
                result["status"] = "low_confidence"
                result["best_match"] = {
                    **top_predictions[0],
                    "label": "low_confidence",
                }
                result["error"] = (
                    "Roboflow devolvio clases muy cercanas entre luiz-junior y victor-garcia"
                )
            else:
                result["success"] = True
                result["status"] = "identified"
                result["best_match"] = best_match
        else:
            result["status"] = "unknown"
            if top_predictions:
                result["best_match"] = {
                    **top_predictions[0],
                    "label": "unknown",
                }
            result["error"] = "Roboflow no devolvio una coincidencia fiable"
        return result

    def _classify_face(self, face_crop: np.ndarray) -> list[dict]:
        payload = self._encode_image(face_crop)
        url = (
            f"{self.roboflow_base_url}/"
            f"{self.roboflow_project_id}/{self.roboflow_version}"
        )
        response = requests.post(
            url,
            params={"api_key": self.roboflow_api_key},
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=15,
        )
        response.raise_for_status()
        return self._normalize_predictions(response.json())

    @staticmethod
    def _encode_image(image: np.ndarray) -> str:
        ok, buffer = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 90])
        if not ok:
            raise ValueError("No se pudo codificar el recorte facial")
        return base64.b64encode(buffer).decode("utf-8")

    @staticmethod
    def _normalize_predictions(payload: dict) -> list[dict]:
        if isinstance(payload.get("predictions"), list):
            return [
                {
                    "label": item.get("class"),
                    "confidence": round(float(item.get("confidence", 0.0)), 4),
                }
                for item in payload["predictions"]
                if item.get("class")
            ]

        if isinstance(payload.get("predictions"), dict):
            return [
                {
                    "label": label,
                    "confidence": round(
                        float((meta or {}).get("confidence", 0.0)),
                        4,
                    ),
                }
                for label, meta in payload["predictions"].items()
            ]

        top = payload.get("top")
        if top:
            return [
                {
                    "label": top,
                    "confidence": round(float(payload.get("confidence", 0.0)), 4),
                }
            ]

        return []

    @staticmethod
    def _boost_hint(confidence: float, hint: str, label: str) -> float:
        clean_hint = "".join(ch for ch in hint.lower() if ch.isalnum() or ch.isspace())
        clean_label = "".join(
            ch for ch in label.lower() if ch.isalnum() or ch.isspace()
        )
        if clean_hint == clean_label:
            return min(confidence + 0.2, 0.9999)
        similarity = SequenceMatcher(None, clean_hint, clean_label).ratio()
        return min(confidence + similarity * 0.1, 0.9999)

    @classmethod
    def _is_ambiguous_pair(cls, top_predictions: list[dict]) -> bool:
        if not cls.AMBIGUOUS_PAIR or len(top_predictions) < 2:
            return False
        labels = {item.get("label") for item in top_predictions[:2]}
        if labels != cls.AMBIGUOUS_PAIR:
            return False
        diff = abs(
            float(top_predictions[0].get("confidence", 0.0))
            - float(top_predictions[1].get("confidence", 0.0))
        )
        return diff <= 0.05
