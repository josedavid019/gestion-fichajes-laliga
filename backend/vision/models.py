from django.db import models
from players.models import Player
from accounts.models import User
from django.db.models import Q


class MediaUpload(models.Model):
    MEDIA_TYPES = [
        ("image", "Imagen"),
        ("video", "Video"),
        ("document", "Documento"),
    ]

    SOURCE_TYPES = [
        ("sticker", "Cromo"),
        ("press_photo", "Foto prensa"),
        ("match_video", "Video partido"),
        ("manual", "Manual"),
    ]

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="media_uploads",
    )

    file_path = models.FileField(upload_to="vision/uploads/")
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)

    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_TYPES,
        default="manual",
    )

    external_id = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "vision_media_upload"

        indexes = [
            models.Index(fields=["media_type"]),
            models.Index(fields=["source_type"]),
            models.Index(fields=["uploaded_at"]),
        ]

    def __str__(self):
        return str(self.file_path)


class DetectionRun(models.Model):
    STATUS = [
        ("pending", "Pendiente"),
        ("running", "Procesando"),
        ("completed", "Completado"),
        ("failed", "Fallido"),
    ]

    media_upload = models.ForeignKey(
        MediaUpload,
        on_delete=models.CASCADE,
        related_name="detection_runs",
    )

    model_version = models.CharField(max_length=100)

    status = models.CharField(
        max_length=10,
        choices=STATUS,
        default="pending",
    )

    total_objects_found = models.PositiveSmallIntegerField(default=0)

    processing_time_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    error_message = models.TextField(blank=True)

    processed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vision_detection_run"

        ordering = ["-processed_at"]

        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["processed_at"]),
        ]

    def __str__(self):
        return f"Run [{self.id}] — {self.status}"


class DetectedObject(models.Model):
    CLASSES = [
        ("player", "Jugador"),
        ("face", "Rostro"),
        ("ball", "Balón"),
        ("jersey", "Camiseta"),
        ("text_region", "Texto"),
        ("other", "Otro"),
    ]

    detection_run = models.ForeignKey(
        DetectionRun,
        on_delete=models.CASCADE,
        related_name="detected_objects",
    )

    player = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="detected_objects",
    )

    detected_class = models.CharField(
        max_length=20,
        choices=CLASSES,
    )

    label = models.CharField(max_length=100)

    confidence = models.DecimalField(
        max_digits=5,
        decimal_places=4,
    )

    bbox_x = models.PositiveIntegerField()
    bbox_y = models.PositiveIntegerField()
    bbox_width = models.PositiveIntegerField()
    bbox_height = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vision_detected_object"

        constraints = [
            models.CheckConstraint(
                condition=Q(confidence__gte=0) & Q(confidence__lte=1),
                name="detected_object_confidence_range",
            ),
            models.CheckConstraint(
                condition=Q(bbox_width__gt=0) & Q(bbox_height__gt=0),
                name="detected_object_positive_bbox",
            ),
        ]

        indexes = [
            models.Index(fields=["detected_class"]),
            models.Index(fields=["confidence"]),
        ]

    def __str__(self):
        return f"{self.label} — {self.confidence}"


class OCRExtraction(models.Model):
    FIELD_TYPES = [
        ("player_name", "Nombre"),
        ("jersey_number", "Número"),
        ("club_name", "Club"),
        ("position", "Posición"),
        ("birth_date", "Fecha nac."),
        ("market_value", "Valor"),
        ("other", "Otro"),
    ]

    media_upload = models.ForeignKey(
        MediaUpload,
        on_delete=models.CASCADE,
        related_name="ocr_extractions",
    )

    field_type = models.CharField(
        max_length=30,
        choices=FIELD_TYPES,
        default="other",
    )

    extracted_text = models.TextField()

    confidence = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vision_ocr_extraction"

        indexes = [
            models.Index(fields=["field_type"]),
        ]

    def __str__(self):
        return f"OCR — {self.media_upload}"


class FaceMatch(models.Model):
    media_upload = models.ForeignKey(
        MediaUpload,
        on_delete=models.CASCADE,
        related_name="face_matches",
    )

    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="face_matches",
    )

    similarity_score = models.DecimalField(
        max_digits=5,
        decimal_places=4,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vision_face_match"

        ordering = ["-similarity_score"]

        constraints = [
            models.CheckConstraint(
                condition=Q(similarity_score__gte=0) & Q(similarity_score__lte=1),
                name="face_match_similarity_range",
            )
        ]

        indexes = [
            models.Index(fields=["similarity_score"]),
            models.Index(fields=["player"]),
        ]

    def __str__(self):
        return f"{self.player} — {self.similarity_score}"


class VisualReport(models.Model):
    media_upload = models.ForeignKey(
        MediaUpload,
        on_delete=models.CASCADE,
        related_name="visual_reports",
    )

    report_data = models.JSONField()

    summary = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vision_visual_report"

        ordering = ["-created_at"]

    def __str__(self):
        return f"Report {self.media_upload} — {self.created_at}"
