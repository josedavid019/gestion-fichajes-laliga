import base64
import uuid
from datetime import datetime, timezone

import cv2
import numpy as np

from .ocr_extractor import OCRResult


def _translate_position(position: str | None) -> str | None:
    """Traduce posiciones del inglés al español"""
    if not position:
        return None

    position_map = {
        # Portero
        "Goalkeeper": "Portero",
        "GK": "Portero",
        # Defensas
        "Defender": "Defensa",
        "Centre-back": "Defensa Central",
        "Left-back": "Lateral Izquierdo",
        "Right-back": "Lateral Derecho",
        "Fullback": "Lateral",
        "DF": "Defensa",
        # Centrocampistas
        "Midfielder": "Centrocampista",
        "Central Midfielder": "Centrocampista Central",
        "Attacking Midfielder": "Centrocampista Atacante",
        "Defensive Midfielder": "Centrocampista Defensivo",
        "Left Midfielder": "Centrocampista Izquierdo",
        "Right Midfielder": "Centrocampista Derecho",
        "MF": "Centrocampista",
        # Delanteros
        "Forward": "Delantero",
        "Striker": "Delantero",
        "Attacker": "Delantero",
        "Left Winger": "Extremo Izquierdo",
        "Right Winger": "Extremo Derecho",
        "Center Forward": "Delantero Centro",
        "CF": "Delantero Centro",
        "ST": "Delantero",
        "FW": "Delantero",
    }

    return position_map.get(position, position)


def _image_to_base64(img: np.ndarray) -> str | None:
    if img is None or img.size == 0:
        return None
    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 85])
    if not ok:
        return None
    return base64.b64encode(buf).decode("utf-8")


def consolidate(
    detection: dict,
    ocr: OCRResult,
    enrichment: dict,
    original_image: np.ndarray,
    include_crops: bool = False,
) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    request_id = str(uuid.uuid4())[:12]
    api_football = enrichment.get("api_football") or {}
    the_sports_db = enrichment.get("the_sports_db") or {}
    external_profile = api_football or the_sports_db
    api_stats = external_profile.get("statistics") or {}
    data_sources = enrichment.get("sources_used") or []

    vision_section = {
        "yolo": {
            "player_detected": detection["success"],
            "confidence": detection.get("confidence"),
            "bounding_box": detection.get("bbox"),
            "total_persons_detected": len(detection.get("all_detections", [])),
            "error": detection.get("error"),
        },
        "ocr": {
            "jersey_number": ocr.jersey_number,
            "player_name_raw": ocr.player_name,
            "team_name_raw": ocr.team_name,
            "extra_tokens": ocr.extra_tokens,
            "raw_text_preview": ocr.raw_text[:200] if ocr.raw_text else None,
        },
    }

    if include_crops:
        vision_section["crops"] = {
            "original_b64": _image_to_base64(original_image),
            "player_crop_b64": _image_to_base64(detection.get("crop")),
            "jersey_zone_b64": _image_to_base64(ocr.jersey_zone),
        }

    return {
        "meta": {
            "request_id": request_id,
            "processed_at": now,
            "module_version": "1.0.0",
            "pipeline": ["yolo_detection", "ocr_extraction"]
            + (["api_enrichment"] if external_profile else []),
            "data_sources": data_sources,
            "enrichment_source": enrichment.get("source"),
            "enrichment_errors": enrichment.get("enrichment_errors", []),
        },
        "player_profile": {
            "identified_name": external_profile.get("full_name")
            or ocr.player_name
            or "Desconocido",
            "first_name": external_profile.get("first_name"),
            "last_name": external_profile.get("last_name"),
            "age": external_profile.get("age"),
            "nationality": external_profile.get("nationality"),
            "birth_date": external_profile.get("birth_date"),
            "height": external_profile.get("height"),
            "height_cm": external_profile.get("height_cm"),
            "weight": external_profile.get("weight"),
            "weight_kg": external_profile.get("weight_kg"),
            "position": _translate_position(external_profile.get("position")),
            "status": external_profile.get("status"),
            "jersey_number": external_profile.get("jersey_number"),
            "current_club": external_profile.get("team", {}).get("name")
            or ocr.team_name,
            "club_logo_url": external_profile.get("team", {}).get("logo"),
            "photo_url": external_profile.get("photo_url"),
        },
        "statistics": {
            "season": f"{datetime.now().year - 1}/{str(datetime.now().year)[-2:]}",
            "appearances": api_stats.get("appearances"),
            "minutes_played": api_stats.get("minutes_played"),
            "goals": api_stats.get("goals"),
            "assists": api_stats.get("assists"),
            "key_passes": api_stats.get("key_passes"),
            "pass_accuracy": api_stats.get("accuracy_passes"),
            "rating": api_stats.get("rating"),
        },
        "market_value": {
            "current_value_eur": None,
            "currency": "EUR",
            "last_updated": None,
            "value_history": [],
        },
        "league_info": {
            "league": "LaLiga",
            "team_id_openliga": None,
            "team_short_name": None,
            "team_icon_url": None,
            "team_standing": None,
            "laliga_top_5": [],
        },
        "vision_analysis": vision_section,
        "raw_api_responses": {
            "api_football": api_football or None,
            "the_sports_db": the_sports_db or None,
        },
    }
