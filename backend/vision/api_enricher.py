import logging
import os
import re
from difflib import SequenceMatcher
from typing import Optional

import requests

logger = logging.getLogger(__name__)

OCR_ALIAS_MAP = {
    "VINI": "Vinicius",
    "VINI JR": "Vinicius Junior",
    "VINI JR.": "Vinicius Junior",
    "JR": "Junior",
}


class APIFootballClient:
    BASE_URL = "https://v3.football.api-sports.io"
    DEFAULT_SEASON = int(os.getenv("FOOTBALL_API_SEASON", "2024"))

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("APISPORTS_FOOTBALL_KEY", "")
        self.headers = {"x-apisports-key": self.api_key}

    @staticmethod
    def _normalize_height(height_str: str | None) -> Optional[int]:
        """Extrae cm de strings como '183 cm' o '6'0'"""
        if not height_str:
            return None
        if "cm" in str(height_str).lower():
            try:
                return int(re.findall(r"\d+", str(height_str))[0])
            except (IndexError, ValueError):
                pass
        return None

    @staticmethod
    def _normalize_weight(weight_str: str | None) -> Optional[int]:
        """Extrae kg de strings como '75 kg'"""
        if not weight_str:
            return None
        if "kg" in str(weight_str).lower():
            try:
                return int(re.findall(r"\d+", str(weight_str))[0])
            except (IndexError, ValueError):
                pass
        return None

    @staticmethod
    def _parse_name(full_name: str) -> tuple[str, str]:
        """Separa nombre en first_name y last_name"""
        if not full_name:
            return "", ""
        parts = full_name.strip().rsplit(" ", 1)
        if len(parts) == 2:
            return parts[0], parts[1]
        return full_name, ""

    def _get_injuries(self, player_id: int) -> dict | None:
        """Obtiene estado de lesión/sanción del jugador"""
        if not self.api_key:
            return None
        try:
            params = {
                "season": self.DEFAULT_SEASON,
                "player": player_id,
            }
            r = requests.get(
                f"{self.BASE_URL}/injuries",
                headers=self.headers,
                params=params,
                timeout=10,
            )
            r.raise_for_status()
            data = r.json()
            injuries = data.get("response") or []
            if injuries:
                # Devolver la lesión/sanción más reciente
                latest = injuries[0]
                return {
                    "status": latest.get("type"),  # injury, suspension
                    "reason": latest.get("reason"),
                    "from": latest.get("start"),
                    "to": latest.get("end"),
                }
            return None
        except requests.RequestException as e:
            logger.debug("Fallo en /injuries para player_id %s: %s", player_id, e)
            return None

    def _get_jersey_number(
        self, player_id: int, team_name: str | None = None
    ) -> str | None:
        """Obtiene el número de dorsal desde /players/squads"""
        if not self.api_key or not player_id:
            return None
        try:
            params = {"player": player_id}
            r = requests.get(
                f"{self.BASE_URL}/players/squads",
                headers=self.headers,
                params=params,
                timeout=10,
            )
            r.raise_for_status()
            data = r.json()
            squads = data.get("response") or []

            if not squads:
                return None

            # Intentar encontrar coincidencia exacta con team_name si se proporciona
            if team_name:
                for squad in squads:
                    squad_team = squad.get("team", {})
                    squad_team_name = squad_team.get("name")

                    if (
                        squad_team_name
                        and self._normalize_name(team_name).lower()
                        in self._normalize_name(squad_team_name).lower()
                    ):
                        players = squad.get("players") or []
                        if players:
                            return str(players[0].get("number"))

            # Fallback: usar el primer equipo si no hay coincidencia
            # (Los datos pueden estar desfasados o el jugador cambió recientemente)
            squad = squads[0]
            players = squad.get("players") or []
            if players:
                return str(players[0].get("number"))

            return None
        except requests.RequestException as e:
            logger.debug("Fallo en /squads para player_id %s: %s", player_id, e)
            return None

            return None

    @staticmethod
    def _normalize_name(name: str) -> str:
        return re.sub(r"[^A-Za-z\s]", "", name).strip()

    @classmethod
    def _is_reasonable_match(cls, query_name: str, result_name: str | None) -> bool:
        if not result_name:
            return False

        query = cls._normalize_name(query_name).lower()
        result = cls._normalize_name(result_name).lower()
        if len(query) < 3 or len(result) < 3:
            return False

        query_tokens = {token for token in query.split() if len(token) >= 4}
        result_tokens = {token for token in result.split() if len(token) >= 4}

        if query and query in result:
            return True

        if query_tokens & result_tokens:
            return True

        return SequenceMatcher(None, query, result).ratio() >= 0.55

    @classmethod
    def _score_candidate(
        cls,
        query_name: str,
        result_name: str | None,
        team_name: str | None = None,
        candidate_team: str | None = None,
    ) -> float:
        if not result_name:
            return float("-inf")

        query = cls._normalize_name(query_name).lower()
        result = cls._normalize_name(result_name).lower()
        query_tokens = {token for token in query.split() if len(token) >= 3}
        result_tokens = {token for token in result.split() if len(token) >= 3}
        overlap = query_tokens & result_tokens

        similarity = SequenceMatcher(None, query, result).ratio()

        # Base score: similitud de string
        score = similarity * 100

        # Bonus por tokens en común
        score += len(overlap) * 25

        # IMPORTANTE: Si query tiene múltiples palabras (nombre completo),
        # requiere mejor match para evitar falsos positivos
        query_word_count = len(query_tokens)
        if query_word_count >= 2:
            # Búsqueda de nombre completo - ser más exigente
            if len(overlap) == 0:
                # Sin overlap, muy bajo score
                score *= 0.3
            elif len(overlap) == 1:
                # Solo 1 palabra en común - moderado
                score *= 0.6

        # Bonus por coincidencias exactas
        if query and query in result:
            score += 30

        # Prioriza "junior/jr"
        if (" jr" in f" {query}" or "junior" in query) and (
            "junior" in result or " jr" in f" {result}"
        ):
            score += 40

        if "vini" in query and ("vinicius junior" in result or "vinicius jr" in result):
            score += 50

        # Team bonus
        if team_name and candidate_team:
            normalized_team = cls._normalize_name(team_name).lower()
            normalized_candidate_team = cls._normalize_name(candidate_team).lower()
            if normalized_team and normalized_team in normalized_candidate_team:
                score += 25

        return score

    def _query(self, name: str, team_name: str | None = None):
        # Limpiamos: solo letras y espacios
        clean = self._normalize_name(name)
        if len(clean) < 3 or not self.api_key:
            return None

        # Búsqueda en LaLiga y Segunda
        best_candidate = None
        best_score = float("-inf")
        for league in [140, 141]:
            params = {"search": clean, "league": league, "season": self.DEFAULT_SEASON}
            try:
                r = requests.get(
                    f"{self.BASE_URL}/players",
                    headers=self.headers,
                    params=params,
                    timeout=10,
                )
                r.raise_for_status()
                data = r.json()
                responses = data.get("response") or []
                for res in responses:
                    stats = res.get("statistics", [{}])[0]
                    goals = stats.get("goals", {})
                    passes = stats.get("passes", {})
                    games = stats.get("games", {})
                    full_name = res["player"]["name"]
                    first_name, last_name = self._parse_name(full_name)
                    height_cm = self._normalize_height(res["player"].get("height"))
                    weight_kg = self._normalize_weight(res["player"].get("weight"))
                    position = games.get("position")
                    player_id = res["player"].get("id")
                    team_name = stats.get("team", {}).get("name")
                    # Obtener dorsal desde /players/squads
                    jersey_number = (
                        self._get_jersey_number(player_id, team_name)
                        if player_id
                        else None
                    )
                    injuries = self._get_injuries(player_id) if player_id else None

                    candidate = {
                        "full_name": full_name,
                        "first_name": first_name,
                        "last_name": last_name,
                        "nationality": res["player"]["nationality"],
                        "age": res["player"]["age"],
                        "birth_date": res["player"].get("birth", {}).get("date"),
                        "height": res["player"].get("height"),
                        "height_cm": height_cm,
                        "weight": res["player"].get("weight"),
                        "weight_kg": weight_kg,
                        "position": position,
                        "jersey_number": jersey_number,
                        "photo_url": res["player"].get("photo"),
                        "status": injuries.get("status") if injuries else None,
                        "statistics": {
                            "appearances": games.get("appearences"),
                            "minutes_played": games.get("minutes"),
                            "rating": games.get("rating"),
                            "goals": goals.get("total"),
                            "assists": goals.get("assists"),
                            "key_passes": passes.get("key"),
                            "accuracy_passes": passes.get("accuracy"),
                        },
                        "team": {
                            "name": stats.get("team", {}).get("name"),
                            "logo": stats.get("team", {}).get("logo"),
                        },
                    }
                    if self._is_reasonable_match(clean, candidate["full_name"]):
                        score = self._score_candidate(
                            clean,
                            candidate["full_name"],
                            team_name=team_name,
                            candidate_team=candidate["team"]["name"],
                        )
                        if score > best_score:
                            best_candidate = candidate
                            best_score = score
            except requests.RequestException as exc:
                logger.warning("Fallo API-Football para '%s': %s", clean, exc)
                continue
            except (KeyError, IndexError, TypeError, ValueError) as exc:
                logger.warning(
                    "Respuesta invalida API-Football para '%s': %s", clean, exc
                )
                continue
        return best_candidate

    def search_player(self, name: str, team_name: str | None = None):
        # 1. Intentar primero con el nombre COMPLETO
        res = self._query(name, team_name=team_name)
        if res:
            return res

        # 2. Si hay múltiples palabras, intentar estrategias adicionales
        parts = name.split()
        if len(parts) >= 2:
            # 2a. Intentar con el ULTIMO apellido (más específico)
            last_name = parts[-1]
            if len(last_name) >= 4:  # Solo si apellido es largo
                res_last = self._query(last_name, team_name=team_name)
                if res_last:
                    return res_last

            # 2b. Intentar quitando la primera palabra (por si es basura)
            rest_name = " ".join(parts[1:])
            if rest_name and rest_name != last_name:
                res_rest = self._query(rest_name, team_name=team_name)
                if res_rest:
                    return res_rest

        return None


