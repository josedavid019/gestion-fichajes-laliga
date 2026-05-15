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


class PlayerSerializer(serializers.ModelSerializer):
    nationality = CountrySerializer(read_only=True)
    position = serializers.ReadOnlyField()
    face_embedding = VectorFieldSerializer(allow_null=True, required=False)

    class Meta:
        model = Player
        fields = "__all__"


class PlayerPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerPosition
        fields = "__all__"


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
