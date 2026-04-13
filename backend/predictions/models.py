from django.db import models
from players.models import Player, Season


class MarketValue(models.Model):
    SOURCES = [
        ("transfermarkt", "Transfermarkt"),
        ("ml_model", "Modelo ML"),
        ("manual", "Manual"),
    ]
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.SET_NULL, null=True)
    value_eur = models.DecimalField(max_digits=14, decimal_places=2)
    source = models.CharField(max_length=20, choices=SOURCES, default="transfermarkt")
    recorded_at = models.DateField()

    class Meta:
        db_table = "predictions_market_value"
        ordering = ["-recorded_at"]

    def __str__(self):
        return f"{self.player} — €{self.value_eur:,.0f}"


class MLModel(models.Model):
    MODEL_TYPES = [
        ("market_value", "Valor de mercado"),
        ("injury_risk", "Riesgo lesión"),
        ("performance", "Rendimiento"),
    ]
    STATUS = [
        ("training", "Entrenando"),
        ("active", "Activo"),
        ("deprecated", "Obsoleto"),
    ]
    name = models.CharField(max_length=150)
    model_type = models.CharField(max_length=20, choices=MODEL_TYPES)
    version = models.CharField(max_length=20)
    algorithm = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=12, choices=STATUS, default="training")
    file_path = models.FileField(upload_to="models/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "predictions_ml_model"
        unique_together = ("name", "version")

    def __str__(self):
        return f"{self.name} v{self.version}"


class MLPrediction(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE)
    predicted_value_eur = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    confidence = models.FloatField(null=True, blank=True)
    shap_values = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "predictions_ml_prediction"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Pred {self.player} — €{self.predicted_value_eur:,.0f}"
