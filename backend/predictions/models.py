from django.db import models
from players.models import Player, Season
from django.db.models import Q


class MarketValue(models.Model):
    SOURCES = [
        ("transfermarkt", "Transfermarkt"),
        ("ml_model", "Modelo ML"),
        ("manual", "Manual"),
    ]
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="market_values",
    )
    season = models.ForeignKey(
        Season,
        on_delete=models.SET_NULL,
        null=True,
        related_name="market_values",
    )
    value = models.DecimalField(max_digits=18, decimal_places=2)
    source = models.CharField(max_length=20, choices=SOURCES, default="transfermarkt")
    recorded_at = models.DateField()

    class Meta:
        db_table = "predictions_market_value"
        ordering = ["-recorded_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["player", "season", "recorded_at", "source"],
                name="unique_market_value_record",
            )
        ]
        indexes = [
            models.Index(fields=["player"]),
            models.Index(fields=["season"]),
            models.Index(fields=["recorded_at"]),
        ]

    def __str__(self):
        return f"{self.player} — €{self.value:,.0f}"


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
    version = models.CharField(max_length=20)
    algorithm = models.CharField(max_length=100, blank=True)
    model_type = models.CharField(max_length=20, choices=MODEL_TYPES)
    status = models.CharField(max_length=12, choices=STATUS, default="training")
    file_path = models.FileField(upload_to="models/", null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "predictions_ml_model"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "version"],
                name="unique_model_version",
            ),
            models.UniqueConstraint(
                fields=["model_type"],
                condition=Q(status="active"),
                name="unique_active_model_per_type",
            ),
        ]
        indexes = [
            models.Index(fields=["model_type", "status"]),
        ]

    def __str__(self):
        return f"{self.name} v{self.version}"


class FeatureSnapshot(models.Model):
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="feature_snapshots",
    )
    season = models.ForeignKey(
        Season,
        on_delete=models.SET_NULL,
        null=True,
        related_name="feature_snapshots",
    )
    snapshot_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "predictions_feature_snapshot"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Snapshot {self.player} — {self.created_at}"


class MLPrediction(models.Model):
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="ml_predictions",
    )
    model = models.ForeignKey(
        MLModel,
        on_delete=models.CASCADE,
        related_name="predictions",
    )
    season = models.ForeignKey(
        Season,
        on_delete=models.SET_NULL,
        null=True,
        related_name="ml_predictions",
    )
    predicted_value = models.DecimalField(max_digits=18, decimal_places=2)
    shap_values = models.JSONField(null=True, blank=True)
    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "predictions_ml_prediction"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["player"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["model", "created_at"]),
        ]

    def __str__(self):
        return f"Pred {self.player} — €{self.predicted_value:,.0f}"


class ModelMetric(models.Model):
    model = models.OneToOneField(
        MLModel,
        on_delete=models.CASCADE,
        related_name="metrics",
    )
    mae = models.DecimalField(max_digits=12, decimal_places=4)
    rmse = models.DecimalField(max_digits=12, decimal_places=4)
    r2_score = models.DecimalField(max_digits=12, decimal_places=4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "predictions_model_metric"

    def __str__(self):
        return f"Metrics {self.model}"


class TrainingRun(models.Model):
    STATUS = [
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]
    model = models.ForeignKey(
        MLModel, on_delete=models.CASCADE, related_name="training_runs"
    )
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField(null=True, blank=True)
    dataset_version = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="running",
    )
    final_mae = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
    )
    final_rmse = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
    )
    final_r2_score = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
    )
    training_time_seconds = models.IntegerField(null=True, blank=True)
    samples_used = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "predictions_training_run"
        ordering = ["-started_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(finished_at__gte=models.F("started_at"))
                | Q(finished_at__isnull=True),
                name="finished_after_started",
            )
        ]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["started_at"]),
        ]

    def __str__(self):
        return f"Training {self.model} — {self.dataset_version}"
