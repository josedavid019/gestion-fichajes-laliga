from decimal import Decimal

from django.conf import settings
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import IsAdminOrDirectorOrReadOnly
from .models import (
    Country,
    Season,
    Competition,
    Club,
    Player,
    PlayerPosition,
    PlayerNationality,
    PlayerClubHistory,
    SeasonPlayerStat,
    ClubCompetition,
    Match,
    PlayerMatchStat,
    Injury,
    Suspension,
)
from .serializers import (
    CountrySerializer,
    SeasonSerializer,
    CompetitionSerializer,
    ClubSerializer,
    PlayerSerializer,
    PlayerPositionSerializer,
    PlayerNationalitySerializer,
    PlayerClubHistorySerializer,
    SeasonPlayerStatSerializer,
    ClubCompetitionSerializer,
    MatchSerializer,
    PlayerMatchStatSerializer,
    InjurySerializer,
    SuspensionSerializer,
)


class PlayerPagination(LimitOffsetPagination):
    default_limit = 50
    max_limit = 100


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "code"]
    ordering_fields = ["name"]


class SeasonViewSet(viewsets.ModelViewSet):
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["start_date", "end_date", "name"]


class CompetitionViewSet(viewsets.ModelViewSet):
    queryset = Competition.objects.select_related("country").all()
    serializer_class = CompetitionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "type", "code"]
    ordering_fields = ["name", "season_year", "is_current"]


class ClubViewSet(viewsets.ModelViewSet):
    queryset = Club.objects.select_related("country").all()
    serializer_class = ClubSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "city", "code"]
    ordering_fields = ["name", "founded_year"]


class PlayerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrDirectorOrReadOnly]
    queryset = (
        Player.objects.select_related(
            "current_club",
            "current_club__country",
        )
        .prefetch_related("positions", "nationalities")
        .all()
    )
    serializer_class = PlayerSerializer
    pagination_class = PlayerPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "status",
        "current_club",
        "nationalities__country",
        "positions__position",
    ]
    search_fields = ["first_name", "last_name", "alias", "full_name"]
    ordering_fields = ["market_value_eur", "date_of_birth", "created_at", "updated_at"]
    ordering = ["-market_value_eur"]

    @action(detail=False, methods=["post"], url_path="update-market-values")
    def update_market_values(self, request):
        api_key = (
            getattr(settings, "APISPORTS_FOOTBALL_KEY", None)
            or getattr(settings, "RAPIDAPI_FOOTBALL_KEY", None)
        )
        if not api_key:
            return Response(
                {"detail": "No se encuentra la clave de API Football en el servidor."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from vision.api_enricher import APIFootballClient

        limit = int(request.query_params.get("limit", 5))
        limit = min(limit, 20)

        players = Player.objects.filter(market_value_eur__isnull=True).order_by("id")[:limit]
        if not players:
            return Response(
                {"updated": 0, "scanned": 0, "message": "No hay jugadores pendientes de valor."},
                status=status.HTTP_200_OK,
            )

        client = APIFootballClient(api_key)
        updated = 0
        not_updated = []
        warnings = set()
        rate_limit_hit = False

        for player in players:
            search_name = f"{player.first_name} {player.last_name}".strip()
            if not search_name:
                search_name = player.alias or player.full_name

            team_name = player.current_club.name if player.current_club else None
            team_id = (
                player.current_club.external_id
                if player.current_club and player.current_club.external_id
                else None
            )

            search_names = [search_name]
            if player.alias and player.alias.strip().lower() not in {
                s.lower() for s in search_names
            }:
                search_names.append(player.alias.strip())
            if player.full_name and player.full_name.strip().lower() not in {
                s.lower() for s in search_names
            }:
                search_names.append(player.full_name.strip())

            football_data = None
            market_value = None

            if player.external_id:
                market_value = client._get_transfer_market_value(
                    player.external_id,
                    team_id=team_id,
                )
                if client.last_error:
                    warnings.add(client.last_error)
                    if "request limit" in client.last_error.lower() or \
                        "ratelimit" in client.last_error.lower():
                        not_updated.append(player.id)
                        rate_limit_hit = True

            if not rate_limit_hit and market_value is None:
                for candidate_name in search_names:
                    football_data = client.search_player(
                        candidate_name,
                        team_name=team_name,
                        team_id=team_id,
                    )
                    if client.last_error:
                        warnings.add(client.last_error)
                        if "request limit" in client.last_error.lower() or \
                            "ratelimit" in client.last_error.lower():
                            not_updated.append(player.id)
                            rate_limit_hit = True
                            break
                    if football_data:
                        break

            if rate_limit_hit:
                break

            if football_data and market_value is None:
                market_value = football_data.get("market_value_eur")

            if market_value is not None:
                player.market_value_eur = Decimal(str(market_value))
                if football_data.get("external_id") and not player.external_id:
                    player.external_id = football_data["external_id"]
                player.save(update_fields=["market_value_eur", "external_id"])
                updated += 1
            else:
                not_updated.append(player.id)

        response_payload = {
            "updated": updated,
            "scanned": len(players),
            "not_updated": not_updated,
            "warnings": list(warnings),
        }

        if any(
            "request limit" in warning.lower() or "ratelimit" in warning.lower()
            for warning in warnings
        ):
            return Response(response_payload, status=status.HTTP_429_TOO_MANY_REQUESTS)

        return Response(response_payload, status=status.HTTP_200_OK)


class PlayerPositionViewSet(viewsets.ModelViewSet):
    queryset = PlayerPosition.objects.select_related("player").all()
    serializer_class = PlayerPositionSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["player", "position", "is_primary"]
    search_fields = ["position"]
    ordering_fields = ["position", "is_primary"]


class PlayerNationalityViewSet(viewsets.ModelViewSet):
    queryset = PlayerNationality.objects.select_related("player", "country").all()
    serializer_class = PlayerNationalitySerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["player", "country", "is_primary"]
    search_fields = []
    ordering_fields = ["is_primary"]


class PlayerClubHistoryViewSet(viewsets.ModelViewSet):
    queryset = PlayerClubHistory.objects.select_related(
        "player", "club", "season"
    ).all()
    serializer_class = PlayerClubHistorySerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["player", "club", "season", "is_current"]
    search_fields = []
    ordering_fields = ["date_from", "date_to", "is_current"]


class SeasonPlayerStatViewSet(viewsets.ModelViewSet):
    queryset = SeasonPlayerStat.objects.select_related(
        "player", "season", "club", "competition"
    ).all()
    serializer_class = SeasonPlayerStatSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["player", "season", "club", "competition"]
    search_fields = []
    ordering_fields = ["appearances", "goals", "assists"]


class ClubCompetitionViewSet(viewsets.ModelViewSet):
    queryset = ClubCompetition.objects.select_related(
        "club", "competition", "season"
    ).all()
    serializer_class = ClubCompetitionSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["club", "competition", "season"]
    search_fields = []
    ordering_fields = ["created_at", "updated_at"]


class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.select_related(
        "competition", "season", "home_club", "away_club"
    ).all()
    serializer_class = MatchSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["competition", "season", "home_club", "away_club", "status"]
    search_fields = []
    ordering_fields = ["match_date", "status"]


class PlayerMatchStatViewSet(viewsets.ModelViewSet):
    queryset = PlayerMatchStat.objects.select_related("player", "match").all()
    serializer_class = PlayerMatchStatSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["player", "match"]
    search_fields = []
    ordering_fields = ["goals", "assists", "minutes_played"]


class InjuryViewSet(viewsets.ModelViewSet):
    queryset = Injury.objects.select_related("player").all()
    serializer_class = InjurySerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["player", "injury_type", "start_date", "end_date"]
    search_fields = ["injury_type", "description"]
    ordering_fields = ["start_date", "end_date"]


class SuspensionViewSet(viewsets.ModelViewSet):
    queryset = Suspension.objects.select_related("player").all()
    serializer_class = SuspensionSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["player", "start_date", "end_date"]
    search_fields = ["reason"]
    ordering_fields = ["start_date", "end_date"]
