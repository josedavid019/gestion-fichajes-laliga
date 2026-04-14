from rest_framework import serializers
from .models import (
    LegalQuery,
    LegalAnswer,
    LegalSource,
    RegulationDocument,
    RegulationChunk,
)


# ── fuentes ────────────────────────────────────────────────────────────────────


class LegalSourceSerializer(serializers.ModelSerializer):
    doc_name = serializers.CharField(source="document.title", read_only=True)
    doc_type = serializers.CharField(source="document.doc_type", read_only=True)
    chunk_text = serializers.CharField(source="chunk.content", read_only=True)
    page = serializers.IntegerField(source="chunk.chunk_index", read_only=True)

    class Meta:
        model = LegalSource
        fields = [
            "id",
            "doc_name",
            "doc_type",
            "page",
            "relevance_score",
            "chunk_text",
            "source_text",
        ]


# ── respuesta ──────────────────────────────────────────────────────────────────


class LegalAnswerSerializer(serializers.ModelSerializer):
    sources = LegalSourceSerializer(many=True, read_only=True)

    class Meta:
        model = LegalAnswer
        fields = [
            "id",
            "answer_text",
            "model_used",
            "confidence_score",
            "created_at",
            "sources",
        ]


# ── consulta (list) ────────────────────────────────────────────────────────────


class LegalQueryListSerializer(serializers.ModelSerializer):
    answers_count = serializers.IntegerField(source="answers.count", read_only=True)

    class Meta:
        model = LegalQuery
        fields = ["id", "question", "created_at", "answers_count"]


# ── consulta (detail) ─────────────────────────────────────────────────────────


class LegalQueryDetailSerializer(serializers.ModelSerializer):
    answers = LegalAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = LegalQuery
        fields = ["id", "question", "created_at", "answers"]


# ── request body para /ask/ ───────────────────────────────────────────────────


class AskRequestSerializer(serializers.Serializer):
    question = serializers.CharField(min_length=5, max_length=2000)
    top_k = serializers.IntegerField(min_value=1, max_value=20, default=5)
