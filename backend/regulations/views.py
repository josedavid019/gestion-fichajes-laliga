import requests
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import (
    LegalQuery,
    LegalAnswer,
    LegalSource,
    RegulationDocument,
    RegulationChunk,
    EmbeddingCache,
)
from .serializers import (
    AskRequestSerializer,
    LegalQueryListSerializer,
    LegalQueryDetailSerializer,
)
from .services.rag_client import rag_query, rag_health


# ── /api/rag/health/ ──────────────────────────────────────────────────────────


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    """Proxy al /health de Colab. Útil para que React verifique la conexión."""
    try:
        data = rag_health()
        return Response(data)
    except requests.exceptions.ConnectionError:
        return Response(
            {"error": "No se puede alcanzar el servidor RAG. ¿Está Colab corriendo?"},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)


# ── /api/rag/ask/ ─────────────────────────────────────────────────────────────


@api_view(["POST"])
@permission_classes([AllowAny])
def ask(request):
    """
    Recibe { question, top_k } desde React.
    1. Valida el input.
    2. Llama al RAG en Colab.
    3. Persiste LegalQuery → LegalAnswer → LegalSource en BD.
    4. Devuelve la respuesta completa a React.
    """
    serializer = AskRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    question = serializer.validated_data["question"]
    top_k = serializer.validated_data["top_k"]

    # ── llamada al RAG ────────────────────────────────────────────────────────
    try:
        rag_result = rag_query(question, top_k=top_k)
    except requests.exceptions.Timeout:
        return Response(
            {"error": "El servidor RAG tardó demasiado. Inténtalo de nuevo."},
            status=status.HTTP_504_GATEWAY_TIMEOUT,
        )
    except requests.exceptions.ConnectionError:
        return Response(
            {"error": "No se puede alcanzar el servidor RAG. ¿Está Colab corriendo?"},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    except requests.exceptions.HTTPError as e:
        return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

    answer_text = rag_result.get("answer", "")
    chunks = rag_result.get("chunks", [])

    # ── persistir en BD (todo en una transacción) ─────────────────────────────
    try:
        with transaction.atomic():
            legal_query = LegalQuery.objects.create(
                user=request.user,
                question=question,
            )

            # Calcula confidence como promedio del top score
            top_score = chunks[0]["score"] if chunks else None

            legal_answer = LegalAnswer.objects.create(
                query=legal_query,
                answer_text=answer_text,
                model_used=rag_result.get("model", "llama3"),
                confidence_score=top_score,
            )

            # Relacionar fuentes con documentos/chunks de BD si existen,
            # o guardar solo el texto si aún no están indexados.
            for chunk in chunks:
                doc_name = chunk.get("doc_name", "")
                page = chunk.get("page")
                content = chunk.get("content", "")
                score = chunk.get("score", 0.0)

                # Busca el documento en BD (por título aproximado)
                doc = RegulationDocument.objects.filter(
                    title__icontains=doc_name.replace(".pdf", "").strip()
                ).first()

                db_chunk = None
                if doc and page is not None:
                    db_chunk = RegulationChunk.objects.filter(
                        document=doc, chunk_index=page
                    ).first()

                LegalSource.objects.create(
                    answer=legal_answer,
                    document=doc,  # None si no está en BD
                    chunk=db_chunk,  # None si no está en BD
                    relevance_score=score,
                    source_text=content,
                )
    except Exception:
        # Si falla la BD no bloqueamos la respuesta al usuario
        pass

    # ── respuesta a React ──────────────────────────────────────────────────────
    return Response(
        {
            "answer": answer_text,
            "chunks": chunks,
            "query_id": legal_query.id if "legal_query" in dir() else None,
        }
    )


# ── /api/rag/history/ ─────────────────────────────────────────────────────────


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def history(request):
    """Devuelve las últimas 50 consultas del usuario autenticado."""
    queries = (
        LegalQuery.objects.filter(user=request.user)
        .prefetch_related("answers__sources")
        .order_by("-created_at")[:50]
    )
    serializer = LegalQueryListSerializer(queries, many=True)
    return Response(serializer.data)


# ── /api/rag/history/<pk>/ ────────────────────────────────────────────────────


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def history_detail(request, pk):
    """Devuelve el detalle completo de una consulta con sus fuentes."""
    try:
        query = LegalQuery.objects.prefetch_related(
            "answers__sources__document",
            "answers__sources__chunk",
        ).get(pk=pk, user=request.user)
    except LegalQuery.DoesNotExist:
        return Response({"error": "No encontrado"}, status=status.HTTP_404_NOT_FOUND)

    serializer = LegalQueryDetailSerializer(query)
    return Response(serializer.data)
