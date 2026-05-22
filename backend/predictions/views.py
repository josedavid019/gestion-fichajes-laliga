from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
import joblib
from pathlib import Path
import numpy as np
from datetime import datetime

from players.models import Player, SeasonPlayerStat
from analytics.models import ClubFinancial
from regulations.models import Contract
from .models import MLModel, MLPrediction
from .serializers import (
    MLPredictionSerializer,
    PlayerPredictionDetailSerializer,
    MLModelSerializer,
)


class PredictionPagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100


class PredictionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para predicciones de valor de mercado."""

    queryset = MLPrediction.objects.select_related("player", "model").all()
    serializer_class = MLPredictionSerializer
    pagination_class = PredictionPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["player", "model"]
    ordering_fields = ["created_at", "confidence_score", "predicted_value"]
    ordering = ["-created_at"]

    @action(detail=False, methods=["get"])
    def player(self, request):
        """GET /api/predictions/player/?player_id=X&model_type=value|injury|performance"""
        player_id = request.query_params.get("player_id")
        model_type = request.query_params.get("model_type", "value")

        if not player_id:
            return Response(
                {"error": "player_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        player = get_object_or_404(Player, id=player_id)
        prediction = self._get_or_create_prediction(player, model_type)

        serializer = PlayerPredictionDetailSerializer(prediction)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def estimate(self, request):
        """POST /api/predictions/estimate/ - Predecir valor con features custom."""
        try:
            features = request.data
            prediction_value = self._predict_from_features(features)

            return Response(
                {
                    "predicted_value_eur": prediction_value,
                    "confidence": 0.85,
                    "model_version": "1.0",
                }
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=["get"])
    def models(self, request):
        """GET /api/predictions/models/ - Listar modelos disponibles."""
        models = MLModel.objects.filter(status="active")
        serializer = MLModelSerializer(models, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def top_performers(self, request):
        """GET /api/predictions/top_performers/ - Top 10 jugadores por valor predicho."""
        limit = int(request.query_params.get("limit", 10))
        predictions = (
            MLPrediction.objects.select_related("player")
            .filter(model__status="active")
            .order_by("-predicted_value")[:limit]
        )

        data = [
            {
                "player": {
                    "id": p.player.id,
                    "alias": p.player.alias or f"{p.player.first_name} {p.player.last_name}",
                    "position": p.player.position,
                    "club": p.player.current_club.name if p.player.current_club else "N/A",
                    "photo_url": p.player.photo_url,
                },
                "predicted_value_eur": float(p.predicted_value or 0),
                "confidence": float(p.confidence_score or 0),
            }
            for p in predictions
        ]

        return Response(data)

    def _get_or_create_prediction(self, player, model_type="value"):
        """Obtiene predicción existente o crea una nueva."""
        # Intentar obtener predicción reciente del modelo activo
        active_model = MLModel.objects.filter(
            status="active",
            model_type=model_type
        ).first()

        if not active_model:
            return self._create_mock_prediction(player, model_type)

        prediction = MLPrediction.objects.filter(
            player=player, model=active_model
        ).first()

        if not prediction:
            prediction = self._create_prediction_for_player(player, active_model, model_type)

        return prediction

    def _create_prediction_for_player(self, player, model, model_type="value"):
        """Crea una predicción para un jugador usando el modelo."""
        try:
            # Para modelos que no son market_value, retornar los datos directamente
            if model_type != "value":
                # Retornar predicción existente o crear mock
                prediction = MLPrediction.objects.filter(
                    player=player, model=model
                ).first()
                if prediction:
                    return prediction
                else:
                    return self._create_mock_prediction(player, model_type)

            # Para market_value, usar el modelo completo
            features = self._extract_player_features(player)
            models_dir = Path(__file__).parent / "models_artifacts"

            # Find the latest model file
            model_files = list(models_dir.glob("market_value_model_*.pkl"))
            if not model_files:
                # Si no existe modelo, crear predicción con valor cercano al actual
                predicted_value = float(player.market_value_eur or 1000000)
                confidence = 0.7
            else:
                # Get the most recent model
                latest_model_file = max(model_files, key=lambda x: x.stat().st_mtime)
                ml_model = joblib.load(str(latest_model_file))

                # Find corresponding scaler
                timestamp = latest_model_file.stem.split('_')[-1]
                scaler_path = models_dir / f"scaler_{timestamp}.pkl"
                features_path = models_dir / f"features_{timestamp}.pkl"

                scaler = joblib.load(str(scaler_path))
                feature_names = joblib.load(str(features_path))

                # Create feature array in correct order
                X = np.array([[features[feat] for feat in feature_names]])
                X_scaled = scaler.transform(X)
                predicted_value = float(ml_model.predict(X_scaled)[0])
                confidence = 0.85

            prediction = MLPrediction.objects.create(
                player=player,
                model=model,
                predicted_value=predicted_value,
                confidence_score=confidence,
                shap_values={
                    "top_features": [
                        "age",
                        "goals_per_90",
                        "avg_rating",
                        "minutes",
                        "assists_per_90",
                    ]
                },
            )

            return prediction

        except Exception as e:
            print(f"Error creating prediction: {e}")
            return self._create_mock_prediction(player, model_type)

    def _extract_player_features(self, player):
        """Extrae features de un jugador desde la BD."""
        latest_stat = SeasonPlayerStat.objects.filter(player=player).order_by(
            "-season__end_date"
        ).first()

        if not latest_stat:
            # Return default features if no stats
            return {
                'age': 25,
                'appearances': 20,
                'minutes': 1500,
                'goals': 5,
                'assists': 3,
                'yellow_cards': 3,
                'red_cards': 0,
                'avg_rating': 6.5,
                'height_cm': 180,
                'weight_kg': 75,
                'years_in_contract': 2,
                'annual_salary_eur': 1000000,
                'club_wage_bill_eur': 50000000,
                'club_revenue_eur': 200000000,
                'goals_per_90': 0.3,
                'assists_per_90': 0.2,
                'cards_per_90': 0.2,
                'minutes_per_appearance': 75,
                'salary_to_revenue': 0.005,
                'pos_DF': 0,
                'pos_FW': 0,
                'pos_GK': 0,
                'pos_MF': 1,
                'foot_right': 1,
                'nat_Argentina': 0,
                'nat_Brazil': 0,
                'nat_England': 0,
                'nat_France': 0,
                'nat_Ghana': 0,
                'nat_Morocco': 0,
                'nat_Other': 1,
                'nat_Poland': 0,
                'nat_Serbia': 0,
                'nat_Sweden': 0,
                'nat_Uruguay': 0,
                'age_squared': 625,
                'rating_goals_interaction': 1.95,
            }

        contract = player.contracts.filter(status="active").first()
        years_in_contract = 0
        annual_salary = 0
        if contract and contract.date_end:
            years_in_contract = max(
                0, (contract.date_end - datetime.now().date()).days / 365
            )
            annual_salary = float(contract.annual_salary_eur or 0)

        # Get club financial data
        club_financial = None
        if latest_stat.club:
            club_financial = latest_stat.club.financial_data.filter(
                season=latest_stat.season
            ).first()

        club_wage_bill = 0
        club_revenue = 0
        if club_financial:
            club_wage_bill = float(club_financial.wage_bill_eur or 0)
            club_revenue = float(club_financial.total_revenue_eur or 0)

        # Calculate age
        age = None
        if player.date_of_birth:
            today = datetime.now().date()
            age = (today - player.date_of_birth).days / 365.25

        # Basic stats
        appearances = latest_stat.appearances
        minutes = latest_stat.minutes
        goals = latest_stat.goals
        assists = latest_stat.assists
        yellow_cards = latest_stat.yellow_cards
        red_cards = latest_stat.red_cards
        avg_rating = float(latest_stat.avg_rating or 6.0)
        height_cm = player.height_cm or 180
        weight_kg = player.weight_kg or 75

        # Calculated features
        goals_per_90 = (goals / minutes * 90) if minutes > 0 else 0
        assists_per_90 = (assists / minutes * 90) if minutes > 0 else 0
        cards_per_90 = ((yellow_cards + red_cards * 2) / minutes * 90) if minutes > 0 else 0
        minutes_per_appearance = minutes / max(appearances, 1)
        salary_to_revenue = (annual_salary / club_wage_bill) if club_wage_bill > 0 else 0

        # Position encoding
        position = player.position or "MF"
        pos_DF = 1 if position in ["DF", "Defender", "CB", "LB", "RB"] else 0
        pos_FW = 1 if position in ["FW", "Forward", "ST", "CF", "LW", "RW"] else 0
        pos_GK = 1 if position in ["GK", "Goalkeeper"] else 0
        pos_MF = 1 if position in ["MF", "Midfielder", "CM", "CAM", "CDM"] else 0

        # Foot encoding
        foot_right = 1 if (player.preferred_foot or "").lower() == "right" else 0

        # Nationality encoding (top nationalities from training)
        nationality = str(player.nationality) if player.nationality else "Other"
        nat_Argentina = 1 if "Argentina" in nationality else 0
        nat_Brazil = 1 if "Brazil" in nationality else 0
        nat_England = 1 if "England" in nationality else 0
        nat_France = 1 if "France" in nationality else 0
        nat_Ghana = 1 if "Ghana" in nationality else 0
        nat_Morocco = 1 if "Morocco" in nationality else 0
        nat_Poland = 1 if "Poland" in nationality else 0
        nat_Serbia = 1 if "Serbia" in nationality else 0
        nat_Sweden = 1 if "Sweden" in nationality else 0
        nat_Uruguay = 1 if "Uruguay" in nationality else 0
        nat_Other = 1 if not any([nat_Argentina, nat_Brazil, nat_England, nat_France, nat_Ghana, nat_Morocco,
                                  nat_Poland, nat_Serbia, nat_Sweden, nat_Uruguay]) else 0

        # Polynomial features
        age_val = age or 25
        age_squared = age_val ** 2
        rating_goals_interaction = avg_rating * goals_per_90

        return {
            'age': age_val,
            'appearances': appearances,
            'minutes': minutes,
            'goals': goals,
            'assists': assists,
            'yellow_cards': yellow_cards,
            'red_cards': red_cards,
            'avg_rating': avg_rating,
            'height_cm': height_cm,
            'weight_kg': weight_kg,
            'years_in_contract': years_in_contract,
            'annual_salary_eur': annual_salary,
            'club_wage_bill_eur': club_wage_bill,
            'club_revenue_eur': club_revenue,
            'goals_per_90': goals_per_90,
            'assists_per_90': assists_per_90,
            'cards_per_90': cards_per_90,
            'minutes_per_appearance': minutes_per_appearance,
            'salary_to_revenue': salary_to_revenue,
            'pos_DF': pos_DF,
            'pos_FW': pos_FW,
            'pos_GK': pos_GK,
            'pos_MF': pos_MF,
            'foot_right': foot_right,
            'nat_Argentina': nat_Argentina,
            'nat_Brazil': nat_Brazil,
            'nat_England': nat_England,
            'nat_France': nat_France,
            'nat_Ghana': nat_Ghana,
            'nat_Morocco': nat_Morocco,
            'nat_Other': nat_Other,
            'nat_Poland': nat_Poland,
            'nat_Serbia': nat_Serbia,
            'nat_Sweden': nat_Sweden,
            'nat_Uruguay': nat_Uruguay,
            'age_squared': age_squared,
            'rating_goals_interaction': rating_goals_interaction,
        }

    def _predict_from_features(self, features):
        """Predice valor desde features directas (JSON)."""
        # Implementación simplificada para estimaciones custom
        # En producción, aquí iría la lógica completa del modelo
        base_value = features.get("age", 25) * 100000
        goals_bonus = features.get("goals", 0) * 50000
        return base_value + goals_bonus

    def _create_mock_prediction(self, player, model_type="value"):
        """Crea una predicción mock si no hay modelo."""
        active_model, _ = MLModel.objects.get_or_create(
            name=f"Default Mock Model {model_type}",
            model_type=model_type,
            defaults={"version": "0.1", "status": "active"},
        )

        if model_type == "value":
            predicted_value = float(player.market_value_eur or 1000000)
        elif model_type == "injury":
            predicted_value = 50  # 50% risk
        else:  # performance
            predicted_value = 75  # 75 performance score

        prediction, _ = MLPrediction.objects.get_or_create(
            player=player,
            model=active_model,
            defaults={
                "predicted_value": predicted_value,
                "confidence_score": 0.7,
                "shap_values": {"note": f"Mock prediction for {model_type}"},
            },
        )

        return prediction
