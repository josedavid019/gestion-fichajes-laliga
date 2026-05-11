from django.db import models
from pgvector.django import VectorField
from django.db.models import Q


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    iso_code = models.CharField(max_length=3, unique=True)
    flag_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "players_country"

    def __str__(self):
        return self.name


class Competition(models.Model):
    COMPETITION_TYPES = [
        ("league", "League"),
        ("cup", "Cup"),
        ("international", "International"),
        ("friendly", "Friendly"),
    ]
    name = models.CharField(max_length=150)
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        related_name="competitions",
    )
    type = models.CharField(max_length=20, choices=COMPETITION_TYPES, default="league")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "players_competition"

    def __str__(self):
        return self.name


class Season(models.Model):
    name = models.CharField(max_length=20, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "players_season"
        constraints = [
            models.UniqueConstraint(
                fields=["is_current"],
                condition=Q(is_current=True),
                name="unique_current_season",
            ),
            models.CheckConstraint(
                condition=Q(start_date__lt=models.F("end_date")),
                name="season_start_before_end",
            ),
        ]

    def __str__(self):
        return self.name


class Club(models.Model):
    name = models.CharField(max_length=150, unique=True)
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        related_name="clubs",
    )
    city = models.CharField(max_length=100, blank=True)
    founded_year = models.IntegerField(null=True, blank=True)
    stadium = models.CharField(max_length=150, blank=True)
    budget = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    logo_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    FOOT_CHOICES = [
        ("left", "Left"),
        ("right", "Right"),
        ("both", "Both"),
    ]
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    alias = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    nationality = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        related_name="players",
    )
    current_club = models.ForeignKey(
        Club,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="current_players",
    )
    shirt_number = models.PositiveSmallIntegerField(null=True, blank=True)
    height_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    weight_kg = models.PositiveSmallIntegerField(null=True, blank=True)
    preferred_foot = models.CharField(max_length=10, choices=FOOT_CHOICES, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="active")
    market_value_eur = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    photo_url = models.URLField(blank=True)
    face_embedding = VectorField(dimensions=512, null=True, blank=True)
    external_id = models.CharField(max_length=100, blank=True, unique=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "players_player"
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["current_club"]),
        ]

    def __str__(self):
        return self.alias or f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class PlayerClubHistory(models.Model):
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
    is_current = models.BooleanField(default=False)

    class Meta:
        db_table = "players_club_history"
        ordering = ["-date_from"]
        indexes = [
            models.Index(fields=["player"]),
            models.Index(fields=["club"]),
            models.Index(fields=["is_current"]),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["player"],
                condition=Q(is_current=True),
                name="unique_current_club_history_per_player",
            )
        ]

    def __str__(self):
        return f"{self.player} → {self.club} ({self.date_from})"


class SeasonPlayerStat(models.Model):
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
        constraints = [
            models.UniqueConstraint(
                fields=["player", "season", "club", "competition"],
                name="unique_player_season_club_competition",
            )
        ]
        indexes = [
            models.Index(fields=["player"]),
            models.Index(fields=["season"]),
            models.Index(fields=["club"]),
        ]

    def __str__(self):
        return f"{self.player} — {self.season} — {self.goals}G {self.assists}A"


class PlayerPosition(models.Model):
    POSITION_CHOICES = [
        ("GK", "Portero"),
        ("CB", "Defensa Central"),
        ("LB", "Lateral Izquierdo"),
        ("RB", "Lateral Derecho"),
        ("CM", "Centrocampista"),
        ("CDM", "Centrocampista Defensivo"),
        ("CAM", "Centrocampista Ofensivo"),
        ("LW", "Extremo Izquierdo"),
        ("RW", "Extremo Derecho"),
        ("ST", "Delantero"),
        ("CF", "Delantero Centro"),
    ]
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="positions"
    )
    position = models.CharField(max_length=10, choices=POSITION_CHOICES)
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = "players_player_position"
        constraints = [
            models.UniqueConstraint(
                fields=["player", "position"], name="unique_player_position"
            )
        ]

    def __str__(self):
        return f"{self.player} — {self.position}"


class PlayerNationality(models.Model):
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="nationalities"
    )
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    class Meta:
        db_table = "players_player_nationality"
        constraints = [
            models.UniqueConstraint(
                fields=["player", "country"], name="unique_player_country"
            )
        ]

    def __str__(self):
        return f"{self.player} — {self.country}"


class ClubCompetition(models.Model):
    club = models.ForeignKey(
        Club, on_delete=models.CASCADE, related_name="competitions"
    )
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "players_club_competition"
        constraints = [
            models.UniqueConstraint(
                fields=["club", "competition", "season"],
                name="unique_club_competition_season",
            )
        ]

    def __str__(self):
        return f"{self.club} — {self.competition} — {self.season}"


class Match(models.Model):
    MATCH_STATUS = [
        ("scheduled", "Scheduled"),
        ("live", "Live"),
        ("finished", "Finished"),
        ("cancelled", "Cancelled"),
    ]
    competition = models.ForeignKey(
        Competition, on_delete=models.CASCADE, related_name="matches"
    )
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="matches")
    home_club = models.ForeignKey(
        Club, on_delete=models.CASCADE, related_name="home_matches"
    )
    away_club = models.ForeignKey(
        Club, on_delete=models.CASCADE, related_name="away_matches"
    )
    match_date = models.DateTimeField()
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=MATCH_STATUS, default="scheduled")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "players_match"
        indexes = [
            models.Index(fields=["match_date"]),
            models.Index(fields=["season"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=~Q(home_club=models.F("away_club")),
                name="prevent_same_home_away_club",
            )
        ]

    def __str__(self):
        return f"{self.home_club} vs {self.away_club} — {self.match_date}"


class PlayerMatchStat(models.Model):
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="match_stats"
    )
    match = models.ForeignKey(
        Match, on_delete=models.CASCADE, related_name="player_stats"
    )
    goals = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    minutes_played = models.IntegerField(default=0)
    yellow_cards = models.IntegerField(default=0)
    red_cards = models.IntegerField(default=0)

    class Meta:
        db_table = "players_player_match_stat"
        constraints = [
            models.UniqueConstraint(
                fields=["player", "match"], name="unique_player_match_stat"
            )
        ]
        indexes = [
            models.Index(fields=["player"]),
            models.Index(fields=["match"]),
        ]

    def __str__(self):
        return f"{self.player} — {self.match} — {self.goals}G {self.assists}A"


class Injury(models.Model):
    INJURY_TYPES = [
        ("muscle", "Lesión Muscular"),
        ("fracture", "Fractura"),
        ("ligament", "Lesión de Ligamento"),
        ("concussion", "Conmoción"),
        ("other", "Otra"),
    ]
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="injuries"
    )
    injury_type = models.CharField(max_length=20, choices=INJURY_TYPES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "players_injury"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.player} — {self.injury_type} ({self.start_date})"


class Suspension(models.Model):
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="suspensions"
    )
    reason = models.CharField(max_length=255)
    matches_suspended = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "players_suspension"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.player} — {self.reason} ({self.matches_suspended} matches)"
