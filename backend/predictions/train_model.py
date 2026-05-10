import os
import django
import numpy as np
import pandas as pd
import joblib
from datetime import datetime
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import xgboost as xgb
from xgboost import XGBRegressor
import shap
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from players.models import Player, SeasonPlayerStat, Season
from regulations.models import Contract
from analytics.models import ClubFinancial
from predictions.models import MLModel


def load_training_data():
    """Carga datos de la BD y prepara features y target."""
    print("📊 Cargando datos de la BD...")

    # Obtener todas las estadísticas de temporadas
    stats = SeasonPlayerStat.objects.select_related(
        'player', 'season', 'club', 'player__current_club', 'player__nationality'
    ).all()

    if not stats.exists():
        raise ValueError("No hay datos en SeasonPlayerStat")

    data = []

    for stat in stats:
        player = stat.player

        # Filtrar: jugadores con < 5 apariciones (ruido)
        if stat.appearances < 5:
            continue

        # Obtener contrato vigente
        contract = player.contracts.filter(status='active').first()
        years_in_contract = 0
        annual_salary = 0
        if contract:
            if contract.date_end:
                years_in_contract = max(0, (contract.date_end - datetime.now().date()).days / 365)
            annual_salary = float(contract.annual_salary_eur or 0)

        # Obtener datos financieros del club
        club_financial = ClubFinancial.objects.filter(
            club=stat.club, season=stat.season
        ).first()
        wage_bill = 0
        revenue = 0
        if club_financial:
            wage_bill = float(club_financial.wage_bill_eur or 0)
            revenue = float(club_financial.total_revenue_eur or 0)

        # Calcular edad
        age = None
        if player.date_of_birth:
            today = datetime.now().date()
            age = (today - player.date_of_birth).days / 365.25

        # Verificar que tenemos valor de mercado (target)
        market_value = player.market_value_eur
        if not market_value:
            continue

        market_value_float = float(market_value)
        if market_value_float <= 0:
            continue

        # Construir registro
        record = {
            'player_id': player.id,
            'age': age if age else 25,  # Default si no hay fecha nacimiento
            'appearances': stat.appearances,
            'minutes': stat.minutes,
            'goals': stat.goals,
            'assists': stat.assists,
            'yellow_cards': stat.yellow_cards,
            'red_cards': stat.red_cards,
            'avg_rating': float(stat.avg_rating or 6.0),
            'height_cm': player.height_cm or 180,
            'weight_kg': player.weight_kg or 75,
            'position': player.position or 'unknown',
            'preferred_foot': player.preferred_foot or 'right',
            'nationality': str(player.nationality) if player.nationality else 'unknown',
            'club': stat.club.name if stat.club else 'unknown',
            'years_in_contract': years_in_contract,
            'annual_salary_eur': annual_salary,
            'club_wage_bill_eur': wage_bill,
            'club_revenue_eur': revenue,
            'market_value_eur': market_value_float,
        }

        # Calcular ratios de rendimiento
        if stat.minutes > 0:
            record['goals_per_90'] = (stat.goals / stat.minutes) * 90
            record['assists_per_90'] = (stat.assists / stat.minutes) * 90
            record['cards_per_90'] = (
                (stat.yellow_cards + stat.red_cards * 2) / stat.minutes
            ) * 90
            record['minutes_per_appearance'] = stat.minutes / max(stat.appearances, 1)
        else:
            record['goals_per_90'] = 0
            record['assists_per_90'] = 0
            record['cards_per_90'] = 0
            record['minutes_per_appearance'] = 0

        # Ratio económico
        if record['club_wage_bill_eur'] > 0:
            record['salary_to_revenue'] = (
                annual_salary / record['club_wage_bill_eur']
            )
        else:
            record['salary_to_revenue'] = 0

        data.append(record)

    df = pd.DataFrame(data)
    print(f"✓ Cargados {len(df)} registros de jugadores")
    print(f"✓ Rango de valores: €{df['market_value_eur'].min():,.0f} - €{df['market_value_eur'].max():,.0f}")

    return df


