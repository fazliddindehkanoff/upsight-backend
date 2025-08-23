from rest_framework import serializers
from .models import Carousel, News, Person, Experience, Gallery, GalleryItem, AboutUs, Feedback, Report


class CarouselSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carousel
        fields = '__all__'


class NewsSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    detail_url = serializers.SerializerMethodField()

    def get_title(self, obj):
        language = self.context.get('language', 'ko')  # Default to Korean
        return obj.title_ko if language == 'ko' else obj.title_uz

    def get_content(self, obj):
        language = self.context.get('language', 'ko')  # Default to Korean
        return obj.content_ko if language == 'ko' else obj.content_uz
        
    
    def get_detail_url(self, obj):
        request = self.context.get('request')
        if request is not None and obj.pk is not None:
            return request.build_absolute_uri(obj.get_absolute_url())

    class Meta:
        model = News
        fields = '__all__'


class ExperienceSerializer(serializers.ModelSerializer):
    experience = serializers.SerializerMethodField()

    def get_experience(self, obj):
        language = self.context.get('language', 'ko')  # Default to Korean
        return obj.experience_ko if language == 'ko' else obj.experience_uz

    class Meta:
        model = Experience
        fields = '__all__'


class PersonSerializer(serializers.ModelSerializer):
    experiences = ExperienceSerializer(many=True, read_only=True)

    class Meta:
        model = Person
        fields = '__all__'


class GalleryItemSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()

    def get_description(self, obj):
        language = self.context.get('language', 'ko')  # Default to Korean
        return obj.description_ko if language == 'ko' else obj.description_uz

    class Meta:
        model = GalleryItem
        fields = '__all__'


class GallerySerializer(serializers.ModelSerializer):
    items = GalleryItemSerializer(many=True, read_only=True)
    detail_url = serializers.HyperlinkedIdentityField(view_name='gallery-detail')

    class Meta:
        model = Gallery
        fields = '__all__'


class AboutUsSerializer(serializers.ModelSerializer):

    class Meta:
        model = AboutUs
        fields = '__all__'


class FeedbackSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    def get_fullname(self, obj):
        language = self.context.get('language', 'ko')  # Default to Korean
        return obj.fullname_ko if language == 'ko' else obj.fullname_uz

    def get_description(self, obj):
        language = self.context.get('language', 'ko')  # Default to Korean
        return obj.description_ko if language == 'ko' else obj.description_uz

    class Meta:
        model = Feedback
        fields = '__all__'



class ReportSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Report
        fields = '__all__'


