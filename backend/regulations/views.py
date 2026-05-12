import logging

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

    # ── pipeline RAG local ────────────────────────────────────────────────────
    try:
        rag_result = local_rag_query(question, top_k=top_k)
    except Exception as e:
        logger.exception("Error en pipeline RAG")
        return Response(
            {"error": f"Error interno del RAG: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    answer_text = rag_result["answer"]
    chunks = rag_result[
        "chunks"
    ]  # lista de dicts con doc_id, score, content, page, doc_name
    model_used = rag_result.get("model", "llama-3.1-8b-instant")

    # ── persistir en BD (todo en una transacción) ─────────────────────────────
    legal_query = None
    legal_answer = None

    try:
        with transaction.atomic():
            legal_query = LegalQuery.objects.create(
                user=request.user if request.user.is_authenticated else None,
                question=question,
            )

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
@permission_classes([IsAuthenticated])
def history(request):
    """Devuelve las últimas 50 consultas del usuario autenticado."""
    queries = (
        LegalQuery.objects.filter(user=request.user)
        .prefetch_related("answer__sources")
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
            "answer__sources__document",
            "answer__sources__chunk",
        ).get(pk=pk, user=request.user)
    except LegalQuery.DoesNotExist:
        return Response(
            {"error": "No encontrado"},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = LegalQueryDetailSerializer(query)
    return Response(serializer.data)
