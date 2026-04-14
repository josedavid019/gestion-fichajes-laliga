import logging
import os
import re
import subprocess
import tempfile
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
        "ESP",
        "POS",
        "AGE",
        "MD",
        "GK",
        "DF",
        "MF",
        "FW",
        "SORARE",
        "STELLAR",
        "NIGHTS",
        "LALIGA",
        "IARC",
        "JURGT",
        "LINC",
        "LINCE",
        "PSSOL",
        "TMIRAFES",
    }
    TEAM_HINTS = {
        "MADRID",
        "BARCELONA",
        "ATLETICO",
        "SEVILLA",
        "VALENCIA",
        "BETIS",
        "VILLARREAL",
        "SOCIEDAD",
        "BILBAO",
        "OSASUNA",
        "GIRONA",
        "GETAFE",
        "CELTA",
        "ALAVES",
        "LEGANES",
        "ESPANYOL",
        "RAYO",
        "MALLORCA",
        "LAS",
        "PALMAS",
    }

    def __init__(self, tesseract_cmd: str | None = None):
        self._tesseract_cmd = tesseract_cmd or "tesseract"

    def run_ocr(self, image: np.ndarray, config: str = "--psm 6") -> str:
        """Llama a tesseract.exe directamente sin pytesseract"""
        try:
            # Guardar imagen en archivo temporal
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_img:
                cv2.imwrite(tmp_img.name, image)
                img_path = tmp_img.name

            # Crear ruta para output (sin extensión)
            with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_out:
                output_path = tmp_out.name[:-4]  # quita .txt

            # Llamar a tesseract - separar config en argumentos individuales
            cmd = [self._tesseract_cmd, img_path, output_path] + config.split()
            subprocess.run(cmd, check=True, capture_output=True, timeout=10)

            # Leer resultado
            with open(output_path + ".txt", "r", encoding="utf-8") as f:
                result = f.read()

            # Limpiar archivos temporales
            try:
                os.remove(img_path)
                os.remove(output_path + ".txt")
            except:
                pass

            return result
        except Exception as e:
            logger.error("Error en tesseract directo: %s", e)
            return ""

    def _clean_text(self, text: str) -> str:
        return re.sub(r"[^A-Z\s]", " ", text.upper())

    def _clean_words(self, text: str) -> list[str]:
        return [
            word
            for word in self._clean_text(text).split()
            if len(word) >= 2 and word not in self.IGNORED
        ]

    def _extract_name(self, text: str) -> str | None:
        """Extrae nombre con prioridad a palabras clave (VINI, JR, etc)"""
        clean = self._clean_text(text)
        all_words = clean.split()

        # Palabras clave conocidas en LaLiga
        key_words = {"VINI", "RODRYGO", "BELLINGHAM", "MBAPPE", "JUNIOR", "JR"}

        # Buscar palabras clave en el texto
        found_keys = [
            w for w in all_words if w in key_words or any(k in w for k in key_words)
        ]

        if found_keys:
            # Si encontramos palabras clave, devolverlas
            # Buscar "JR" o "JUNIOR" después de una palabra larga
            for i, word in enumerate(all_words):
                if len(word) >= 4 and i + 1 < len(all_words):
                    next_word = all_words[i + 1]
                    if "JR" in next_word or "JUNIOR" in next_word:
                        return f"{word} {next_word}"

            # Si no, devolver la primera palabra clave encontrada
            if found_keys:
                # Buscar si hay un JR cerca
                for i, w in enumerate(all_words):
                    if w in found_keys:
                        result = w
                        # Buscar JR en los próximos 3 words
                        for j in range(i + 1, min(i + 3, len(all_words))):
                            if "JR" in all_words[j] or "JUNIOR" in all_words[j]:
                                result += " " + all_words[j]
                                break
                        return result

        # Fallback: buscar nombres completos (combinación de palabras largas)
        # Filtrar palabras válidas
        valid_words = [w for w in all_words if len(w) >= 3 and w not in self.IGNORED]

        if len(valid_words) >= 2:
            # Si hay 2+ palabras, combinar las primeras 2-3 (nombre + apellido)
            candidate = " ".join(valid_words[:3])
            return candidate
        elif len(valid_words) == 1:
            return valid_words[0]

        return None

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

        try:
            h, w = image.shape[:2]
            footer = image[int(h * 0.6) :, :]

            # ZONA SUPERIOR: buscar dorsal (está en la mitad inferior del jugador)
            # Procesamos desde 40% hasta 80% de altura para capturar el dorsal
            upper_zone = image[int(h * 0.25) : int(h * 0.75), :]

            # Procesado dual del footer
            gray = cv2.cvtColor(footer, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

            # Modo 1: Normal
            thr1 = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10
            )
            txt1 = self.run_ocr(thr1, config="--psm 6")

            # Modo 2: Invertido
            _, thr2 = cv2.threshold(
                gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
            )
            txt2 = self.run_ocr(thr2, config="--psm 6")

            combined = f"{txt1}\n{txt2}"
            result.raw_text = combined
            result.player_name = self._extract_name(combined)
            result.team_name = self._extract_team(combined)

            # Dorsal: también procesar zona superior
            gray_upper = cv2.cvtColor(upper_zone, cv2.COLOR_BGR2GRAY)
            gray_upper = cv2.resize(
                gray_upper, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC
            )

            # Buscar números en zona superior (PSM 13: imagen de línea única)
            thr_upper = cv2.adaptiveThreshold(
                gray_upper,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                31,
                10,
            )
            txt_upper = self.run_ocr(thr_upper, config="--psm 13")

            # Combinar todos los textos para búsqueda de números
            all_text = f"{combined}\n{txt_upper}"

            # Buscar números de 1-2 dígitos (dorsales válidos)
            nums = re.findall(r"\b\d{1,2}\b", all_text)
            if nums:
                # Tomar el primer número válido (entre 1-99)
                for num_str in nums:
                    num = int(num_str)
                    if 1 <= num <= 99:  # Dorsal válido (evitar 0)
                        result.jersey_number = num_str
                        break

            # Tokens extra para el frontend
            result.extra_tokens = [w for w in combined.upper().split() if len(w) > 3][
                :10
            ]
            # Guardamos zona para el response_builder
            result.jersey_zone = footer

        except Exception as e:
            logger.error("Error en OCR.extract: %s", e)
            # Devolver result vacío (graceful degradation)

        return result
