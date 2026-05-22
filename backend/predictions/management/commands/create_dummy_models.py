from django.core.management.base import BaseCommand
from predictions.models import MLModel, MLPrediction
from players.models import Player
from datetime import datetime
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Create dummy models and predictions for injury risk and performance'

    def handle(self, *args, **options):
        self.stdout.write("[*] Creating dummy ML models...")

        # Create injury risk model
        injury_model, created = MLModel.objects.get_or_create(
            name='Injury Risk Prediction',
            model_type='injury_risk',
            defaults={
                'version': '1.0',
                'algorithm': 'XGBoost',
                'status': 'active',
                'file_path': 'injury_risk_model_dummy.pkl',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"[+] Created injury risk model (ID: {injury_model.id})"))
        else:
            self.stdout.write(f"[*] Injury risk model already exists (ID: {injury_model.id})")

        # Create performance model
        performance_model, created = MLModel.objects.get_or_create(
            name='Performance Prediction',
            model_type='performance',
            defaults={
                'version': '1.0',
                'algorithm': 'XGBoost',
                'status': 'active',
                'file_path': 'performance_model_dummy.pkl',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"[+] Created performance model (ID: {performance_model.id})"))
        else:
            self.stdout.write(f"[*] Performance model already exists (ID: {performance_model.id})")

        # Get first 5 players
        players = Player.objects.all()[:5]

        if not players:
            self.stdout.write(self.style.ERROR("[-] No players found"))
            return

        self.stdout.write(f"\n[*] Creating predictions for {len(players)} players...")

        for i, player in enumerate(players, 1):
            player_name = player.alias or f"{player.first_name} {player.last_name}"

            # Create injury risk prediction
            injury_pred, created = MLPrediction.objects.get_or_create(
                player=player,
                model=injury_model,
                defaults={
                    'predicted_value': Decimal(str(random.randint(20, 80))),  # Risk percentage
                    'confidence_score': Decimal(str(round(0.7 + random.random() * 0.25, 2))),
                    'shap_values': {
                        'risk_factors': ['age', 'minutes_played', 'injury_history', 'intensity'],
                        'timeline': 'Medio' if random.random() > 0.5 else 'Alto',
                    }
                }
            )
            if created:
                self.stdout.write(f"  [{i}/5] {player_name} - Injury: {injury_pred.predicted_value}%")

            # Create performance prediction
            perf_pred, created = MLPrediction.objects.get_or_create(
                player=player,
                model=performance_model,
                defaults={
                    'predicted_value': Decimal(str(random.randint(65, 95))),  # Performance score
                    'confidence_score': Decimal(str(round(0.75 + random.random() * 0.2, 2))),
                    'shap_values': {
                        'performance_factors': ['consistency', 'intensity', 'skill_level', 'form'],
                        'trend': 'Positiva' if random.random() > 0.4 else 'Negativa',
                    }
                }
            )
            if created:
                self.stdout.write(f"  [{i}/5] {player_name} - Performance: {perf_pred.predicted_value}")

        self.stdout.write(self.style.SUCCESS("\n[OK] Dummy models and predictions created successfully!"))