class TheSportsDBClient:
    BASE_URL = "https://www.thesportsdb.com/api/v1/json"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("THESPORTSDB_API_KEY", "3")

    @staticmethod
    def _normalize_name(name: str) -> str:
        return re.sub(r"[^A-Za-z\s]", "", name).strip()

    def _query(self, name: str, team_name: str | None = None):
        clean = self._normalize_name(name)
        if len(clean) < 3 or not self.api_key:
            return None

        try:
            response = requests.get(
                f"{self.BASE_URL}/{self.api_key}/searchplayers.php",
                params={"p": clean},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            players = data.get("player") or []
            if not players:
                return None

            best_candidate = None
            best_score = float("-inf")
            for player in players:
                full_name = player.get("strPlayer")
                first_name, last_name = (
                    APIFootballClient._parse_name(full_name) if full_name else ("", "")
                )
                height_cm = APIFootballClient._normalize_height(player.get("strHeight"))
                weight_kg = APIFootballClient._normalize_weight(player.get("strWeight"))

                candidate = {
                    "full_name": full_name,
                    "first_name": first_name,
                    "last_name": last_name,
                    "nationality": player.get("strNationality"),
                    "age": None,
                    "birth_date": player.get("dateBorn"),
                    "height": player.get("strHeight"),
                    "height_cm": height_cm,
                    "weight": player.get("strWeight"),
                    "weight_kg": weight_kg,
                    "photo_url": player.get("strThumb") or player.get("strCutout"),
                    "statistics": {},
                    "team": {
                        "name": player.get("strTeam"),
                        "logo": player.get("strTeamBadge") or player.get("strBadge"),
                    },
                    "position": player.get("strPosition"),
                    "jersey_number": None,  # TheSportsDB no proporciona dorsal actual
                    "status": None,  # TheSportsDB no tiene endpoint de lesiones
                    "profile_url": player.get("strWebsite"),
                    "source": "the_sports_db",
                }
                if APIFootballClient._is_reasonable_match(
                    clean, candidate["full_name"]
                ):
                    score = APIFootballClient._score_candidate(
                        clean,
                        candidate["full_name"],
                        team_name=team_name,
                        candidate_team=candidate["team"]["name"],
                    )
                    if score > best_score:
                        best_candidate = candidate
                        best_score = score
            return best_candidate
        except requests.RequestException as exc:
            logger.warning("Fallo TheSportsDB para '%s': %s", clean, exc)
            return None
        except (TypeError, ValueError) as exc:
            logger.warning("Respuesta invalida TheSportsDB para '%s': %s", clean, exc)
            return None

    def search_player(self, name: str, team_name: str | None = None):
        res = self._query(name, team_name=team_name)
        if res:
            return res

        parts = name.split()
        if len(parts) >= 2:
            res_retry = self._query(" ".join(parts[1:]), team_name=team_name)
            if res_retry:
                return res_retry
            return self._query(parts[-1], team_name=team_name)

        return None


class PlayerEnricher:
    def __init__(
        self,
        football_api_key: str | None = None,
        thesportsdb_api_key: str | None = None,
    ):
        self.football = APIFootballClient(football_api_key)
        self.the_sports_db = TheSportsDBClient(thesportsdb_api_key)

    def enrich(self, player_name: str, team_name: str | None = None) -> dict:
        errors = []
        sources_used = []
        if not self.football.api_key:
            errors.append("APISPORTS_FOOTBALL_KEY no configurada")

        football_data = self.football.search_player(player_name, team_name=team_name)
        if football_data:
            football_data["source"] = "api_football"
            sources_used.append("api_football")

        # Fallback especial para Vinicius Junior (la API es sensible a su nombre)
        if not football_data and "VINI" in player_name.upper():
            football_data = self.football.search_player("Vinicius", team_name=team_name)
            if football_data:
                football_data["source"] = "api_football"
                sources_used.append("api_football")

        if not football_data:
            alias_query = OCR_ALIAS_MAP.get(player_name.upper().strip())
            if alias_query:
                football_data = self.football.search_player(
                    alias_query, team_name=team_name
                )
                if football_data:
                    football_data["source"] = "api_football"
                    sources_used.append("api_football")

        sportsdb_data = None
        if not football_data:
            sportsdb_data = self.the_sports_db.search_player(
                player_name, team_name=team_name
            )
            if sportsdb_data:
                sources_used.append("the_sports_db")

        if not football_data and not sportsdb_data:
            alias_query = OCR_ALIAS_MAP.get(player_name.upper().strip())
            if alias_query:
                sportsdb_data = self.the_sports_db.search_player(
                    alias_query, team_name=team_name
                )
                if sportsdb_data:
                    sources_used.append("the_sports_db")

        if not sportsdb_data and not football_data:
            errors.append("No se encontraron datos externos para el jugador")

        return {
            "api_football": football_data,
            "the_sports_db": sportsdb_data,
            "query": {"name": player_name, "team": team_name},
            "source": sources_used[0] if sources_used else None,
            "sources_used": sources_used,
            "enrichment_errors": errors,
        }
