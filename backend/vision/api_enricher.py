import logging
import os
import re
from difflib import SequenceMatcher

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

        score = SequenceMatcher(None, query, result).ratio() * 100
        score += len(overlap) * 18

        # Bonus por apellido/nombre exacto incluido en el resultado.
        if query and query in result:
            score += 25

        # Prioriza explicitamente "junior/jr" cuando el OCR lo sugiera.
        if (" jr" in f" {query}" or "junior" in query) and (
            "junior" in result or " jr" in f" {result}"
        ):
            score += 35

        if "vini" in query and ("vinicius junior" in result or "vinicius jr" in result):
            score += 45

        if team_name and candidate_team:
            normalized_team = cls._normalize_name(team_name).lower()
            normalized_candidate_team = cls._normalize_name(candidate_team).lower()
            if normalized_team and normalized_team in normalized_candidate_team:
                score += 20

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
                    candidate = {
                        "full_name": res["player"]["name"],
                        "nationality": res["player"]["nationality"],
                        "age": res["player"]["age"],
                        "birth_date": res["player"].get("birth", {}).get("date"),
                        "height": res["player"].get("height"),
                        "weight": res["player"].get("weight"),
                        "photo_url": res["player"].get("photo"),
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
        res = self._query(name, team_name=team_name)
        if res:
            return res

        # 2. Si falla y tiene varias palabras, probamos quitando la primera (por si es basura como LINC, IARC)
        parts = name.split()
        if len(parts) >= 2:
            # Reintentamos solo con el resto del nombre
            res_retry = self._query(" ".join(parts[1:]), team_name=team_name)
            if res_retry:
                return res_retry

            # 3. Si sigue fallando, probamos solo con el apellido final
            return self._query(parts[-1], team_name=team_name)

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
                candidate = {
                    "full_name": player.get("strPlayer"),
                    "nationality": player.get("strNationality"),
                    "age": None,
                    "birth_date": player.get("dateBorn"),
                    "height": player.get("strHeight"),
                    "weight": player.get("strWeight"),
                    "photo_url": player.get("strThumb") or player.get("strCutout"),
                    "statistics": {},
                    "team": {
                        "name": player.get("strTeam"),
                        "logo": player.get("strTeamBadge") or player.get("strBadge"),
                    },
                    "position": player.get("strPosition"),
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
