from django.db import models
from players.models import Player, Club
from accounts.models import User


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

    class Meta:
        db_table = "regulations_contract"

    def __str__(self):
        return f"Contrato {self.player} — {self.club}"


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
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "regulations_document"
        indexes = [
            models.Index(fields=["doc_type"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return self.title


class RegulationChunk(models.Model):
    document = models.ForeignKey(
        RegulationDocument,
        on_delete=models.CASCADE,
        related_name="chunks",
    )

    chunk_index = models.PositiveIntegerField()
    section_title = models.CharField(max_length=255, blank=True)
    article_number = models.CharField(max_length=50, blank=True)
    clause_type = models.CharField(max_length=100, blank=True)
    content = models.TextField()
    embedding = models.JSONField(null=True, blank=True)
    embedding_model = models.CharField(max_length=100, default="all-MiniLM-L6-v2")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "regulations_chunk"
        unique_together = ("document", "chunk_index")
        indexes = [
            models.Index(fields=["document"]),
            models.Index(fields=["article_number"]),
            models.Index(fields=["clause_type"]),
        ]

    def __str__(self):
        return f"{self.document} — Artículo {self.article_number}"


class LegalQuery(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    question = models.TextField()
    embedding = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "regulations_legal_query"

    def __str__(self):
        return self.question[:80]


class LegalAnswer(models.Model):
    query = models.ForeignKey(
        LegalQuery,
        on_delete=models.CASCADE,
        related_name="answers",
    )

    answer_text = models.TextField()
    model_used = models.CharField(max_length=100, default="gpt")
    confidence_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "regulations_legal_answer"

    def __str__(self):
        return f"Respuesta a query {self.query.id}"


class LegalSource(models.Model):
    answer = models.ForeignKey(
        LegalAnswer,
        on_delete=models.CASCADE,
        related_name="sources",
    )

    # null=True en ambos FK porque cuando los PDFs no están indexados
    # en BD (vienen solo de Colab), no hay documento ni chunk local
    document = models.ForeignKey(
        RegulationDocument,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    chunk = models.ForeignKey(
        RegulationChunk,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    relevance_score = models.FloatField()
    source_text = models.TextField(blank=True)

    class Meta:
        db_table = "regulations_legal_source"
        # unique_together eliminado — falla cuando chunk=None con múltiples fuentes

    def __str__(self):
        return f"Fuente {self.document} (score: {self.relevance_score})"


class EmbeddingCache(models.Model):
    text = models.TextField(unique=True)
    embedding = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "regulations_embedding_cache"

    def __str__(self):
        return f"EmbeddingCache {self.id}"
