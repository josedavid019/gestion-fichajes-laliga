import logging
import os
import tempfile

import cv2

logger = logging.getLogger(__name__)


class VideoAnalyzer:
    def __init__(self, pipeline, sample_seconds: float = 1.0, max_frames: int = 8):
        self.pipeline = pipeline
        self.sample_seconds = sample_seconds
        self.max_frames = max_frames

    def analyze(self, video_bytes: bytes, player_name_hint: str | None = None) -> dict:
        video_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_video:
                tmp_video.write(video_bytes)
                video_path = tmp_video.name

            capture = cv2.VideoCapture(video_path)
            if not capture.isOpened():
                return self._error("No se pudo abrir el video proporcionado")

            fps = capture.get(cv2.CAP_PROP_FPS) or 0
            total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
            stride = max(1, int(fps * self.sample_seconds)) if fps else 15

            frame_results = []
            frame_index = 0
            while len(frame_results) < self.max_frames:
                ok, frame = capture.read()
                if not ok:
                    break
                if frame_index % stride == 0:
                    frame_results.append(
                        self.pipeline.run_image_array(
                            frame,
                            player_name_hint=player_name_hint,
                            media_type="video",
                        )
                    )
                frame_index += 1

            capture.release()
            if not frame_results:
                return self._error("No se pudieron extraer frames utilizables del video")

            return self._aggregate(frame_results, fps=fps, total_frames=total_frames)
        except Exception as exc:
            logger.exception("Error analizando video: %s", exc)
            return self._error(f"Error analizando video: {exc}")
        finally:
            if video_path and os.path.exists(video_path):
                try:
                    os.remove(video_path)
                except OSError:
                    logger.debug("No se pudo borrar temporal %s", video_path)

    @staticmethod
    def _error(message: str) -> dict:
        return {
            "meta": {"error": True, "message": message},
            "player_profile": None,
            "statistics": None,
            "market_value": None,
            "league_info": None,
            "vision_analysis": None,
        }

    def _aggregate(self, frame_results: list[dict], fps: float, total_frames: int) -> dict:
        best_result = max(
            frame_results,
            key=lambda item: (
                float(_face_confidence(item)),
                float(
                    item.get("vision_analysis", {})
                    .get("yolo", {})
                    .get("confidence", 0.0)
                    or 0.0
                ),
            ),
        )

        successful_frames = sum(
            1
            for item in frame_results
            if item.get("vision_analysis", {})
            .get("yolo", {})
            .get("player_detected", False)
        )
        best_result["meta"]["media_type"] = "video"
        best_result["meta"]["video_summary"] = {
            "frames_analyzed": len(frame_results),
            "frames_with_player": successful_frames,
            "fps": round(float(fps or 0), 2),
            "total_frames": total_frames,
        }
        best_result["vision_analysis"]["video"] = {
            "frames_analyzed": len(frame_results),
            "frames_with_player": successful_frames,
        }
        return best_result


def _face_confidence(item: dict) -> float:
    best_match = (
        item.get("vision_analysis", {})
        .get("face_recognition", {})
        .get("best_match")
    )
    if not isinstance(best_match, dict):
        return 0.0
    return float(best_match.get("confidence", 0.0) or 0.0)
