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
        max_digits=14, decimal_places=2, required=False
    )
    confidence = serializers.FloatField(required=False)
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
