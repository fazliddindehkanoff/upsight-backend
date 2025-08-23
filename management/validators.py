import os
from django.core.exceptions import ValidationError


def validate_pdf_file(file):
    ext = os.path.splitext(file.name)[1].lower()
    if ext != ".pdf":
        raise ValidationError("Only PDF files are allowed.")


def validate_file_size(file):
    max_size = 10 * 1024 * 1024  # 10MB in bytes
    if file.size > max_size:
        raise ValidationError("File size cannot exceed 10MB.")


def validate_image_size(file):
    max_size = 5 * 1024 * 1024  # 5MB for images
    if file.size > max_size:
        raise ValidationError("Image size cannot exceed 5MB.")