def feature_engineering(df):
    """Realiza feature engineering y preparación de datos."""
    print("\n🔧 Feature Engineering...")

    df = df.copy()

    # Normalizar posiciones a categorías estándar
    position_mapping = {
        'GK': ['Goalkeeper', 'GK', 'portero'],
        'DF': ['Defender', 'CB', 'LB', 'RB', 'DF', 'defensa'],
        'MF': ['Midfielder', 'CM', 'CAM', 'CDM', 'MF', 'centrocampista'],
        'FW': ['Forward', 'ST', 'CF', 'LW', 'RW', 'FW', 'delantero'],
    }

    def normalize_position(pos):
        if not pos or pos == 'unknown':
            return 'MF'
        pos_lower = str(pos).lower()
        for normalized, variants in position_mapping.items():
            if pos_lower in [v.lower() for v in variants]:
                return normalized
        return 'MF'  # Default a mediocampista

    df['position'] = df['position'].apply(normalize_position)

    # One-hot encoding para categorías
    df = pd.get_dummies(
        df,
        columns=['position', 'preferred_foot'],
        drop_first=False,
        prefix=['pos', 'foot']
    )

    # Normalizar nacionalidades a top 10 + 'Other'
    top_nationalities = df['nationality'].value_counts().head(10).index
    df['nationality'] = df['nationality'].apply(
        lambda x: x if x in top_nationalities else 'Other'
    )
    df = pd.get_dummies(df, columns=['nationality'], prefix='nat')

    # Features polinómicas
    df['age_squared'] = df['age'] ** 2
    df['rating_goals_interaction'] = df['avg_rating'] * df['goals_per_90']

    print(f"✓ Features finales: {df.shape[1]} columnas")
    print(f"✓ Features: {[c for c in df.columns if c not in ['player_id', 'market_value_eur', 'club']]}")

    return df


def train_model(df):
    """Entrena el modelo XGBoost."""
    print("\n🤖 Entrenando XGBoost...")

    # Separar features y target
    X = df.drop(columns=['player_id', 'market_value_eur', 'club'])
    y = df['market_value_eur']

    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"  Train: {len(X_train)} registros")
    print(f"  Test: {len(X_test)} registros")

    # Escalar features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Entrenar XGBoost
    model = XGBRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        verbosity=0,
    )

    model.fit(
        X_train_scaled, y_train,
        eval_set=[(X_test_scaled, y_test)],
        verbose=False,
    )

    # Evaluar
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

    y_pred = model.predict(X_test_scaled)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    print(f"\n📈 Métricas del modelo:")
    print(f"  MAE: €{mae:,.0f}")
    print(f"  RMSE: €{rmse:,.0f}")
    print(f"  R² Score: {r2:.4f}")

    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    print(f"\n🎯 Top 10 Features:")
    for idx, row in feature_importance.head(10).iterrows():
        print(f"  {row['feature']}: {row['importance']:.4f}")

    return model, scaler, X, feature_importance, (mae, rmse, r2)


def calculate_shap_values(model, X, scaler):
    """Calcula SHAP values para interpretabilidad."""
    print("\n💡 Calculando SHAP values...")

    X_scaled = scaler.transform(X)

    # Usar TreeExplainer para XGBoost
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_scaled)

    return shap_values, explainer


def save_model(model, scaler, feature_names, model_metadata):
    """Guarda el modelo y sus artefactos."""
    print("\n💾 Guardando modelo...")

    # Crear directorio si no existe
    model_dir = Path(__file__).parent / 'models_artifacts'
    model_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    model_path = model_dir / f'market_value_model_{timestamp}.pkl'
    scaler_path = model_dir / f'scaler_{timestamp}.pkl'

    joblib.dump(model, str(model_path))
    joblib.dump(scaler, str(scaler_path))
    joblib.dump(list(feature_names), str(model_dir / f'features_{timestamp}.pkl'))

    # Guardar metadatos en BD
    ml_model = MLModel.objects.create(
        name='Market Value Prediction',
        model_type='market_value',
        version='1.0',
        algorithm='XGBoost',
        status='active',
        file_path=str(model_path),
    )

    # Guardar metadata
    metadata = {
        'model_id': ml_model.id,
        'algorithm': 'XGBoost',
        'scaler_path': str(scaler_path),
        'features_path': str(model_dir / f'features_{timestamp}.pkl'),
        'timestamp': timestamp,
        'mae': model_metadata[0],
        'rmse': model_metadata[1],
        'r2_score': model_metadata[2],
    }

    print(f"✓ Modelo guardado en: {model_path}")
    print(f"✓ ID del modelo en BD: {ml_model.id}")

    return ml_model, metadata


def main():
    """Pipeline completo de entrenamiento."""
    print("=" * 60)
    print("🚀 ENTRENAMIENTO DE MODELO ML - PREDICCIÓN DE VALOR")
    print("=" * 60)

    try:
        # 1. Cargar datos
        df = load_training_data()

        # 2. Feature engineering
        df = feature_engineering(df)

        # 3. Entrenar modelo
        model, scaler, X, feature_importance, metrics = train_model(df)

        # 4. Calcular SHAP values
        shap_values, explainer = calculate_shap_values(model, X, scaler)

        # 5. Guardar modelo
        ml_model, metadata = save_model(
            model, scaler, X.columns, metrics
        )

        print("\n" + "=" * 60)
        print("✅ ENTRENAMIENTO COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        print(f"Modelo ID: {ml_model.id}")
        print(f"Algoritmo: {ml_model.algorithm}")
        print(f"R² Score: {metrics[2]:.4f}")

        return ml_model

    except Exception as e:
        print(f"\n❌ ERROR durante el entrenamiento: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == '__main__':
    main()
