from django.db import models
from pgvector.django import VectorField
from players.models import Player, Club
from accounts.models import User
from django.db.models import Q


class RegulationDocument(models.Model):
    DOC_TYPES = [
        ("fifa_regulation", "FIFA"),
        ("laliga_regulation", "LaLiga"),
        ("financial", "Financiero"),
        ("law", "Ley"),
        ("other", "Otro"),
    ]
    title = models.CharField(max_length=255)
    source = models.CharField(max_length=255, blank=True)
    doc_type = models.CharField(max_length=30, choices=DOC_TYPES)
    category = models.CharField(max_length=100, blank=True)
    version = models.CharField(max_length=50, blank=True)
    published_date = models.DateField(null=True, blank=True)
    language = models.CharField(max_length=10, default="es")
    is_active = models.BooleanField(default=True)
    file_path = models.FileField(upload_to="regulations/", null=True, blank=True)
    external_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True,
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_regulations",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "regulations_document"
        constraints = [
            models.UniqueConstraint(
                fields=["title", "version"],
                name="unique_document_version",
            )
        ]
        indexes = [
            models.Index(fields=["doc_type"]),
            models.Index(fields=["category"]),
            models.Index(fields=["is_active"]),
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
    embedding = VectorField(dimensions=384, null=True, blank=True)
    embedding_model = models.CharField(
        max_length=100, default="paraphrase-multilingual-MiniLM-L12-v2"
    )
    is_useful = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "regulations_chunk"
        constraints = [
            models.UniqueConstraint(
                fields=["document", "chunk_index"],
                name="unique_document_chunk_index",
            )
        ]
        indexes = [
            models.Index(fields=["document"]),
            models.Index(fields=["article_number"]),
            models.Index(fields=["clause_type"]),
            models.Index(fields=["page"]),
            models.Index(fields=["is_useful"]),
            models.Index(fields=["document", "chunk_index"]),
            models.Index(fields=["document", "article_number"]),
        ]

    def __str__(self):
        return f"{self.document.title} — {self.article_number or f'chunk {self.chunk_index}'}"


class LegalQuery(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="legal_queries",
    )
    question = models.TextField()
    embedding = VectorField(dimensions=384, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "regulations_legal_query"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.question[:80]


class LegalAnswer(models.Model):
    query = models.OneToOneField(
        LegalQuery, on_delete=models.CASCADE, related_name="answer"
    )
    answer_text = models.TextField()
    model_used = models.CharField(max_length=100, default="rag")
    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        blank=True,
    )
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
    relevance_score = models.DecimalField(
        max_digits=5,
        decimal_places=4,
    )
    source_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "regulations_legal_source"
        ordering = ["-relevance_score"]
        indexes = [
            models.Index(fields=["answer"]),
            models.Index(fields=["document"]),
            models.Index(fields=["chunk"]),
        ]

    def __str__(self):
        return f"{self.doc_name or self.document} (score: {self.relevance_score:.3f})"


class EmbeddingCache(models.Model):
    text_hash = models.CharField(max_length=64, unique=True, null=True, blank=True)
    text = models.TextField()
    embedding = VectorField(dimensions=384)
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
    start_date = models.DateField()
    end_date = models.DateField()
    salary = models.DecimalField(max_digits=14, decimal_places=2)
    salary_currency = models.CharField(max_length=3, default="EUR")
    release_clause = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    agent = models.ForeignKey(
        "Agent",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contracts",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "regulations_contract"
        constraints = [
            models.CheckConstraint(
                condition=Q(end_date__gte=models.F("start_date")),
                name="contract_end_after_start",
            ),
            models.UniqueConstraint(
                fields=["player"],
                condition=Q(status="active"),
                name="unique_active_contract_per_player",
            ),
        ]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["end_date"]),
            models.Index(fields=["player"]),
            models.Index(fields=["club"]),
        ]

    def __str__(self):
        return f"Contrato {self.player} — {self.club} ({self.status})"


class Agent(models.Model):
    full_name = models.CharField(max_length=255)
    agency = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "regulations_agent"

    def __str__(self):
        return self.full_name


class ContractClause(models.Model):
    CLAUSE_TYPES = [
        ("salary", "Salary"),
        ("release", "Release Clause"),
        ("bonus", "Bonus"),
        ("duration", "Duration"),
        ("image_rights", "Image Rights"),
        ("other", "Other"),
    ]
    contract = models.ForeignKey(
        Contract, on_delete=models.CASCADE, related_name="clauses"
    )
    clause_type = models.CharField(max_length=100, choices=CLAUSE_TYPES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "regulations_contract_clause"
        indexes = [
            models.Index(fields=["contract"]),
            models.Index(fields=["clause_type"]),
        ]

    def __str__(self):
        return f"{self.contract} — {self.clause_type}"
