from django.contrib import admin

from .models import DetectionRun, DetectedObject, MediaUpload, OCRExtraction


@admin.register(MediaUpload)
class MediaUploadAdmin(admin.ModelAdmin):
    list_display = ("id", "file_name", "media_type", "source_type", "created_at")
    search_fields = ("file_name",)
    list_filter = ("media_type", "source_type", "created_at")


@admin.register(DetectionRun)
class DetectionRunAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "media_upload",
        "model_name",
        "status",
        "total_objects_found",
        "created_at",
    )
    list_filter = ("status", "model_name", "created_at")


@admin.register(DetectedObject)
class DetectedObjectAdmin(admin.ModelAdmin):
    list_display = ("id", "detection_run", "object_class", "confidence", "player")
    list_filter = ("object_class",)


@admin.register(OCRExtraction)
class OCRExtractionAdmin(admin.ModelAdmin):
    list_display = ("id", "media_upload", "field_type", "confidence", "created_at")
    list_filter = ("field_type", "created_at")
