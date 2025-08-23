from django.db import models
from management.models import University


class News(models.Model):
    title_uz = models.CharField(max_length=200, verbose_name='Title in Uzbek')
    title_ko = models.CharField(max_length=200, verbose_name='Title in Korean')
    content_uz = models.TextField()
    content_ko = models.TextField()
    image = models.ImageField(upload_to='news_images/', blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    university = models.ForeignKey(University, on_delete=models.CASCADE)

    def __str__(self):
        return self.title_uz


class Notice(models.Model):
    title_uz = models.CharField(max_length=200, verbose_name='Title in Uzbek')
    title_ko = models.CharField(max_length=200, verbose_name='Title in Korean')
    content_uz = models.TextField()
    content_ko = models.TextField()
    image = models.ImageField(upload_to='notice_images/', blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    university = models.ForeignKey(University, on_delete=models.CASCADE)

    def __str__(self):
        return self.title_uz


class Translation(models.Model):
    title_uz = models.CharField(max_length=200, verbose_name='Title in Uzbek')
    title_ko = models.CharField(max_length=200, verbose_name='Title in Korean')
    content_uz = models.TextField()
    content_ko = models.TextField()
    image = models.ImageField(upload_to='notice_images/', blank=True, null=True)
    university = models.ForeignKey(University, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title_uz} Translation"


class Information(models.Model):
    title_uz = models.CharField(max_length=200, verbose_name='Title in Uzbek')
    title_ko = models.CharField(max_length=200, verbose_name='Title in Korean')
    content_uz = models.TextField()
    content_ko = models.TextField()
    image = models.ImageField(upload_to='information_images/', blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    university = models.ForeignKey(University, on_delete=models.CASCADE)

    def __str__(self):
        return self.title_uz


class InformationDocuments(models.Model):
    information = models.ForeignKey(Information, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='information_documents/')
    document_uz = models.CharField(max_length=200, verbose_name='Document Title in Uzbek')
    document_ko = models.CharField(max_length=200, verbose_name='Document Title in Korean')

    def __str__(self):
        return f"Document for {self.information.title_uz}"
