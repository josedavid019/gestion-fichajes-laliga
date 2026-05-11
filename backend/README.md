# ⚽ Football Analytics Platform — Database Schema

## 📌 Overview

Esta base de datos soporta una plataforma avanzada de:

- Gestión de jugadores y clubes
- Analítica futbolística
- Predicción ML de valor de mercado
- RAG jurídico/deportivo
- Computer Vision aplicada al scouting
- Recomendaciones y scouting inteligente
- Historial contractual y transferencias

La arquitectura está diseñada para:

- PostgreSQL + pgvector
- Machine Learning pipelines
- Retrieval-Augmented Generation (RAG)
- Computer Vision
- Escalabilidad multi-módulo
- APIs REST/GraphQL

---

# 🧩 APPS

---

# 1. PLAYERS APP

Core principal del dominio futbolístico.

---

## Country

Catálogo de países.

| Campo    | Tipo      |
| -------- | --------- |
| name     | CharField |
| iso_code | CharField |
| flag_url | URLField  |

### Relaciones

- competitions
- clubs
- players

---

## Competition

Competiciones y torneos.

| Campo   | Tipo                              |
| ------- | --------------------------------- |
| name    | CharField                         |
| country | FK → Country                      |
| type    | league/cup/international/friendly |

---

## Season

Temporadas futbolísticas.

| Campo      | Tipo         |
| ---------- | ------------ |
| name       | CharField    |
| start_date | DateField    |
| end_date   | DateField    |
| is_current | BooleanField |

### Constraints

- Solo una temporada puede ser actual.

---

## Club

Clubes de fútbol.

| Campo        | Tipo         |
| ------------ | ------------ |
| name         | CharField    |
| country      | FK → Country |
| city         | CharField    |
| founded_year | IntegerField |
| stadium      | CharField    |
| budget       | DecimalField |
| logo_url     | URLField     |

---

## Player

Entidad principal del jugador.

| Campo            | Tipo               |
| ---------------- | ------------------ |
| first_name       | CharField          |
| last_name        | CharField          |
| alias            | CharField          |
| date_of_birth    | DateField          |
| nationality      | FK → Country       |
| current_club     | FK → Club          |
| shirt_number     | IntegerField       |
| height_cm        | IntegerField       |
| weight_kg        | IntegerField       |
| preferred_foot   | left/right/both    |
| status           | active/injured/etc |
| market_value_eur | DecimalField       |
| photo_url        | URLField           |
| face_embedding   | VectorField(512)   |
| external_id      | CharField          |

### Features

- Face recognition embeddings
- Estado deportivo
- Valor de mercado
- Relación con scouting y ML

---

## PlayerClubHistory

Historial de clubes.

| Campo        | Tipo        |
| ------------ | ----------- |
| player       | FK → Player |
| club         | FK → Club   |
| season       | FK → Season |
| date_from    | DateField   |
| date_to      | DateField   |
| loan         | Boolean     |
| transfer_fee | Decimal     |
| is_current   | Boolean     |

### Constraints

- Solo un club actual por jugador.

---

## SeasonPlayerStat

Estadísticas agregadas por temporada.

| Campo        | Tipo    |
| ------------ | ------- |
| player       | FK      |
| season       | FK      |
| club         | FK      |
| competition  | FK      |
| appearances  | Integer |
| minutes      | Integer |
| goals        | Integer |
| assists      | Integer |
| yellow_cards | Integer |
| red_cards    | Integer |
| avg_rating   | Decimal |

### Uso

- Features ML
- Analytics
- Dashboards

---

## PlayerPosition

Posiciones jugadas.

| Campo      | Tipo      |
| ---------- | --------- |
| player     | FK        |
| position   | CharField |
| is_primary | Boolean   |

---

## PlayerNationality

Múltiples nacionalidades.

| Campo   | Tipo |
| ------- | ---- |
| player  | FK   |
| country | FK   |

---

## ClubCompetition

Participación de clubes en competiciones.

| Campo       | Tipo |
| ----------- | ---- |
| club        | FK   |
| competition | FK   |
| season      | FK   |

---

## Match

Partidos.

| Campo       | Tipo               |
| ----------- | ------------------ |
| competition | FK                 |
| season      | FK                 |
| home_club   | FK                 |
| away_club   | FK                 |
| match_date  | DateTime           |
| home_score  | Integer            |
| away_score  | Integer            |
| status      | scheduled/live/etc |

### Constraints

- Un club no puede jugar contra sí mismo.

---

## PlayerMatchStat

Estadísticas individuales por partido.

| Campo          | Tipo    |
| -------------- | ------- |
| player         | FK      |
| match          | FK      |
| goals          | Integer |
| assists        | Integer |
| minutes_played | Integer |

---

## Injury

Lesiones.

| Campo       | Tipo                |
| ----------- | ------------------- |
| player      | FK                  |
| injury_type | muscle/fracture/etc |
| start_date  | Date                |
| end_date    | Date                |
| description | Text                |

