from django.db import models
from players.models import Player
from accounts.models import User


class MediaUpload(models.Model):
    MEDIA_TYPES = [("image", "Imagen"), ("video", "Video"), ("document", "Documento")]
    SOURCE_TYPES = [
        ("sticker", "Cromo"),
        ("press_photo", "Foto prensa"),
        ("match_video", "Video partido"),
        ("manual", "Manual"),
    ]
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to="vision/uploads/%Y/%m/")
    file_name = models.CharField(max_length=255)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    source_type = models.CharField(
        max_length=20, choices=SOURCE_TYPES, default="manual"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vision_media_upload"

    def __str__(self):
        return self.file_name


class DetectionRun(models.Model):
    STATUS = [
        ("pending", "Pendiente"),
        ("running", "Procesando"),
        ("completed", "Completado"),
        ("failed", "Fallido"),
    ]
    media_upload = models.ForeignKey(MediaUpload, on_delete=models.CASCADE)
    model_name = models.CharField(max_length=20, default="yolov8s")
    confidence_threshold = models.FloatField(default=0.5)
    status = models.CharField(max_length=10, choices=STATUS, default="pending")
    total_objects_found = models.PositiveSmallIntegerField(default=0)
    processing_time_ms = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vision_detection_run"

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
        DetectionRun, on_delete=models.CASCADE, related_name="detected_objects"
    )
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True)
    object_class = models.CharField(max_length=20, choices=CLASSES)
    confidence = models.FloatField()
    bbox_x = models.FloatField()
    bbox_y = models.FloatField()
    bbox_width = models.FloatField()
    bbox_height = models.FloatField()

    class Meta:
        db_table = "vision_detected_object"


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
    media_upload = models.ForeignKey(MediaUpload, on_delete=models.CASCADE)
    detection_run = models.ForeignKey(
        DetectionRun, on_delete=models.SET_NULL, null=True, blank=True
    )
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    raw_text = models.TextField()
    normalized_text = models.TextField(blank=True)
    confidence = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vision_ocr_extraction"
