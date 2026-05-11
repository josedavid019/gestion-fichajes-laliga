from django.contrib import admin

from .models import (
    DetectionRun,
    DetectedObject,
    MediaUpload,
    OCRExtraction,
    FaceMatch,
    VisualReport,
)


@admin.register(MediaUpload)
class MediaUploadAdmin(admin.ModelAdmin):
    list_display = ("id", "file_path", "media_type", "source_type", "uploaded_at")
    search_fields = ("file_path",)
    list_filter = ("media_type", "source_type", "uploaded_at")


@admin.register(DetectionRun)
class DetectionRunAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "media_upload",
        "model_version",
        "status",
        "total_objects_found",
        "processed_at",
    )
    list_filter = ("status", "model_version", "processed_at")


@admin.register(DetectedObject)
class DetectedObjectAdmin(admin.ModelAdmin):
    list_display = ("id", "detection_run", "label", "confidence", "player")
    list_filter = ("label",)


@admin.register(OCRExtraction)
class OCRExtractionAdmin(admin.ModelAdmin):
    list_display = ("id", "media_upload", "extracted_text", "confidence")
    search_fields = ("extracted_text",)


@admin.register(FaceMatch)
class FaceMatchAdmin(admin.ModelAdmin):
    list_display = ("id", "media_upload", "player", "similarity_score", "created_at")
    search_fields = ("player__first_name", "player__last_name")
    list_filter = ("similarity_score", "created_at")


@admin.register(VisualReport)
class VisualReportAdmin(admin.ModelAdmin):
    list_display = ("id", "media_upload", "created_at")
    list_filter = ("created_at",)