---

## Suspension

Suspensiones.

| Campo             | Tipo      |
| ----------------- | --------- |
| player            | FK        |
| reason            | CharField |
| matches_suspended | Integer   |
| start_date        | Date      |
| end_date          | Date      |

---

# 2. PREDICTIONS APP

Sistema de Machine Learning y predicciones.

---

## MarketValue

Historial de valores de mercado.

| Campo       | Tipo                    |
| ----------- | ----------------------- |
| player      | FK                      |
| season      | FK                      |
| value       | Decimal                 |
| source      | transfermarkt/ml/manual |
| recorded_at | Date                    |

---

## MLModel

Registro de modelos ML.

| Campo       | Tipo             |
| ----------- | ---------------- |
| name        | CharField        |
| version     | CharField        |
| algorithm   | CharField        |
| model_type  | market_value/etc |
| status      | training/active  |
| file_path   | FileField        |
| description | Text             |

---

## FeatureSnapshot

Snapshots de features usadas por ML.

| Campo         | Tipo      |
| ------------- | --------- |
| player        | FK        |
| snapshot_data | JSONField |

---

## MLPrediction

Predicciones generadas.

| Campo            | Tipo    |
| ---------------- | ------- |
| player           | FK      |
| model            | FK      |
| predicted_value  | Decimal |
| shap_values      | JSON    |
| confidence_score | Decimal |

---

## ModelMetric

Métricas del modelo.

| Campo    | Tipo     |
| -------- | -------- |
| model    | OneToOne |
| mae      | Decimal  |
| rmse     | Decimal  |
| r2_score | Decimal  |

---

## TrainingRun

Ejecuciones de entrenamiento.

| Campo                 | Tipo              |
| --------------------- | ----------------- |
| model                 | FK                |
| started_at            | DateTime          |
| finished_at           | DateTime          |
| dataset_version       | CharField         |
| status                | running/completed |
| training_time_seconds | Integer           |
| samples_used          | Integer           |

---

# 3. REGULATIONS APP

Sistema jurídico + RAG.

---

## RegulationDocument

Documentos legales/regulatorios.

| Campo       | Tipo         |
| ----------- | ------------ |
| title       | CharField    |
| source      | CharField    |
| doc_type    | fifa/law/etc |
| category    | CharField    |
| version     | CharField    |
| language    | CharField    |
| file_path   | FileField    |
| uploaded_by | FK User      |

---

## RegulationChunk

Chunks vectorizados para RAG.

| Campo          | Tipo             |
| -------------- | ---------------- |
| document       | FK               |
| chunk_index    | Integer          |
| section_title  | CharField        |
| article_number | CharField        |
| content        | Text             |
| embedding      | VectorField(384) |

### Features

- Semantic search
- Retrieval pipelines
- Legal AI assistant

---

## LegalQuery

Consultas legales.

| Campo     | Tipo        |
| --------- | ----------- |
| user      | FK          |
| question  | Text        |
| embedding | VectorField |

---

## LegalAnswer

Respuesta generada por RAG.

| Campo            | Tipo     |
| ---------------- | -------- |
| query            | OneToOne |
| answer_text      | Text     |
| confidence_score | Decimal  |
| chunks_used      | Integer  |

---

## LegalSource

Fuentes usadas en respuestas.

| Campo           | Tipo    |
| --------------- | ------- |
| answer          | FK      |
| document        | FK      |
| chunk           | FK      |
| relevance_score | Decimal |

---

## EmbeddingCache

Cache de embeddings.

| Campo     | Tipo        |
| --------- | ----------- |
| text_hash | CharField   |
| text      | Text        |
| embedding | VectorField |

---

## Contract

Contratos de jugadores.

| Campo          | Tipo           |
| -------------- | -------------- |
| player         | FK             |
| club           | FK             |
| status         | active/expired |
| start_date     | Date           |
| end_date       | Date           |
| salary         | Decimal        |
| release_clause | Decimal        |
| agent          | FK             |

### Constraints

- Fecha final ≥ fecha inicial
- Solo un contrato activo por jugador

---

## Agent

Representantes/agentes.

| Campo     | Tipo      |
| --------- | --------- |
| full_name | CharField |
| agency    | CharField |
| phone     | CharField |

---

## ContractClause

Cláusulas contractuales.

| Campo       | Tipo               |
| ----------- | ------------------ |
| contract    | FK                 |
| clause_type | salary/release/etc |
| description | Text               |

---

# 4. SCOUTING APP

Scouting inteligente y recomendaciones.

---

## Transfer

Transferencias de jugadores.

| Campo         | Tipo               |
| ------------- | ------------------ |
| player        | FK                 |
| from_club     | FK                 |
| to_club       | FK                 |
| initiated_by  | FK User            |
| fee           | Decimal            |
| transfer_date | Date               |
| status        | pending/completed  |
| transfer_type | permanent/loan/etc |
| season        | FK                 |
| currency      | CharField          |

