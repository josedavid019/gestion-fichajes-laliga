from rest_framework import serializers
from .models import Player, Club, Country


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["id", "name", "code", "flag_url"]


class ClubSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)

    class Meta:
        model = Club
        fields = ["id", "name", "country", "city", "logo_url"]


class PlayerSerializer(serializers.ModelSerializer):
    nationality = CountrySerializer(read_only=True)
    current_club = ClubSerializer(read_only=True)
    age = serializers.SerializerMethodField()

    class Meta:
        model = Player
        fields = [
            "id",
            "first_name",
            "last_name",
            "alias",
            "age",
            "nationality",
            "current_club",
            "position",
            "shirt_number",
            "height_cm",
            "weight_kg",
            "preferred_foot",
            "status",
            "market_value_eur",
            "photo_url",
        ]

    def get_age(self, obj):
        if obj.date_of_birth:
            from datetime import date
            today = date.today()
            return (
                today.year
                - obj.date_of_birth.year
                - (
                    (today.month, today.day)
                    < (obj.date_of_birth.month, obj.date_of_birth.day)
                )
            )
        return None
