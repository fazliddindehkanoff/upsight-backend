from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.admin import StackedInline, TabularInline
from .models import Carousel, News, Person, Experience, AboutUs, Feedback, Report, Gallery, GalleryItem


@admin.register(Carousel)
class CarouselAdminClass(ModelAdmin):
    pass


class GalleryItemInline(TabularInline):
    model = GalleryItem
    extra = 3


@admin.register(Gallery)
class GalleryAdmin(ModelAdmin):
    inlines = [GalleryItemInline]


@admin.register(News)
class NewsAdminClass(ModelAdmin):
    pass


class ExperienceInline(StackedInline):
    model = Experience
    extra = 1


@admin.register(Person)
class PersonAdmin(ModelAdmin):
    inlines = [ExperienceInline]


@admin.register(AboutUs)
class AboutUsAdminClass(ModelAdmin):
    pass


@admin.register(Feedback)
class FeedbackAdminClass(ModelAdmin):
    pass


@admin.register(Report)
class ReportAdminClass(ModelAdmin):
    pass