### Constraints

- No transferirse al mismo club.

---

## ScoutingReport

Reportes de scouting.

| Campo                | Tipo    |
| -------------------- | ------- |
| player               | FK      |
| scout                | FK User |
| club                 | FK      |
| strengths            | Text    |
| weaknesses           | Text    |
| recommendation       | Text    |
| rating               | Integer |
| potential_rating     | Integer |
| ready_for_first_team | Boolean |

---

## Shortlist

Listas de seguimiento.

| Campo       | Tipo      |
| ----------- | --------- |
| club        | FK        |
| created_by  | FK User   |
| name        | CharField |
| description | Text      |
| is_archived | Boolean   |

---

## ShortlistPlayer

Jugadores incluidos en shortlist.

| Campo     | Tipo    |
| --------- | ------- |
| shortlist | FK      |
| player    | FK      |
| priority  | Integer |

---

## PlayerComparison

Comparaciones entre jugadores.

| Campo           | Tipo |
| --------------- | ---- |
| player_a        | FK   |
| player_b        | FK   |
| comparison_data | JSON |

### Constraints

- No comparar mismo jugador consigo mismo.

---

## Recommendation

Sistema de recomendaciones.

| Campo            | Tipo      |
| ---------------- | --------- |
| player           | FK        |
| recommended_club | FK        |
| score            | Decimal   |
| confidence_score | Decimal   |
| reason           | Text      |
| model_version    | CharField |

---

# 5. VISION APP

Computer Vision y OCR.

---

## MediaUpload

Archivos multimedia procesados.

| Campo       | Tipo                 |
| ----------- | -------------------- |
| uploaded_by | FK User              |
| file_path   | FileField            |
| media_type  | image/video/document |
| source_type | sticker/manual/etc   |

---

## DetectionRun

Procesamiento de detección.

| Campo               | Tipo              |
| ------------------- | ----------------- |
| media_upload        | FK                |
| model_version       | CharField         |
| status              | pending/completed |
| total_objects_found | Integer           |
| processing_time_ms  | Integer           |

---

## DetectedObject

Objetos detectados.

| Campo          | Tipo            |
| -------------- | --------------- |
| detection_run  | FK              |
| player         | FK              |
| detected_class | player/face/etc |
| label          | CharField       |
| confidence     | Decimal         |
| bbox_x         | Integer         |
| bbox_y         | Integer         |
| bbox_width     | Integer         |
| bbox_height    | Integer         |

### Constraints

- Confidence entre 0 y 1
- Bounding boxes positivas

---

## OCRExtraction

Extracciones OCR.

| Campo          | Tipo            |
| -------------- | --------------- |
| media_upload   | FK              |
| field_type     | player_name/etc |
| extracted_text | Text            |
| confidence     | Decimal         |

---

## FaceMatch

Matching facial.

| Campo            | Tipo    |
| ---------------- | ------- |
| media_upload     | FK      |
| player           | FK      |
| similarity_score | Decimal |

---

## VisualReport

Reportes visuales generados.

| Campo        | Tipo |
| ------------ | ---- |
| media_upload | FK   |
| report_data  | JSON |
| summary      | Text |

---

# 🧠 MACHINE LEARNING FEATURES

## Modelos soportados

- Predicción valor de mercado
- Riesgo de lesión
- Recomendación de clubes
- Similaridad facial
- OCR extraction
- Player embeddings
- Semantic legal search

---

# 🔍 VECTOR SEARCH

La plataforma usa:

- PostgreSQL
- pgvector
- Embeddings semánticos
- Face embeddings
- Retrieval-Augmented Generation (RAG)

## Embeddings usados

| Uso                   | Dimensión |
| --------------------- | --------- |
| Face Recognition      | 512       |
| Legal Semantic Search | 384       |

---

# ⚙️ STACK TECNOLÓGICO

## Backend

- Django
- Django REST Framework
- PostgreSQL
- pgvector

## ML / AI

- Scikit-learn
- XGBoost
- SentenceTransformers
- OpenCV
- YOLO
- OCR
- SHAP

## Infraestructura

- Docker
- Celery
- Redis

---

# 📈 FUTURAS EXTENSIONES

- Event tracking por partido
- Tracking GPS
- Expected Goals (xG)
- Salary cap analytics
- Injury prediction avanzada
- Tactical analysis
- Multi-club tenancy
- Video embeddings
- LLM agents deportivos

---

# 🛡️ DATA INTEGRITY

La base de datos incluye:

- UniqueConstraints
- CheckConstraints
- Índices optimizados
- Relaciones normalizadas
- Validaciones de negocio
- Historial temporal
- Soft business rules

---

# 🚀 ESCALABILIDAD

Arquitectura preparada para:

- Millones de embeddings
- Pipelines ML distribuidos
- Procesamiento async
- APIs de alta concurrencia
- Búsqueda vectorial
- Dashboards analíticos
- Sistemas RAG
