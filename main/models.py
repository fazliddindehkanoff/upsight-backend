from django.db import models
from django.urls import reverse


class Carousel(models.Model):
    image = models.ImageField(upload_to="carousel_images/")

    def __str__(self):
        return f"img: {self.id}"


class News(models.Model):
    title_ko = models.CharField(max_length=100, null=True, blank=True)
    title_uz = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to="news_images/")
    content_ko = models.TextField(null=True, blank=True)
    content_uz = models.TextField(null=True, blank=True)
    file_field = models.FileField(
        upload_to="news_files/", null=True, blank=True
    )  # New field
    date_posted = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse("news-detail", args=[str(self.pk)])

    def get_title(self, language="ko"):
        return self.title_ko if language == "ko" else self.title_uz

    def get_content(self, language="ko"):
        return self.content_ko if language == "ko" else self.content_uz

    def __str__(self):
        return self.title_ko or self.title_uz


class Person(models.Model):
    full_name_uz = models.CharField(max_length=50, null=True, blank=True)
    full_name_ko = models.CharField(max_length=50, null=True, blank=True)
    position_uz = models.CharField(max_length=50)
    position_ko = models.CharField(max_length=50)
    image = models.ImageField(upload_to="person_images/")

    def get_full_name(self, language="ko"):
        return self.full_name_ko if language == "ko" else self.full_name_uz

    def get_position(self, language="ko"):
        return self.position_ko if language == "ko" else self.position_uz

    def __str__(self):
        return self.full_name_ko or self.full_name_uz


class Experience(models.Model):
    person = models.ForeignKey(
        Person,
        related_name="experiences",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    experience_ko = models.CharField(max_length=1024, null=True, blank=True)
    experience_uz = models.CharField(max_length=1024, null=True, blank=True)

    def get_experience(self, language="ko"):
        return self.experience_ko if language == "ko" else self.experience_uz

    def __str__(self):
        return self.experience_ko or self.experience_uz


class Gallery(models.Model):
    title_ko = models.CharField(max_length=100)
    title_uz = models.CharField(max_length=100)
    image = models.ImageField(upload_to="gallery_images/")

    def get_title(self, language="ko"):
        return self.title_ko if language == "ko" else self.title_uz

    def __str__(self):
        return self.title_ko or self.title_uz


class GalleryItem(models.Model):
    gallery = models.ForeignKey(
        Gallery, related_name="items", on_delete=models.CASCADE, null=True, blank=True
    )
    description_ko = models.TextField(null=True, blank=True)
    description_uz = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to="gallery_images/gallery_items_images/")

    def get_description(self, language="ko"):
        return self.description_ko if language == "ko" else self.description_uz

    def __str__(self):
        return str(self.gallery)


class AboutUs(models.Model):
    fullname = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    content = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.fullname


class Feedback(models.Model):
    image = models.ImageField(upload_to="feedback/")
    fullname_uz = models.CharField(max_length=100, blank=True, null=True)
    fullname_ko = models.CharField(max_length=100, blank=True, null=True)
    description_uz = models.TextField(blank=True, null=True)
    description_ko = models.TextField(blank=True, null=True)

    def get_fullname(self, language="ko"):
        return self.fullname_ko if language == "ko" else self.fullname_uz

    def get_description(self, language="ko"):
        return self.description_ko if language == "ko" else self.description_uz

    def __str__(self):
        return self.fullname_ko or self.fullname_uz


class Report(models.Model):
    umumiy_oquv = models.IntegerField(default=0)
    jami_oquv = models.IntegerField(default=0)
    oqituvchi = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.umumiy_oquv}"
