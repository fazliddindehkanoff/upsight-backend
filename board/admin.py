from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.admin import TabularInline

from .models import News, Notice, Translation, Information, InformationDocuments


class InformationDocumentsInline(TabularInline):
    model = InformationDocuments
    extra = 1
    fields = ("document_uz", "document_ko", "file")


@admin.register(News)
class NewsAdmin(ModelAdmin):
    list_display = ["get_title_display", "university", "date", "has_image"]
    list_filter = ["university", "date"]
    search_fields = ["title_uz", "title_ko", "content_uz", "content_ko"]
    readonly_fields = ("date",)

    fieldsets = (
        (
            "Content",
            {
                "fields": (
                    ("title_uz", "title_ko"),
                    ("content_uz", "content_ko"),
                    "image",
                    "university",
                    "date",
                )
            },
        ),
    )

    def get_title_display(self, obj):
        return f"{obj.title_ko} / {obj.title_uz}"

    get_title_display.short_description = "Title (KO/UZ)"

    def has_image(self, obj):
        return bool(obj.image)

    has_image.boolean = True
    has_image.short_description = "Has Image"


@admin.register(Notice)
class NoticeAdmin(ModelAdmin):
    list_display = ["get_title_display", "university", "date", "has_image"]
    list_filter = ["university", "date"]
    search_fields = ["title_uz", "title_ko", "content_uz", "content_ko"]
    readonly_fields = ("date",)

    fieldsets = (
        (
            "Content",
            {
                "fields": (
                    ("title_uz", "title_ko"),
                    ("content_uz", "content_ko"),
                    "image",
                    "university",
                    "date",
                )
            },
        ),
    )

    def get_title_display(self, obj):
        return f"{obj.title_ko} / {obj.title_uz}"

    get_title_display.short_description = "Title (KO/UZ)"

    def has_image(self, obj):
        return bool(obj.image)

    has_image.boolean = True
    has_image.short_description = "Has Image"


@admin.register(Translation)
class TranslationAdmin(ModelAdmin):
    list_display = ["get_title_display", "university", "has_image"]
    list_filter = ["university"]
    search_fields = ["title_uz", "title_ko", "content_uz", "content_ko"]

    fieldsets = (
        (
            "Translation Content",
            {
                "fields": (
                    ("title_uz", "title_ko"),
                    ("content_uz", "content_ko"),
                    "image",
                    "university",
                )
            },
        ),
    )

    def get_title_display(self, obj):
        return f"{obj.title_ko} / {obj.title_uz}"

    get_title_display.short_description = "Title (KO/UZ)"

    def has_image(self, obj):
        return bool(obj.image)

    has_image.boolean = True
    has_image.short_description = "Has Image"


@admin.register(Information)
class InformationAdmin(ModelAdmin):
    list_display = [
        "get_title_display",
        "university",
        "date",
        "has_image",
        "document_count",
    ]
    list_filter = ["university", "date"]
    search_fields = ["title_uz", "title_ko", "content_uz", "content_ko"]
    readonly_fields = ("date",)

    fieldsets = (
        (
            "Information Content",
            {
                "fields": (
                    ("title_uz", "title_ko"),
                    ("content_uz", "content_ko"),
                    "image",
                    "university",
                    "date",
                )
            },
        ),
    )

    inlines = [InformationDocumentsInline]

    def get_title_display(self, obj):
        return f"{obj.title_ko} / {obj.title_uz}"

    get_title_display.short_description = "Title (KO/UZ)"

    def has_image(self, obj):
        return bool(obj.image)

    has_image.boolean = True
    has_image.short_description = "Has Image"

    def document_count(self, obj):
        return obj.documents.count()

    document_count.short_description = "Documents"
