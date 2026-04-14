import logging
import re
from dataclasses import dataclass, field

import cv2
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class OCRResult:
    raw_text: str = ""
    jersey_number: str | None = None
    player_name: str | None = None
    team_name: str | None = None
    extra_tokens: list[str] = field(default_factory=list)
    jersey_zone: np.ndarray | None = None


class OCRExtractor:
    # Palabras que suelen molestar la lectura
    IGNORED = {
        "ESP", "POS", "AGE", "MD", "GK", "DF", "MF", "FW", "SORARE", "STELLAR",
        "NIGHTS", "LALIGA", "IARC", "JURGT", "LINC", "LINCE", "PSSOL", "TMIRAFES",
    }
    TEAM_HINTS = {
        "MADRID", "BARCELONA", "ATLETICO", "SEVILLA", "VALENCIA", "BETIS",
        "VILLARREAL", "SOCIEDAD", "BILBAO", "OSASUNA", "GIRONA", "GETAFE",
        "CELTA", "ALAVES", "LEGANES", "ESPANYOL", "RAYO", "MALLORCA", "LAS",
        "PALMAS",
    }

    def __init__(self, tesseract_cmd: str | None = None):
        self._pytesseract = None
        if tesseract_cmd:
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    @property
    def pytesseract(self):
        if self._pytesseract is None:
            import pytesseract
            self._pytesseract = pytesseract
        return self._pytesseract

    def run_ocr(self, image: np.ndarray, config: str = "--psm 6") -> str:
        return self.pytesseract.image_to_string(image, config=config)

    def _clean_text(self, text: str) -> str:
        return re.sub(r"[^A-Z\s]", " ", text.upper())

    def _clean_words(self, text: str) -> list[str]:
        return [
            word
            for word in self._clean_text(text).split()
            if len(word) >= 2 and word not in self.IGNORED
        ]

    def _extract_name(self, text: str) -> str | None:
        words = self._clean_words(text)
        if not words:
            return None
        return " ".join(words[:3])

    def _extract_team(self, text: str) -> str | None:
        for line in self._clean_text(text).splitlines():
            words = [word for word in line.split() if word and word not in self.IGNORED]
            if not words:
                continue
            if any(word in self.TEAM_HINTS for word in words):
                return " ".join(words[:3])
        return None

    def extract(self, image: np.ndarray) -> OCRResult:
        result = OCRResult()
        if image is None or image.size == 0:
            return result

        h, w = image.shape[:2]
        footer = image[int(h * 0.6):, :]

        # Procesado dual
        gray = cv2.cvtColor(footer, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        # Modo 1: Normal
        thr1 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10)
        txt1 = self.run_ocr(thr1, config="--psm 6")

        # Modo 2: Invertido
        _, thr2 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        txt2 = self.run_ocr(thr2, config="--psm 6")

        combined = f"{txt1}\n{txt2}"
        result.raw_text = combined
        result.player_name = self._extract_name(combined)
        result.team_name = self._extract_team(combined)

        # Dorsal
        nums = re.findall(r"\b\d{1,2}\b", combined)
        if nums:
            result.jersey_number = nums[0]

        # Tokens extra para el frontend
        result.extra_tokens = [w for w in combined.upper().split() if len(w) > 3][:10]
        # Guardamos zona para el response_builder
        result.jersey_zone = footer

        return result
