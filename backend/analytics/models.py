from django.db import models
from players.models import Player, Club, Season


class ClubFinancial(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    revenue = models.DecimalField(max_digits=18, decimal_places=2)
    expenses = models.DecimalField(max_digits=18, decimal_places=2)
    wage_bill = models.DecimalField(max_digits=18, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "analytics_club_financial"
        constraints = [
            models.UniqueConstraint(
                fields=["club", "season"], name="unique_club_season_financial"
            )
        ]

    def __str__(self):
        return f"{self.club} — {self.season}"


class FinancialRule(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    threshold = models.DecimalField(max_digits=18, decimal_places=2)
    rule_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "analytics_financial_rule"

    def __str__(self):
        return self.name


class FinancialCheck(models.Model):
    club_financial = models.ForeignKey(ClubFinancial, on_delete=models.CASCADE)
    rule = models.ForeignKey(FinancialRule, on_delete=models.CASCADE)
    passed = models.BooleanField()
    checked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "analytics_financial_check"

    def __str__(self):
        return f"{self.club_financial} — {self.rule} — {self.passed}"


class SquadRegistration(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "analytics_squad_registration"
        constraints = [
            models.UniqueConstraint(
                fields=["club", "player", "season"], name="unique_squad_registration"
            )
        ]

    def __str__(self):
        return f"{self.player} — {self.club} — {self.season}"


class DimensionPlayer(models.Model):
    player_key = models.CharField(max_length=100, unique=True)
    player_name = models.CharField(max_length=255)
    nationality = models.CharField(max_length=100)
    age = models.IntegerField()
    position = models.CharField(max_length=50)

    class Meta:
        db_table = "dw_dimension_player"

    def __str__(self):
        return self.player_name


class DimensionClub(models.Model):
    club_key = models.CharField(max_length=100, unique=True)
    club_name = models.CharField(max_length=255)
    country = models.CharField(max_length=100)

    class Meta:
        db_table = "dw_dimension_club"

    def __str__(self):
        return self.club_name


class DimensionCompetition(models.Model):
    competition_key = models.CharField(max_length=100, unique=True)
    competition_name = models.CharField(max_length=255)

    class Meta:
        db_table = "dw_dimension_competition"

    def __str__(self):
        return self.competition_name


class DimensionSeason(models.Model):
    season_key = models.CharField(max_length=100, unique=True)
    season_name = models.CharField(max_length=100)

    class Meta:
        db_table = "dw_dimension_season"

    def __str__(self):
        return self.season_name


class FactPlayerStat(models.Model):
    player_key = models.CharField(max_length=100)
    season_key = models.CharField(max_length=100)
    competition_key = models.CharField(max_length=100)
    goals = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    matches = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "dw_fact_player_stat"
        indexes = [
            models.Index(fields=["player_key"]),
            models.Index(fields=["season_key"]),
            models.Index(fields=["competition_key"]),
            models.Index(fields=["player_key", "season_key"]),
        ]

    def __str__(self):
        return f"{self.player_key} — {self.season_key}"


class FactMarketValue(models.Model):
    player_key = models.CharField(max_length=100)
    season_key = models.CharField(max_length=100)
    market_value = models.DecimalField(max_digits=18, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "dw_fact_market_value"
        indexes = [
            models.Index(fields=["player_key"]),
            models.Index(fields=["season_key"]),
            models.Index(fields=["player_key", "season_key"]),
        ]

    def __str__(self):
        return f"{self.player_key} — {self.market_value}"


class FactTransfer(models.Model):
    player_key = models.CharField(max_length=100)
    from_club_key = models.CharField(max_length=100, null=True, blank=True)
    to_club_key = models.CharField(max_length=100)
    fee = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    transfer_date = models.DateField()
    season_key = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "dw_fact_transfer"
        indexes = [
            models.Index(fields=["player_key"]),
            models.Index(fields=["from_club_key"]),
            models.Index(fields=["to_club_key"]),
            models.Index(fields=["season_key"]),
            models.Index(fields=["transfer_date"]),
        ]

    def __str__(self):
        return f"{self.player_key} — {self.from_club_key} → {self.to_club_key}"


class FactFinancialCheck(models.Model):
    club_key = models.CharField(max_length=100)
    rule_key = models.CharField(max_length=100)
    passed = models.BooleanField()
    checked_at = models.DateTimeField()
    season_key = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "dw_fact_financial_check"
        indexes = [
            models.Index(fields=["club_key"]),
            models.Index(fields=["rule_key"]),
            models.Index(fields=["season_key"]),
        ]

    def __str__(self):
        return f"{self.club_key} — {self.rule_key} — {self.passed}"


class FactDetectionRun(models.Model):
    media_key = models.CharField(max_length=100)
    detections = models.IntegerField()
    avg_confidence = models.DecimalField(max_digits=5, decimal_places=4)
    model_version = models.CharField(max_length=100)
    processing_time_ms = models.IntegerField()
    detected_players = models.IntegerField()
    season_key = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "dw_fact_detection_run"
        indexes = [
            models.Index(fields=["media_key"]),
            models.Index(fields=["season_key"]),
        ]

    def __str__(self):
        return f"{self.media_key} — {self.detections} detections"
