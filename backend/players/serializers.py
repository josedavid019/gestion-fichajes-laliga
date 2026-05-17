from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import (
    Player,
    Club,
    Country,
    Season,
    Competition,
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


class VectorFieldSerializer(serializers.Field):
    def to_internal_value(self, data):
        if data is None:
            return None
        if not isinstance(data, list):
            raise ValidationError("Expected a list of numbers for the vector field.")
        try:
            return [float(value) for value in data]
        except (TypeError, ValueError):
            raise ValidationError("Each vector element must be a number.")

    def to_representation(self, value):
        if value is None:
            return None
        return list(value)


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["id", "name", "code", "flag_url"]


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = "__all__"


class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = "__all__"


class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = "__all__"


class PlayerPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerPosition
        fields = "__all__"


class PlayerSerializer(serializers.ModelSerializer):
    nationality = CountrySerializer(read_only=True)
    position = serializers.SerializerMethodField()
    positions = PlayerPositionSerializer(many=True, read_only=True)
    current_club = ClubSerializer(read_only=True)
    current_club_id = serializers.PrimaryKeyRelatedField(
        queryset=Club.objects.all(),
        source="current_club",
        write_only=True,
        required=False,
        allow_null=True,
    )
    position_name = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    face_embedding = VectorFieldSerializer(allow_null=True, required=False)

    class Meta:
        model = Player
        fields = "__all__"

    def get_position(self, obj: Player):
        primary = obj.positions.filter(is_primary=True).first()
        if primary:
            return primary.position
        first = obj.positions.first()
        return first.position if first else None

    def _set_primary_position(self, player: Player, position_name: str | None):
        if not position_name:
            return
        player.positions.update(is_primary=False)
        PlayerPosition.objects.update_or_create(
            player=player,
            position=position_name,
            defaults={"is_primary": True},
        )

    def create(self, validated_data):
        position_name = validated_data.pop("position_name", None)
        player = super().create(validated_data)
        self._set_primary_position(player, position_name)
        return player

    def update(self, instance, validated_data):
        position_name = validated_data.pop("position_name", None)
        player = super().update(instance, validated_data)
        if position_name is not None:
            self._set_primary_position(player, position_name)
        return player


class PlayerNationalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerNationality
        fields = "__all__"


class PlayerClubHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerClubHistory
        fields = "__all__"


class SeasonPlayerStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeasonPlayerStat
        fields = "__all__"


class ClubCompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubCompetition
        fields = "__all__"


class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = "__all__"


class PlayerMatchStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerMatchStat
        fields = "__all__"


class InjurySerializer(serializers.ModelSerializer):
    class Meta:
        model = Injury
        fields = "__all__"


class SuspensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suspension
        fields = "__all__"
