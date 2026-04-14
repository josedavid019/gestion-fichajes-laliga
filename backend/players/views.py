from rest_framework import viewsets, filters
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from .models import Player
from .serializers import PlayerSerializer


class PlayerPagination(LimitOffsetPagination):
    default_limit = 50
    max_limit = 100


class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Player.objects.select_related(
        "nationality", "current_club", "current_club__country"
    ).all()
    serializer_class = PlayerSerializer
    pagination_class = PlayerPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "current_club", "nationality"]
    search_fields = ["first_name", "last_name", "alias"]
    ordering_fields = ["market_value_eur", "date_of_birth", "created_at"]
    ordering = ["-market_value_eur"]
