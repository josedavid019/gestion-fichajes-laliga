import logging
from django.db import transaction, connection
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
)
from .serializers import (
    AskRequestSerializer,
    LegalQueryListSerializer,
    LegalQueryDetailSerializer,
)
from .services.rag_service import rag_query as local_rag_query

logger = logging.getLogger(__name__)


# ── /api/rag/ask/ ─────────────────────────────────────────────────────────────


@api_view(["POST"])
@permission_classes([AllowAny])
def ask(request):
    """
    Recibe { question, top_k } desde React.
    1. Valida el input.
    2. Ejecuta el pipeline RAG local (embeddings + pgvector + Groq).
    3. Persiste LegalQuery → LegalAnswer → LegalSource en BD.
    4. Devuelve la respuesta completa a React.
    """
    serializer = AskRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    question = serializer.validated_data["question"]
    top_k = serializer.validated_data["top_k"]

    # Crear y persistir la consulta antes de llamar al RAG, así se registra aunque falle
    legal_query = None
    try:
        legal_query = LegalQuery.objects.create(
            user=request.user if request.user.is_authenticated else None,
            question=question,
        )
    except Exception:
        logger.exception("No se pudo crear LegalQuery en BD")

    # ── pipeline RAG local ────────────────────────────────────────────────────
    try:
        rag_result = local_rag_query(question, top_k=top_k)
    except Exception as e:
        logger.exception("Error en pipeline RAG")
        return Response(
            {
                "error": f"Error interno del RAG: {str(e)}",
                "query_id": legal_query.id if legal_query else None,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    answer_text = rag_result["answer"]
    chunks = rag_result["chunks"]
    model_used = rag_result.get("model", "llama-3.1-8b-instant")

    # ── persistir respuesta y fuentes en BD (todo en una transacción) ────────
    try:
        with transaction.atomic():
            top_score = chunks[0]["score"] if chunks else None

            legal_answer = LegalAnswer.objects.create(
                query=legal_query,
                answer_text=answer_text,
                model_used=model_used,
                confidence_score=top_score,
                chunks_used=len(chunks),
            )

            sources_to_create = []
            for chunk in chunks:
                # Intentar vincular al documento real en BD
                doc = RegulationDocument.objects.filter(pk=chunk.get("doc_id")).first()

                # Intentar vincular al chunk real en BD
                db_chunk = RegulationChunk.objects.filter(
                    pk=chunk.get("chunk_id")
                ).first()

                sources_to_create.append(
                    LegalSource(
                        answer=legal_answer,
                        document=doc,
                        chunk=db_chunk,
                        doc_name=chunk.get("doc_name", ""),
                        page=chunk.get("page"),
                        relevance_score=chunk["score"],
                        source_text=chunk.get("content", ""),
                    )
                )

            if sources_to_create:
                LegalSource.objects.bulk_create(sources_to_create)

    except Exception:
        # Si falla la persistencia, no bloqueamos la respuesta al usuario
        logger.exception("Error al persistir la consulta RAG en BD")

    return Response(
        {
            "answer": answer_text,
            "chunks": chunks,
            "query_id": legal_query.id if legal_query else None,
        },
        status=status.HTTP_200_OK,
    )


# ── /api/rag/history/ ─────────────────────────────────────────────────────────


@api_view(["GET"])
@permission_classes([AllowAny])
def history(request):
    """Devuelve las últimas 50 consultas del usuario autenticado.

    Si la petición no está autenticada, devuelve lista vacía en lugar de 401.
    """
    if not request.user.is_authenticated:
        return Response([], status=status.HTTP_200_OK)

    # Build a base QuerySet (without prefetch) so we can log its SQL
    qs_base = LegalQuery.objects.filter(user=request.user).order_by("-created_at")[:50]

    # Log SQL for the main queries QuerySet
    try:
        logger.info("SQL history (queries): %s", str(qs_base.query))
    except Exception:
        logger.exception("No se pudo obtener SQL del queryset principal")

    # Force evaluation to obtain IDs used by related queries
    try:
        qs_list = list(qs_base)
    except Exception:
        qs_list = []

    # Log SQL for the answers that will be prefetched
    try:
        answers_qs = LegalAnswer.objects.filter(query__in=qs_base)
        logger.info("SQL history (answers): %s", str(answers_qs.query))
    except Exception:
        logger.exception("No se pudo obtener SQL para answers")

    # Log SQL for the sources that will be prefetched
    try:
        sources_qs = LegalSource.objects.filter(answer__in=answers_qs)
        logger.info("SQL history (sources): %s", str(sources_qs.query))
    except Exception:
        logger.exception("No se pudo obtener SQL para sources")

    # Use the original prefetch for response serialization
    queries = qs_base.prefetch_related("answer__sources")
    serializer = LegalQueryListSerializer(queries, many=True)
    return Response(serializer.data)


# ── /api/rag/history/<pk>/ ────────────────────────────────────────────────────


@api_view(["GET", "DELETE"])
@permission_classes([IsAuthenticated])
def history_detail(request, pk):
    """Devuelve el detalle completo de una consulta con sus fuentes.

    Además soporta DELETE para borrar una entrada del historial del usuario.
    """
    try:
        query = LegalQuery.objects.prefetch_related(
            "answer__sources__document",
            "answer__sources__chunk",
        ).get(pk=pk, user=request.user)
    except LegalQuery.DoesNotExist:
        return Response({"error": "No encontrado"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "DELETE":
        try:
            with transaction.atomic():
                query.delete()
            return Response({"ok": True}, status=status.HTTP_200_OK)
        except Exception:
            logger.exception("Error al borrar entry de historial")
            return Response(
                {"error": "No se pudo borrar"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    serializer = LegalQueryDetailSerializer(query)
    return Response(serializer.data)


# ── /api/rag/health/ ─────────────────────────────────────────────────────────


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    """Información mínima para que el frontend muestre estado del RAG."""
    try:
        total_chunks = RegulationChunk.objects.filter(is_useful=True).count()
    except Exception:
        total_chunks = None

    return Response(
        {"ok": True, "chunks": total_chunks, "model": "llama-3.1-8b-instant"}
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def clear_history(request):
    """Borra todo el historial del usuario autenticado."""
    try:
        with transaction.atomic():
            deleted, _ = LegalQuery.objects.filter(user=request.user).delete()
        return Response({"deleted": deleted}, status=status.HTTP_200_OK)
    except Exception:
        logger.exception("Error al borrar todo el historial")
        return Response(
            {"error": "No se pudo borrar"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
