from django.db import models
from pgvector.django import VectorField


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=3, unique=True)
    flag_url = models.URLField(blank=True)

    class Meta:
        db_table = "players_country"

    def __str__(self):
        return self.name


class Competition(models.Model):
    name = models.CharField(max_length=150)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=20, default="league")

    class Meta:
        db_table = "players_competition"

    def __str__(self):
        return self.name


class Season(models.Model):
    name = models.CharField(max_length=20, unique=True)
    year_start = models.PositiveSmallIntegerField()
    year_end = models.PositiveSmallIntegerField()
    is_current = models.BooleanField(default=False)

    class Meta:
        db_table = "players_season"

    def __str__(self):
        return self.name


class Club(models.Model):
    name = models.CharField(max_length=150)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    city = models.CharField(max_length=100, blank=True)
    logo_url = models.URLField(blank=True)

    class Meta:
        db_table = "players_club"

    def __str__(self):
        return self.name


class Player(models.Model):
    STATUS = [
        ("active", "Activo"),
        ("injured", "Lesionado"),
        ("suspended", "Sancionado"),
        ("retired", "Retirado"),
        ("free_agent", "Libre"),
    ]
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    alias = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    nationality = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    current_club = models.ForeignKey(
        Club, on_delete=models.SET_NULL, null=True, blank=True
    )
    position = models.CharField(max_length=20, blank=True)
    shirt_number = models.PositiveSmallIntegerField(null=True, blank=True)
    height_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    weight_kg = models.PositiveSmallIntegerField(null=True, blank=True)
    preferred_foot = models.CharField(max_length=10, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="active")
    market_value_eur = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    photo_url = models.URLField(blank=True)
    face_embedding = VectorField(dimensions=512, null=True, blank=True)
    external_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "players_player"
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["position"]),
            models.Index(fields=["current_club"]),
        ]

    def __str__(self):
        return self.alias or f"{self.first_name} {self.last_name}"


class PlayerClubHistory(models.Model):
    """
    Historial de clubes por jugador.
    Necesario para el ML de valor de mercado y el dashboard.
    """

    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="club_history"
    )
    club = models.ForeignKey(
        Club, on_delete=models.CASCADE, related_name="player_history"
    )
    season = models.ForeignKey(Season, on_delete=models.SET_NULL, null=True)
    date_from = models.DateField()
    date_to = models.DateField(null=True, blank=True)
    loan = models.BooleanField(default=False)
    transfer_fee = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )

    class Meta:
        db_table = "players_club_history"
        ordering = ["-date_from"]

    def __str__(self):
        return f"{self.player} → {self.club} ({self.date_from})"


class SeasonPlayerStat(models.Model):
    """
    Estadísticas agregadas por jugador y temporada.
    Son el input principal del modelo ML de valor de mercado.
    """

    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="season_stats"
    )
    season = models.ForeignKey(
        Season, on_delete=models.CASCADE, related_name="player_stats"
    )
    club = models.ForeignKey(
        Club, on_delete=models.CASCADE, related_name="season_stats"
    )
    competition = models.ForeignKey(Competition, on_delete=models.SET_NULL, null=True)
    appearances = models.PositiveSmallIntegerField(default=0)
    minutes = models.PositiveIntegerField(default=0)
    goals = models.PositiveSmallIntegerField(default=0)
    assists = models.PositiveSmallIntegerField(default=0)
    yellow_cards = models.PositiveSmallIntegerField(default=0)
    red_cards = models.PositiveSmallIntegerField(default=0)
    avg_rating = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True
    )

    class Meta:
        db_table = "players_season_stat"
        unique_together = ("player", "season", "club", "competition")

    def __str__(self):
        return f"{self.player} — {self.season} — {self.goals}G {self.assists}A"
