"""
Script de diagnóstico RAG — cópialo en la raíz de tu proyecto Django
y ejecútalo con:

    python manage.py shell < test_rag.py

O interactivo:

    python manage.py shell
    >>> exec(open('test_rag.py').read())
"""

import sys, os

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

import json
import sys
import traceback
from django.conf import settings

SEP = "─" * 60
PASS = "✅"
FAIL = "❌"
WARN = "⚠️ "


def titulo(texto):
    print(f"\n{SEP}")
    print(f"  {texto}")
    print(SEP)


def ok(msg):
    print(f"  {PASS}  {msg}")


def err(msg):
    print(f"  {FAIL}  {msg}")


def warn(msg):
    print(f"  {WARN}  {msg}")


# ─────────────────────────────────────────────────────────────────
# TEST 1 — settings.py tiene RAG_API_URL
# ─────────────────────────────────────────────────────────────────
titulo("TEST 1 · settings.RAG_API_URL")

rag_url = getattr(settings, "RAG_API_URL", None)

if not rag_url:
    err("RAG_API_URL no está definida en settings.py")
    err("Añade:  RAG_API_URL = 'https://xxxx.ngrok-free.app'")
    sys.exit(1)
elif (
    "XXXX" in rag_url or "ngrok-free.app" not in rag_url and "localhost" not in rag_url
):
    warn(f"RAG_API_URL parece un placeholder: {rag_url}")
    warn("Asegúrate de haber copiado la URL real de Colab")
else:
    ok(f"RAG_API_URL = {rag_url}")


# ─────────────────────────────────────────────────────────────────
# TEST 2 — requests está instalado
# ─────────────────────────────────────────────────────────────────
titulo("TEST 2 · dependencias Python")

try:
    import requests

    ok(f"requests {requests.__version__}")
except ImportError:
    err("requests no está instalado — ejecuta:  pip install requests")
    sys.exit(1)

try:
    from rest_framework import VERSION as drf_version

    ok(f"djangorestframework {drf_version}")
except ImportError:
    err("djangorestframework no instalado — pip install djangorestframework")

try:
    import corsheaders

    ok("django-cors-headers instalado")
except ImportError:
    warn("django-cors-headers no instalado — pip install django-cors-headers")
    warn("Necesario para que React pueda llamar a Django")


# ─────────────────────────────────────────────────────────────────
# TEST 3 — /health del servidor Colab
# ─────────────────────────────────────────────────────────────────
titulo("TEST 3 · GET /health — servidor Colab")

try:
    r = requests.get(f"{rag_url.rstrip('/')}/health", timeout=10)
    r.raise_for_status()
    data = r.json()
    ok(f"Servidor responde — HTTP {r.status_code}")
    ok(f"Chunks cargados : {data.get('chunks', '?')}")
    ok(f"Documentos      : {data.get('docs', [])}")
    ok(f"Modelo embedding: {data.get('model', '?')}")
    ok(f"LLM             : {data.get('llm', '?')}")
    HEALTH_OK = True
except requests.exceptions.ConnectionError:
    err("No se puede conectar al servidor")
    err("→ ¿Está Colab corriendo? ¿ngrok activo?")
    HEALTH_OK = False
except requests.exceptions.Timeout:
    err("Timeout al conectar (10 s)")
    err("→ Colab puede estar en modo sleep")
    HEALTH_OK = False
except requests.exceptions.HTTPError as e:
    err(f"Error HTTP: {e}")
    HEALTH_OK = False
except Exception as e:
    err(f"Error inesperado: {e}")
    HEALTH_OK = False


# ─────────────────────────────────────────────────────────────────
# TEST 4 — POST /search (sin LLM, más rápido)
# ─────────────────────────────────────────────────────────────────
titulo("TEST 4 · POST /search — búsqueda semántica (sin LLM)")

if not HEALTH_OK:
    warn("Saltando — el servidor no responde")
else:
    try:
        payload = {"query": "límite salarial LaLiga", "top_k": 3}
        r = requests.post(
            f"{rag_url.rstrip('/')}/search",
            json=payload,
            timeout=20,
        )
        r.raise_for_status()
        data = r.json()
        resultados = data.get("results", [])
        ok(f"Chunks devueltos: {len(resultados)}")
        for i, chunk in enumerate(resultados, 1):
            score = chunk.get("score", 0)
            doc = chunk.get("doc_name", "?")
            preview = chunk.get("content", "")[:80].replace("\n", " ")
            print(f"\n  [{i}] score={score:.3f}  doc={doc}")
            print(f"       {preview}…")
        SEARCH_OK = len(resultados) > 0
        if not SEARCH_OK:
            warn(
                "El servidor respondió pero no devolvió chunks — ¿los PDFs están cargados?"
            )
    except Exception as e:
        err(f"Error en /search: {e}")
        SEARCH_OK = False


# ─────────────────────────────────────────────────────────────────
# TEST 5 — POST /rag (con LLM — puede tardar ~10 s)
# ─────────────────────────────────────────────────────────────────
titulo("TEST 5 · POST /rag — consulta completa con LLM (puede tardar ~15 s)")

if not HEALTH_OK:
    warn("Saltando — el servidor no responde")
