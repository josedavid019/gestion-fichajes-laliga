from django.db import models
from players.models import Player, Club, Season
from accounts.models import User
from django.db.models import Q


class Transfer(models.Model):
    TRANSFER_STATUS = [
        ("pending", "Pending"),
        ("negotiating", "Negotiating"),
        ("agreed", "Agreed"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("failed", "Failed"),
    ]
    TRANSFER_TYPES = [
        ("permanent", "Permanent"),
        ("loan", "Loan"),
        ("free", "Free Transfer"),
        ("return_loan", "Return Loan"),
    ]
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="transfers"
    )
    from_club = models.ForeignKey(
        Club,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transfers_out",
    )
    to_club = models.ForeignKey(
        Club, on_delete=models.CASCADE, related_name="transfers_in"
    )
    initiated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transfers_initiated",
    )
    fee = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    transfer_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=TRANSFER_STATUS,
        default="pending",
    )
    transfer_type = models.CharField(
        max_length=20,
        choices=TRANSFER_TYPES,
        default="permanent",
    )
    season = models.ForeignKey(
        Season,
        on_delete=models.SET_NULL,
        null=True,
        related_name="transfers",
    )
    currency = models.CharField(max_length=3, default="EUR")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "scouting_transfer"
        ordering = ["-transfer_date"]
        constraints = [
            models.CheckConstraint(
                condition=~Q(from_club=models.F("to_club")),
                name="prevent_same_transfer_club",
            ),
            models.UniqueConstraint(
                fields=[
                    "player",
                    "from_club",
                    "to_club",
                    "transfer_date",
                ],
                name="unique_transfer_record",
            ),
        ]
        indexes = [
            models.Index(fields=["player"]),
            models.Index(fields=["transfer_date"]),
            models.Index(fields=["to_club"]),
            models.Index(fields=["from_club"]),
        ]

    def __str__(self):
        return f"{self.player} — {self.from_club} → {self.to_club}"


class ScoutingReport(models.Model):
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="scouting_reports"
    )
    scout = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="scouting_reports"
    )
    club = models.ForeignKey(
        Club, on_delete=models.SET_NULL, null=True, related_name="scouting_reports"
    )
    strengths = models.TextField()
    weaknesses = models.TextField()
    recommendation = models.TextField()
    rating = models.IntegerField(null=True, blank=True)
    position_fit = models.TextField()
    potential_rating = models.IntegerField(null=True, blank=True)
    ready_for_first_team = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "scouting_report"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Report {self.player} by {self.scout}"


class Shortlist(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="shortlists")
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="shortlists"
    )
    is_archived = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "scouting_shortlist"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.club})"


class ShortlistPlayer(models.Model):
    shortlist = models.ForeignKey(
        Shortlist, on_delete=models.CASCADE, related_name="players"
    )
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="shortlists"
    )
    added_at = models.DateTimeField(auto_now_add=True)
    priority = models.IntegerField(default=0)

    class Meta:
        db_table = "scouting_shortlist_player"
        constraints = [
            models.UniqueConstraint(
                fields=["shortlist", "player"],
                name="unique_shortlist_player",
            )
        ]
        indexes = [
            models.Index(fields=["shortlist"]),
            models.Index(fields=["player"]),
        ]

    def __str__(self):
        return f"{self.player} in {self.shortlist.name}"


class PlayerComparison(models.Model):
    player_a = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="comparisons_as_a"
    )
    player_b = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="comparisons_as_b"
    )
    comparison_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "scouting_player_comparison"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=~Q(player_a=models.F("player_b")),
                name="prevent_same_player_comparison",
            )
        ]
        indexes = [
            models.Index(fields=["player_a"]),
            models.Index(fields=["player_b"]),
        ]

    def __str__(self):
        return f"Comparison {self.player_a} vs {self.player_b}"


class Recommendation(models.Model):
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="recommendations"
    )
    recommended_club = models.ForeignKey(
        Club, on_delete=models.CASCADE, related_name="player_recommendations"
    )
    score = models.DecimalField(max_digits=5, decimal_places=4)
    reason = models.TextField()
    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        blank=True,
    )
    model_version = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "scouting_recommendation"
        ordering = ["-score", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["player", "recommended_club"],
                name="unique_player_club_recommendation",
            )
        ]
        indexes = [
            models.Index(fields=["player"]),
            models.Index(fields=["recommended_club"]),
            models.Index(fields=["score"]),
        ]

    def __str__(self):
        return f"{self.player} → {self.recommended_club} ({self.score})"
