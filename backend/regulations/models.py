from django.db import models
from pgvector.django import VectorField
from players.models import Player, Club
from accounts.models import User

EMBEDDING_DIM = 384


class RegulationDocument(models.Model):
    DOC_TYPES = [
        ("fifa_regulation", "FIFA"),
        ("laliga_regulation", "LaLiga"),
        ("financial", "Financiero"),
        ("law", "Ley"),
        ("other", "Otro"),
    ]
    title = models.CharField(max_length=255)
    doc_type = models.CharField(max_length=30, choices=DOC_TYPES)
    category = models.CharField(max_length=100, blank=True)
    version = models.CharField(max_length=50, blank=True)
    published_date = models.DateField(null=True, blank=True)
    language = models.CharField(max_length=10, default="es")
    is_active = models.BooleanField(default=True)
    file_path = models.FileField(upload_to="regulations/", null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    total_chunks = models.PositiveIntegerField(default=0)
    processing_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "regulations_document"
        indexes = [
            models.Index(fields=["doc_type"]),
            models.Index(fields=["category"]),
            models.Index(fields=["is_processed"]),
        ]

    def __str__(self):
        return self.title


class RegulationChunk(models.Model):
    document = models.ForeignKey(
        RegulationDocument, on_delete=models.CASCADE, related_name="chunks"
    )
    chunk_index = models.PositiveIntegerField()
    section_title = models.CharField(max_length=255, blank=True)
    article_number = models.CharField(max_length=50, blank=True)
    clause_type = models.CharField(max_length=100, blank=True)
    page = models.IntegerField(null=True, blank=True)
    content = models.TextField()
    embedding = VectorField(dimensions=EMBEDDING_DIM, null=True, blank=True)
    embedding_model = models.CharField(
        max_length=100, default="paraphrase-multilingual-MiniLM-L12-v2"
    )
    is_useful = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "regulations_chunk"
        unique_together = ("document", "chunk_index")
        indexes = [
            models.Index(fields=["document"]),
            models.Index(fields=["article_number"]),
            models.Index(fields=["clause_type"]),
            models.Index(fields=["page"]),
            models.Index(fields=["is_useful"]),
        ]

    def __str__(self):
        return f"{self.document.title} — {self.article_number or f'chunk {self.chunk_index}'}"


class LegalQuery(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    question = models.TextField()
    embedding = VectorField(dimensions=EMBEDDING_DIM, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "regulations_legal_query"
        ordering = ["-created_at"]

    def __str__(self):
        return self.question[:80]


class LegalAnswer(models.Model):
    query = models.OneToOneField(
        LegalQuery, on_delete=models.CASCADE, related_name="answer"
    )
    answer_text = models.TextField()
    model_used = models.CharField(max_length=100, default="rag")
    confidence_score = models.FloatField(null=True, blank=True)
    chunks_used = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "regulations_legal_answer"

    def __str__(self):
        return f"Respuesta a query {self.query_id}"


class LegalSource(models.Model):
    answer = models.ForeignKey(
        LegalAnswer, on_delete=models.CASCADE, related_name="sources"
    )
    document = models.ForeignKey(
        RegulationDocument, on_delete=models.SET_NULL, null=True, blank=True
    )
    chunk = models.ForeignKey(
        RegulationChunk, on_delete=models.SET_NULL, null=True, blank=True
    )
    doc_name = models.CharField(max_length=255, blank=True)
    page = models.IntegerField(null=True, blank=True)
    relevance_score = models.FloatField()
    source_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "regulations_legal_source"
        ordering = ["-relevance_score"]

    def __str__(self):
        return f"{self.doc_name or self.document} (score: {self.relevance_score:.3f})"


class EmbeddingCache(models.Model):
    """
    Caché de embeddings para no llamar al modelo dos veces
    con el mismo texto. Útil para queries repetidas.
    """

    text_hash = models.CharField(max_length=64, unique=True)
    text = models.TextField()
    embedding = VectorField(dimensions=EMBEDDING_DIM)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "regulations_embedding_cache"

    def __str__(self):
        return f"Cache [{self.text[:50]}]"


class Contract(models.Model):
    STATUS = [
        ("active", "Activo"),
        ("expired", "Expirado"),
        ("terminated", "Rescindido"),
        ("pending", "Pendiente"),
    ]
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="contracts"
    )
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="contracts")
    status = models.CharField(max_length=20, choices=STATUS, default="active")
    date_start = models.DateField()
    date_end = models.DateField()
    annual_salary_eur = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "regulations_contract"
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["date_end"]),
        ]

    def __str__(self):
        return f"Contrato {self.player} — {self.club} ({self.status})"
