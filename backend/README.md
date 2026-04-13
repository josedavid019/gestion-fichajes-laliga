# Base de datos — GESTIÓN DE FICHAJES LA LIGA (Django)

## Estructura de archivos

```
django_models/
├── accounts/models.py          ← Usuarios, roles, auditoría
├── players/models.py           ← Jugadores, clubes, estadísticas
├── regulations/models.py       ← Contratos, cláusulas, RAG (LegalQuery/Answer)
├── vision/models.py            ← YOLO, OCR, reconocimiento facial
├── predictions/models.py       ← ML, valor de mercado, predicciones
├── scouting/models.py          ← Fichajes, shortlists, informes scouts
├── analytics/models.py         ← Fair Play Financiero + tablas Power BI
└── ENTREGA_MINIMA_models.py    ← Solo las tablas núcleo (para la próxima entrega)
```

---

## Resumen de tablas por entrega

### ✅ PRÓXIMA ENTREGA — Tablas mínimas (usar ENTREGA_MINIMA_models.py)

| App         | Tablas                                                                 |
| ----------- | ---------------------------------------------------------------------- |
| accounts    | User, Role, UserRole                                                   |
| players     | Country, Club, Season, Competition, Player                             |
| regulations | Contract, RegulationDocument, RegulationChunk, LegalQuery, LegalAnswer |
| vision      | MediaUpload, DetectionRun, DetectedObject, OCRExtraction               |
| predictions | MarketValue, MLModel, MLPrediction                                     |
| analytics   | ClubFinancial, FinancialRule, FinancialCheck                           |

**Total tablas mínimas: 21**

---

### 🔵 PROYECTO COMPLETO — Tablas adicionales

| App         | Tablas adicionales                                                                                                                                                            |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| accounts    | Profile, AuditLog                                                                                                                                                             |
| players     | PlayerPosition, PlayerNationality, PlayerClubHistory, ClubCompetition, Match, PlayerMatchStat, SeasonPlayerStat, Injury, Suspension                                           |
| regulations | Agent, ContractClause, LegalSource                                                                                                                                            |
| vision      | FaceMatch, VisualReport                                                                                                                                                       |
| predictions | FeatureSnapshot, ModelMetric, TrainingRun                                                                                                                                     |
| scouting    | Transfer, TransferStatus, ScoutingReport, Shortlist, ShortlistPlayer, PlayerComparison, Recommendation                                                                        |
| analytics   | SquadRegistration, DimensionPlayer, DimensionClub, DimensionCompetition, DimensionSeason, FactPlayerStat, FactMarketValue, FactTransfer, FactFinancialCheck, FactDetectionRun |

**Total tablas completas: 21 + 35 = 56 tablas**

---

## Configuración de Django (settings.py)

```python
INSTALLED_APPS = [
    # ...
    'accounts',
    'players',
    'regulations',
    'vision',
    'predictions',
    'scouting',
    'analytics',
]

AUTH_USER_MODEL = 'accounts.User'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'fichajes_laliga',
        'USER': 'postgres',
        'PASSWORD': 'tu_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

---

## Comandos de instalación

```bash
# 1. Instalar dependencias
pip install django djangorestframework psycopg2-binary Pillow

# 2. Crear las apps
python manage.py startapp accounts
python manage.py startapp players
python manage.py startapp regulations
python manage.py startapp vision
python manage.py startapp predictions
python manage.py startapp scouting
python manage.py startapp analytics

# 3. Copiar cada models.py en su carpeta correspondiente

# 4. Ejecutar migraciones
python manage.py makemigrations
python manage.py migrate

# 5. Crear superusuario
python manage.py createsuperuser
```

---

## Mapa de relaciones clave

```
User ──────────► UserRole ◄──── Role
User ──────────► AuditLog
User ──────────► LegalQuery ──► LegalAnswer

Country ───────► Club ◄──────── Player
Country ───────► Player (nacionalidad)
Country ───────► Competition

Player ─────────► MarketValue
Player ─────────► MLPrediction ◄─── MLModel
Player ─────────► Contract ◄──────── Club

MediaUpload ────► DetectionRun ──► DetectedObject ──► Player
MediaUpload ────► OCRExtraction
MediaUpload ────► FaceMatch ────► Player

RegulationDocument ──► RegulationChunk (embedding vectorial)
LegalQuery ──────────► LegalAnswer ──► LegalSource ──► RegulationChunk

ClubFinancial ──► FinancialCheck ◄── FinancialRule
                        │
                        └──► Player (verificación sub-23 / FFP)

── Power BI ─────────────────────────────────────────────────────────
DimensionPlayer + DimensionClub + DimensionSeason + DimensionCompetition
       │                │               │                  │
       └────────────────┴───────────────┴──────────────────┘
                                │
               ┌────────────────┼────────────────┐
               ▼                ▼                ▼
         FactPlayerStat  FactMarketValue    FactTransfer
         FactFinancialCheck  FactDetectionRun
```

---

## Notas importantes para la integración

### Power BI

- Conecta directamente a PostgreSQL con el conector nativo
- Las tablas `bi_dim_*` y `bi_fact_*` están desnormalizadas para rendimiento en BI
- Ejecuta un proceso ETL (celery beat / management command) para popular las tablas Fact/Dimension desde las tablas operacionales

### RAG (Regulations)

- El campo `embedding` en `RegulationChunk` guarda el vector semántico como JSON
- Para producción usar **pgvector** (`pip install pgvector`) y reemplazar JSONField por VectorField
- El flujo es: PDF → chunks → embedding (OpenAI/HuggingFace) → PostgreSQL

### YOLO / OCR

- `MediaUpload` recibe el archivo
- `DetectionRun` registra cada ejecución del modelo YOLO
- `DetectedObject` guarda bounding boxes
- `OCRExtraction` extrae texto de campos específicos (nombre, número, estadísticas)
- `FaceMatch` vincula el rostro detectado con un jugador de la DB

### ML Predicción de valor

- `FeatureSnapshot` construye el vector de entrada del modelo
- `MLPrediction` guarda el output + SHAP values para explicabilidad
- `ModelMetric` registra MAE, RMSE, R² para comparar versiones del modelo
