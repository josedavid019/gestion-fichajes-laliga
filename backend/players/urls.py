from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CountryViewSet,
    SeasonViewSet,
    CompetitionViewSet,
    ClubViewSet,
    PlayerViewSet,
    PlayerPositionViewSet,
    PlayerNationalityViewSet,
    PlayerClubHistoryViewSet,
    SeasonPlayerStatViewSet,
    ClubCompetitionViewSet,
    MatchViewSet,
    PlayerMatchStatViewSet,
    InjuryViewSet,
    SuspensionViewSet,
)

router = DefaultRouter()
router.register(r"countries", CountryViewSet)
router.register(r"seasons", SeasonViewSet)
router.register(r"competitions", CompetitionViewSet)
router.register(r"clubs", ClubViewSet)
router.register(r"players", PlayerViewSet)
router.register(r"player-positions", PlayerPositionViewSet)
router.register(r"player-nationalities", PlayerNationalityViewSet)
router.register(r"player-club-history", PlayerClubHistoryViewSet)
router.register(r"season-player-stats", SeasonPlayerStatViewSet)
router.register(r"club-competitions", ClubCompetitionViewSet)
router.register(r"matches", MatchViewSet)
router.register(r"player-match-stats", PlayerMatchStatViewSet)
router.register(r"injuries", InjuryViewSet)
router.register(r"suspensions", SuspensionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
