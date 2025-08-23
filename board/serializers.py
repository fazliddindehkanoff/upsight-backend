from rest_framework import serializers
from .models import News, Notice, Translation, Information, InformationDocuments


class NewsSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    university_name = serializers.CharField(source='university.__str__', read_only=True)
    has_image = serializers.SerializerMethodField()
    
    class Meta:
        model = News
        fields = [
            'id', 'title_uz', 'title_ko', 'title', 'content_uz', 'content_ko', 
            'content', 'image', 'has_image', 'date', 'university', 'university_name'
        ]
    
    def get_title(self, obj):
        return obj.title_ko or obj.title_uz
    
    def get_content(self, obj):
        return obj.content_ko or obj.content_uz
    
    def get_has_image(self, obj):
        return bool(obj.image)


class NoticeSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    university_name = serializers.CharField(source='university.__str__', read_only=True)
    has_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Notice
        fields = [
            'id', 'title_uz', 'title_ko', 'title', 'content_uz', 'content_ko', 
            'content', 'image', 'has_image', 'date', 'university', 'university_name'
        ]
    
    def get_title(self, obj):
        return obj.title_ko or obj.title_uz
    
    def get_content(self, obj):
        return obj.content_ko or obj.content_uz
    
    def get_has_image(self, obj):
        return bool(obj.image)


class TranslationSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    university_name = serializers.CharField(source='university.__str__', read_only=True)
    has_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Translation
        fields = [
            'id', 'title_uz', 'title_ko', 'title', 'content_uz', 'content_ko',
            'content', 'image', 'has_image', 'university', 'university_name'
        ]
    
    def get_title(self, obj):
        return obj.title_ko or obj.title_uz
    
    def get_content(self, obj):
        return obj.content_ko or obj.content_uz
    
    def get_has_image(self, obj):
        return bool(obj.image)


class InformationDocumentsSerializer(serializers.ModelSerializer):
    document_title = serializers.SerializerMethodField()
    has_file = serializers.SerializerMethodField()
    
    class Meta:
        model = InformationDocuments
        fields = [
            'id', 'document_uz', 'document_ko', 'document_title', 'file', 'has_file'
        ]
    
    def get_document_title(self, obj):
        return obj.document_ko or obj.document_uz
    
    def get_has_file(self, obj):
        return bool(obj.file)


class InformationSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    university_name = serializers.CharField(source='university.__str__', read_only=True)
    has_image = serializers.SerializerMethodField()
    documents = InformationDocumentsSerializer(many=True, read_only=True)
    document_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Information
        fields = [
            'id', 'title_uz', 'title_ko', 'title', 'content_uz', 'content_ko', 
            'content', 'image', 'has_image', 'date', 'university', 'university_name',
            'documents', 'document_count'
        ]
    
    def get_title(self, obj):
        return obj.title_ko or obj.title_uz
    
    def get_content(self, obj):
        return obj.content_ko or obj.content_uz
    
    def get_has_image(self, obj):
        return bool(obj.image)
    
    def get_document_count(self, obj):
        return obj.documents.count()


# CRUD Serializers for Create/Update operations
class NewsCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = [
            'title_uz', 'title_ko', 'content_uz', 'content_ko',
            'image', 'university'
        ]
    
    def validate(self, data):
        """Validate that at least one language version is provided"""
        if not data.get('title_uz') and not data.get('title_ko'):
            raise serializers.ValidationError("At least one title (UZ or KO) is required.")
        if not data.get('content_uz') and not data.get('content_ko'):
            raise serializers.ValidationError("At least one content (UZ or KO) is required.")
        return data


class NoticeCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = [
            'title_uz', 'title_ko', 'content_uz', 'content_ko',
            'image', 'university'
        ]
    
    def validate(self, data):
        """Validate that at least one language version is provided"""
        if not data.get('title_uz') and not data.get('title_ko'):
            raise serializers.ValidationError("At least one title (UZ or KO) is required.")
        if not data.get('content_uz') and not data.get('content_ko'):
            raise serializers.ValidationError("At least one content (UZ or KO) is required.")
        return data


class TranslationCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Translation
        fields = [
            'title_uz', 'title_ko', 'content_uz', 'content_ko',
            'image', 'university'
        ]
    
    def validate(self, data):
        """Validate that at least one language version is provided"""
        if not data.get('title_uz') and not data.get('title_ko'):
            raise serializers.ValidationError("At least one title (UZ or KO) is required.")
        if not data.get('content_uz') and not data.get('content_ko'):
            raise serializers.ValidationError("At least one content (UZ or KO) is required.")
        return data


class InformationCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Information
        fields = [
            'title_uz', 'title_ko', 'content_uz', 'content_ko',
            'image', 'university'
        ]
    
    def validate(self, data):
        """Validate that at least one language version is provided"""
        if not data.get('title_uz') and not data.get('title_ko'):
            raise serializers.ValidationError("At least one title (UZ or KO) is required.")
        if not data.get('content_uz') and not data.get('content_ko'):
            raise serializers.ValidationError("At least one content (UZ or KO) is required.")
        return data


class InformationDocumentsCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformationDocuments
        fields = [
            'information', 'document_uz', 'document_ko', 'file'
        ]
    
    def validate(self, data):
        """Validate that at least one language version is provided"""
        if not data.get('document_uz') and not data.get('document_ko'):
            raise serializers.ValidationError("At least one document title (UZ or KO) is required.")
        return data