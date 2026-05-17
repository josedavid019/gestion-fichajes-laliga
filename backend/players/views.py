from rest_framework import viewsets, filters
from rest_framework.pagination import LimitOffsetPagination
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