else:
    try:
        payload = {
            "question": "¿Cuánto tiempo puede durar máximo un contrato de jugador profesional?",
            "top_k": 3,
        }
        print(f"  Pregunta: {payload['question']}")
        print("  Esperando respuesta del LLM...")

        r = requests.post(
            f"{rag_url.rstrip('/')}/rag",
            json=payload,
            timeout=40,
        )
        r.raise_for_status()
        data = r.json()

        answer = data.get("answer", "")
        chunks = data.get("chunks", [])

        if answer:
            ok(f"Respuesta recibida ({len(answer)} chars)")
            print(f"\n  ┌─ RESPUESTA ───────────────────────────────────")
            for line in answer[:500].split("\n"):
                print(f"  │ {line}")
            if len(answer) > 500:
                print(f"  │ ... (truncado)")
            print(f"  └───────────────────────────────────────────────")
        else:
            warn("El servidor respondió pero sin campo 'answer'")
            warn(f"Respuesta raw: {json.dumps(data)[:200]}")

        if chunks:
            ok(f"Fuentes devueltas: {len(chunks)}")
        else:
            warn("No se devolvieron chunks/fuentes")

        RAG_OK = bool(answer)

    except requests.exceptions.Timeout:
        err("Timeout (40 s) — Groq puede estar lento, inténtalo de nuevo")
        RAG_OK = False
    except Exception as e:
        err(f"Error en /rag: {e}")
        traceback.print_exc()
        RAG_OK = False


# ─────────────────────────────────────────────────────────────────
# TEST 6 — rag_client.py de Django funciona
# ─────────────────────────────────────────────────────────────────
titulo("TEST 6 · regulations.services.rag_client — capa Django")

try:
    from regulations.services.rag_client import rag_health, rag_query

    ok("Módulo importado correctamente")

    if HEALTH_OK:
        h = rag_health()
        ok(f"rag_health() OK — {h.get('chunks', '?')} chunks")
    else:
        warn("Saltando rag_health() — servidor no disponible")

except ImportError as e:
    err(f"No se puede importar rag_client: {e}")
    err("¿Existe el archivo regulations/services/rag_client.py?")
except Exception as e:
    err(f"Error ejecutando rag_client: {e}")


# ─────────────────────────────────────────────────────────────────
# TEST 7 — modelos de BD accesibles
# ─────────────────────────────────────────────────────────────────
titulo("TEST 7 · modelos de base de datos")

try:
    from regulations.models import (
        LegalQuery,
        LegalAnswer,
        LegalSource,
        RegulationDocument,
        RegulationChunk,
        EmbeddingCache,
    )

    ok("Todos los modelos importan sin error")

    counts = {
        "LegalQuery": LegalQuery.objects.count(),
        "LegalAnswer": LegalAnswer.objects.count(),
        "RegulationDocument": RegulationDocument.objects.count(),
        "RegulationChunk": RegulationChunk.objects.count(),
    }
    for model, n in counts.items():
        ok(f"{model}: {n} registros en BD")

except Exception as e:
    err(f"Error con modelos: {e}")
    err("¿Corriste python manage.py migrate?")


# ─────────────────────────────────────────────────────────────────
# TEST 8 — simular lo que hace la view ask()
# ─────────────────────────────────────────────────────────────────
titulo("TEST 8 · simulación completa view ask() — guarda en BD")

if not HEALTH_OK:
    warn("Saltando — el servidor RAG no responde")
else:
    try:
        from django.contrib.auth import get_user_model
        from regulations.models import LegalQuery, LegalAnswer, LegalSource
        from regulations.services.rag_client import rag_query as client_rag_query

        User = get_user_model()

        # Usar el primer superusuario disponible como usuario de prueba
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            user = User.objects.first()

        if not user:
            warn("No hay usuarios en BD — crea uno con createsuperuser")
            warn("El flujo de BD se saltará pero el RAG puede funcionar igual")
        else:
            ok(f"Usuario de prueba: {user.email}")

            pregunta = "¿Qué documentos necesita un club para inscribir a un jugador en LaLiga?"
            print(f"  Pregunta: {pregunta}")

            result = client_rag_query(pregunta, top_k=3)
            answer_text = result.get("answer", "")
            chunks = result.get("chunks", [])

            # Guardar en BD
            from django.db import transaction

            with transaction.atomic():
                lq = LegalQuery.objects.create(user=user, question=pregunta)
                la = LegalAnswer.objects.create(
                    query=lq,
                    answer_text=answer_text,
                    model_used=result.get("model", "llama3"),
                    confidence_score=chunks[0]["score"] if chunks else None,
                )
                for chunk in chunks:
                    LegalSource.objects.create(
                        answer=la,
                        document=None,
                        chunk=None,
                        relevance_score=chunk.get("score", 0),
                        source_text=chunk.get("content", "")[:500],
                    )

            ok(f"LegalQuery #{lq.id} creada")
            ok(f"LegalAnswer #{la.id} creada — {len(answer_text)} chars")
            ok(f"LegalSource  x{len(chunks)} creadas")
            ok("¡Flujo completo Django → Colab → BD funciona!")

    except Exception as e:
        err(f"Error en simulación: {e}")
        traceback.print_exc()


# ─────────────────────────────────────────────────────────────────
# RESUMEN
# ─────────────────────────────────────────────────────────────────
titulo("RESUMEN")
print(
    """
  Si todos los tests pasaron con ✅ puedes conectar React.

  Si alguno falló:
  ┌─ TEST 1/2  → problema de configuración local (settings / pip)
  ├─ TEST 3    → Colab no está corriendo o ngrok expiró
  ├─ TEST 4/5  → los PDFs no cargaron en Colab (re-corre las celdas)
  ├─ TEST 6    → falta el archivo regulations/services/rag_client.py
  ├─ TEST 7    → falta ejecutar  python manage.py migrate
  └─ TEST 8    → revisa el traceback arriba
"""
)
