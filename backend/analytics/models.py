from django.db import models
from players.models import Player, Club, Season


class ClubFinancial(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    total_revenue_eur = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True
    )
    wage_bill_eur = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True
    )
    transfer_income_eur = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True
    )
    transfer_expenditure_eur = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True
    )
    net_debt_eur = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True
    )
    wage_to_revenue_ratio = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )

    class Meta:
        db_table = "analytics_club_financial"
        unique_together = ("club", "season")

    def __str__(self):
        return f"{self.club} — {self.season}"


class FinancialRule(models.Model):
    RULE_TYPES = [
        ("ffp", "Fair Play Financiero"),
        ("laliga_salary_cap", "Tope salarial LaLiga"),
        ("squad_registration", "Inscripción"),
        ("other", "Otra"),
    ]
    name = models.CharField(max_length=255)
    rule_type = models.CharField(max_length=30, choices=RULE_TYPES)
    description = models.TextField()
    threshold_eur = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True
    )
    threshold_ratio = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "analytics_financial_rule"

    def __str__(self):
        return self.name


class FinancialCheck(models.Model):
    RESULTS = [
        ("pass", "Cumple"),
        ("fail", "No cumple"),
        ("warning", "Advertencia"),
        ("pending", "Pendiente"),
    ]
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    rule = models.ForeignKey(FinancialRule, on_delete=models.SET_NULL, null=True)
    result = models.CharField(max_length=10, choices=RESULTS, default="pending")
    value_checked = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True
    )
    threshold_applied = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True
    )
    notes = models.TextField(blank=True)
    checked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "analytics_financial_check"

    def __str__(self):
        return f"{self.club} — {self.rule} — {self.result}"
