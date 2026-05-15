from rest_framework import serializers
from .models import (
    LegalQuery,
    LegalAnswer,
    LegalSource,
)

# ── fuentes ────────────────────────────────────────────────────────────────────


class LegalSourceSerializer(serializers.ModelSerializer):
    # LegalSource ya tiene doc_name y page como campos directos en el modelo,
    # así que los leemos de ahí. Si además hay FK a document/chunk, usamos
    # SerializerMethodField para no explotar cuando son None.
    doc_type = serializers.SerializerMethodField()
    chunk_text = serializers.SerializerMethodField()

    class Meta:
        model = LegalSource
        fields = [
            "id",
            "doc_name",  # CharField directo en el modelo
            "doc_type",
            "page",  # IntegerField directo en el modelo
            "relevance_score",
            "chunk_text",
            "source_text",
        ]

    def get_doc_type(self, obj):
        # document puede ser None (SET_NULL)
        if obj.document:
            return obj.document.doc_type
        return None

    def get_chunk_text(self, obj):
        # chunk puede ser None (SET_NULL)
        if obj.chunk:
            return obj.chunk.content
        return obj.source_text or None


# ── respuesta ──────────────────────────────────────────────────────────────────


class LegalAnswerSerializer(serializers.ModelSerializer):
    # LegalAnswer tiene OneToOneField desde LegalQuery, por lo que el
    # related_name es "answer" (singular), no "answers".
    # La relación inversa sources sí es ForeignKey → many.
    sources = LegalSourceSerializer(many=True, read_only=True)

    class Meta:
        model = LegalAnswer
        fields = [
            "id",
            "answer_text",
            "model_used",
            "confidence_score",
            "chunks_used",
            "created_at",
            "sources",
        ]


# ── consulta (list) ────────────────────────────────────────────────────────────


class LegalQueryListSerializer(serializers.ModelSerializer):
    # Incluir la respuesta completa cuando exista para que el frontend
    # pueda mostrar pregunta + respuesta sin volver a consultar al RAG.
    answer = LegalAnswerSerializer(read_only=True)

    class Meta:
        model = LegalQuery
        fields = ["id", "question", "created_at", "answer"]


# ── consulta (detail) ─────────────────────────────────────────────────────────


class LegalQueryDetailSerializer(serializers.ModelSerializer):
    # OneToOne: "answer" singular, wrapped en lista para que React
    # no tenga que cambiar de array a objeto.
    answer = LegalAnswerSerializer(read_only=True)

    class Meta:
        model = LegalQuery
        fields = ["id", "question", "created_at", "answer"]


# ── request body para /ask/ ───────────────────────────────────────────────────


class AskRequestSerializer(serializers.Serializer):
    question = serializers.CharField(min_length=5, max_length=2000)
    top_k = serializers.IntegerField(min_value=1, max_value=20, default=5)
