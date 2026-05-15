from django.db import models
from pgvector.django import VectorField
from django.db.models import Q
from django.utils import timezone


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=6, blank=True, default="")
    flag_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "players_country"

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


class Competition(models.Model):
    name = models.CharField(max_length=150)
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        related_name="competitions",
    )
    type = models.CharField(max_length=50, blank=True)
    external_id = models.IntegerField(unique=True, null=True, blank=True)
    code = models.CharField(max_length=20, blank=True)
    logo_url = models.URLField(blank=True)
    is_current = models.BooleanField(default=False)
    season_year = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "players_competition"

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
    stadium_capacity = models.IntegerField(null=True, blank=True)
    stadium_image = models.URLField(blank=True)
    budget = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    logo_url = models.URLField(blank=True)
    external_id = models.IntegerField(unique=True, null=True, blank=True)
    code = models.CharField(max_length=20, blank=True)
    national = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "players_club"

    def __str__(self):
        return self.name


class Player(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("injured", "Injured"),
        ("suspended", "Suspended"),
        ("inactive", "Inactive"),
    ]
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    alias = models.CharField(max_length=100, blank=True)
    full_name = models.CharField(max_length=200, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
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
    preferred_foot = models.CharField(max_length=20, blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="active", blank=True
    )
    market_value_eur = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    photo_url = models.URLField(blank=True)
    external_id = models.IntegerField(unique=True, null=True, blank=True)
    face_embedding = VectorField(dimensions=512, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "players_player"
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["current_club"]),
            models.Index(fields=["full_name"]),
        ]

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        today = timezone.now().date()
        dob = self.date_of_birth
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    @property
    def position(self):
        primary = self.positions.filter(is_primary=True).first()
        if primary:
            return primary.position
        first = self.positions.first()
        return first.position if first else None

    @property
    def nationality(self):
        primary = self.nationalities.filter(is_primary=True).first()
        if primary:
            return primary.country
        first = self.nationalities.first()
        return first.country if first else None

    @property
    def is_injured(self):
        return self.injuries.filter(
            start_date__lte=timezone.now().date(), end_date__isnull=True
        ).exists()

    def __str__(self):
        return self.alias or self.full_name


class PlayerPosition(models.Model):
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="positions"
    )
    position = models.CharField(max_length=50)
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
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = "players_player_nationality"
        constraints = [
            models.UniqueConstraint(
                fields=["player", "country"], name="unique_player_country"
            ),
            models.UniqueConstraint(
                fields=["player"],
                condition=Q(is_primary=True),
                name="unique_primary_nationality_per_player",
            ),
        ]

    def __str__(self):
        return f"{self.player} — {self.country}"


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
    transfer_fee = models.CharField(max_length=50, blank=True, default="")
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
        max_digits=5, decimal_places=2, null=True, blank=True
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
        ("postponed", "Postponed"),
    ]

    STATUS_MAP = {
        "NS": "scheduled",
        "TBD": "scheduled",
        "1H": "live",
        "HT": "live",
        "2H": "live",
        "ET": "live",
        "BT": "live",
        "P": "live",
        "LIVE": "live",
        "FT": "finished",
        "AET": "finished",
        "PEN": "finished",
        "CANC": "cancelled",
        "ABD": "cancelled",
        "PST": "postponed",
        "SUSP": "postponed",
        "INT": "postponed",
        "AWD": "finished",
        "WO": "finished",
    }

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
    external_id = models.IntegerField(unique=True, null=True, blank=True)
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
            models.Index(fields=["external_id"]),
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
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="injuries"
    )
    injury_type = models.CharField(max_length=50)
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
    matches_suspended = models.IntegerField(null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "players_suspension"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.player} — {self.reason} ({self.start_date})"
