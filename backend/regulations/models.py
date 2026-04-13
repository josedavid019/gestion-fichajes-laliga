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
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS, default="active")
    date_start = models.DateField()
    date_end = models.DateField()
    annual_salary_eur = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )

    class Meta:
        db_table = "regulations_contract"

    def __str__(self):
        return f"Contrato {self.player} — {self.club}"


class RegulationDocument(models.Model):
    DOC_TYPES = [
        ("fifa_regulation", "FIFA"),
        ("laliga_regulation", "LaLiga"),
        ("financial_fair_play", "FFP"),
        ("other", "Otro"),
    ]
    title = models.CharField(max_length=255)
    doc_type = models.CharField(max_length=30, choices=DOC_TYPES)
    language = models.CharField(max_length=10, default="es")
    is_active = models.BooleanField(default=True)
    file_path = models.FileField(upload_to="regulations/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "regulations_document"

    def __str__(self):
        return self.title


class RegulationChunk(models.Model):
    document = models.ForeignKey(
        RegulationDocument, on_delete=models.CASCADE, related_name="chunks"
    )
    chunk_index = models.PositiveIntegerField()
    section_title = models.CharField(max_length=255, blank=True)
    content = models.TextField()
    embedding = models.JSONField(null=True, blank=True)  # vector semántico
    embedding_model = models.CharField(max_length=100, default="text-embedding-3-small")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "regulations_chunk"
        unique_together = ("document", "chunk_index")

    def __str__(self):
        return f"{self.document} — Chunk {self.chunk_index}"


class LegalQuery(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    question = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "regulations_legal_query"

    def __str__(self):
        return self.question[:80]
