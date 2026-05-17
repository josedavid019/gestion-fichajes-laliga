from rest_framework import serializers
from players.serializers import PlayerSerializer
from .models import MLModel, MLPrediction


class MLModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLModel
        fields = [
            "id",
            "name",
            "model_type",
            "version",
            "algorithm",
            "status",
            "created_at",
        ]


class MLPredictionSerializer(serializers.ModelSerializer):
    predicted_value_eur = serializers.DecimalField(
        source="predicted_value",
        max_digits=18,
        decimal_places=2,
        read_only=True,
    )
    confidence = serializers.FloatField(
        source="confidence_score",
        read_only=True,
    )

    class Meta:
        model = MLPrediction
        fields = [
            "id",
            "player",
            "model",
            "predicted_value_eur",
            "confidence",
            "shap_values",
            "created_at",
        ]


class PlayerPredictionDetailSerializer(serializers.Serializer):
    """Combina datos del jugador con su predicción."""

    player = PlayerSerializer(read_only=True)
    predicted_value_eur = serializers.DecimalField(
        source="predicted_value",
        max_digits=18,
        decimal_places=2,
        required=False,
    )
    confidence = serializers.FloatField(
        source="confidence_score",
        required=False,
    )
    shap_values = serializers.JSONField(required=False)
    model_version = serializers.CharField(required=False)

    class Meta:
        fields = [
            "player",
            "predicted_value_eur",
            "confidence",
            "shap_values",
            "model_version",
        ]
