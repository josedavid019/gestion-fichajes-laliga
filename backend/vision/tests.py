import io
from unittest.mock import MagicMock, patch

import cv2
import numpy as np
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


def _make_dummy_image(width=200, height=300, with_text=True) -> bytes:
    img = np.ones((height, width, 3), dtype=np.uint8) * 50
    cv2.rectangle(img, (50, 80), (150, 220), (200, 60, 30), -1)
    if with_text:
        cv2.putText(img, "10", (80, 160), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        cv2.putText(
            img,
            "MESSI",
            (45, 200),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )
    ok, buf = cv2.imencode(".jpg", img)
    assert ok
    return buf.tobytes()


class OCRExtractorTests(TestCase):
    @patch("vision.ocr_extractor.OCRExtractor.run_ocr", return_value="10\nMESSI\nBARCELONA")
    def test_extract_returns_result_object(self, _mock_run_ocr):
        from vision.ocr_extractor import OCRExtractor

        extractor = OCRExtractor()
        dummy_img = np.ones((300, 200, 3), dtype=np.uint8) * 200
        result = extractor.extract(dummy_img)

        self.assertEqual(result.jersey_number, "10")
        self.assertEqual(result.player_name, "MESSI")
        self.assertEqual(result.team_name, "BARCELONA")
        self.assertIsInstance(result.extra_tokens, list)

    def test_extract_empty_image(self):
        from vision.ocr_extractor import OCRExtractor

        extractor = OCRExtractor()
        result = extractor.extract(np.array([]))

        self.assertIsNone(result.jersey_number)
        self.assertIsNone(result.player_name)


class PlayerDetectorTests(TestCase):
    def test_detect_no_persons(self):
        from vision.player_detector import PlayerDetector

        mock_model = MagicMock()
        mock_result = MagicMock()
        mock_result.boxes = []
        mock_model.return_value = [mock_result]

        detector = PlayerDetector.__new__(PlayerDetector)
        detector._model = mock_model
        detector.conf_threshold = 0.45

        dummy = np.ones((300, 200, 3), dtype=np.uint8)
        result = detector.detect(dummy)
        self.assertFalse(result["success"])

    def test_detect_empty_image(self):
        from vision.player_detector import PlayerDetector

        detector = PlayerDetector.__new__(PlayerDetector)
        detector._model = None
        detector.conf_threshold = 0.45

        result = detector.detect(np.array([]))
        self.assertFalse(result["success"])
        self.assertIsNotNone(result["error"])


class ResponseBuilderTests(TestCase):
    def test_consolidate_structure(self):
        from vision.ocr_extractor import OCRResult
        from vision.response_builder import consolidate

        detection = {
            "success": False,
            "crop": None,
            "bbox": None,
            "confidence": None,
            "all_detections": [],
            "error": "No player",
        }
        ocr = OCRResult(raw_text="", jersey_number="10", player_name="MESSI")
        enrichment = {
            "api_football": None,
            "transfermarkt": None,
            "openligadb_team": None,
            "laliga_standings": None,
            "enrichment_errors": [],
        }
        dummy_img = np.ones((300, 200, 3), dtype=np.uint8)

        result = consolidate(detection, ocr, enrichment, dummy_img)

        self.assertIn("meta", result)
        self.assertIn("player_profile", result)
        self.assertIn("statistics", result)
        self.assertIn("market_value", result)
        self.assertIn("league_info", result)
        self.assertIn("vision_analysis", result)
        self.assertEqual(result["meta"]["data_sources"], [])
        self.assertEqual(result["raw_api_responses"]["api_football"], None)


@override_settings(ROOT_URLCONF="config.urls")
class AnalyzePlayerEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("analyze_player")

    def test_no_image_returns_400(self):
        response = self.client.post(self.url, {}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_image_too_large_returns_413(self):
        big_data = b"x" * (11 * 1024 * 1024)
        big_file = io.BytesIO(big_data)
        big_file.name = "big.jpg"
        response = self.client.post(self.url, {"image": big_file}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

    @patch("vision.views.get_pipeline")
    def test_valid_image_returns_json(self, mock_get_pipeline):
        mock_pipeline = MagicMock()
        mock_pipeline.run.return_value = {
            "meta": {"request_id": "test123", "error": False},
            "player_profile": {"identified_name": "Lionel Messi", "jersey_number": "10"},
            "statistics": {"goals": 20},
            "market_value": {"current_value_eur": "80000000"},
            "league_info": {"league": "LaLiga"},
            "vision_analysis": {
                "yolo": {"player_detected": True, "confidence": 0.91, "bounding_box": None, "total_persons_detected": 1, "error": None},
                "ocr": {"player_name_raw": None},
            },
        }
        mock_get_pipeline.return_value = mock_pipeline

        img_file = io.BytesIO(_make_dummy_image())
        img_file.name = "player.jpg"
        response = self.client.post(self.url, {"image": img_file}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["player_profile"]["identified_name"], "Lionel Messi")

    def test_health_endpoint(self):
        response = self.client.get(reverse("vision_health"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["status"], "ok")
