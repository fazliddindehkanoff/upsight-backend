from rest_framework import serializers
from django.core.validators import FileExtensionValidator
from django.core.files.images import get_image_dimensions
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
    # Add explicit field definitions for better form handling
    title_uz = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=200,
        help_text="Title in Uzbek language"
    )
    title_ko = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=200,
        help_text="Title in Korean language"
    )
    content_uz = serializers.CharField(
        required=False,
        allow_blank=True,
        style={'base_template': 'textarea.html'},
        help_text="Content in Uzbek language"
    )
    content_ko = serializers.CharField(
        required=False,
        allow_blank=True,
        style={'base_template': 'textarea.html'},
        help_text="Content in Korean language"
    )
    image = serializers.ImageField(
        required=False,
        allow_null=True,
        help_text="Upload news image (JPG, PNG, GIF formats supported)"
    )
    
    class Meta:
        model = News
        fields = [
            'title_uz', 'title_ko', 'content_uz', 'content_ko',
            'image', 'university'
        ]
    
    def validate_image(self, value):
        """Validate image file"""
        if value:
            # Check file size (max 5MB)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError(
                    "Image file size must be less than 5MB."
                )
            
            # Check image dimensions
            try:
                width, height = get_image_dimensions(value)
                if width and height:
                    if width > 2048 or height > 2048:
                        raise serializers.ValidationError(
                            "Image dimensions must be less than 2048x2048 pixels."
                        )
            except Exception:
                raise serializers.ValidationError(
                    "Invalid image file. Please upload a valid image."
                )
        return value
    
    def validate(self, data):
        """Enhanced validation with better error messages"""
        errors = {}
        
        # Check if at least one language version is provided for title
        if not data.get('title_uz') and not data.get('title_ko'):
            errors['title'] = "Please provide a title in at least one language (Uzbek or Korean)."
        
        # Check if at least one language version is provided for content
        if not data.get('content_uz') and not data.get('content_ko'):
            errors['content'] = "Please provide content in at least one language (Uzbek or Korean)."
        
        # Validate title lengths
        if data.get('title_uz') and len(data['title_uz'].strip()) < 3:
            errors['title_uz'] = "Uzbek title must be at least 3 characters long."
        if data.get('title_ko') and len(data['title_ko'].strip()) < 3:
            errors['title_ko'] = "Korean title must be at least 3 characters long."
        
        # Validate content lengths
        if data.get('content_uz') and len(data['content_uz'].strip()) < 10:
            errors['content_uz'] = "Uzbek content must be at least 10 characters long."
        if data.get('content_ko') and len(data['content_ko'].strip()) < 10:
            errors['content_ko'] = "Korean content must be at least 10 characters long."
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data
    
    def to_internal_value(self, data):
        """Clean and process form data"""
        # Handle multipart form data safely
        if hasattr(data, 'getlist'):
            # Create a new dict, preserving file objects
            processed_data = {}
            for key in data.keys():
                values = data.getlist(key)
                if len(values) == 1:
                    processed_data[key] = values[0]
                else:
                    processed_data[key] = values
            data = processed_data
        
        # Clean text fields only (avoid processing file fields)
        text_fields = ['title_uz', 'title_ko', 'content_uz', 'content_ko']
        for field in text_fields:
            if field in data and data[field] and hasattr(data[field], 'strip'):
                data[field] = data[field].strip()
        
        return super().to_internal_value(data)


class NoticeCreateUpdateSerializer(serializers.ModelSerializer):
    # Add explicit field definitions for better form handling
    title_uz = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=200,
        help_text="Title in Uzbek language"
    )
    title_ko = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=200,
        help_text="Title in Korean language"
    )
    content_uz = serializers.CharField(
        required=False,
        allow_blank=True,
        style={'base_template': 'textarea.html'},
        help_text="Content in Uzbek language"
    )
    content_ko = serializers.CharField(
        required=False,
        allow_blank=True,
        style={'base_template': 'textarea.html'},
        help_text="Content in Korean language"
    )
    image = serializers.ImageField(
        required=False,
        allow_null=True,
        help_text="Upload notice image (JPG, PNG, GIF formats supported)"
    )
    
    class Meta:
        model = Notice
        fields = [
            'title_uz', 'title_ko', 'content_uz', 'content_ko',
            'image', 'university'
        ]
    
    def validate_image(self, value):
        """Validate image file"""
        if value:
            # Check file size (max 5MB)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError(
                    "Image file size must be less than 5MB."
                )
            
            # Check image dimensions
            try:
                width, height = get_image_dimensions(value)
                if width and height:
                    if width > 2048 or height > 2048:
                        raise serializers.ValidationError(
                            "Image dimensions must be less than 2048x2048 pixels."
                        )
            except Exception:
                raise serializers.ValidationError(
                    "Invalid image file. Please upload a valid image."
                )
        return value
    
    def validate(self, data):
        """Enhanced validation with better error messages"""
        errors = {}
        
        # Check if at least one language version is provided for title
        if not data.get('title_uz') and not data.get('title_ko'):
            errors['title'] = "Please provide a title in at least one language (Uzbek or Korean)."
        
        # Check if at least one language version is provided for content
        if not data.get('content_uz') and not data.get('content_ko'):
            errors['content'] = "Please provide content in at least one language (Uzbek or Korean)."
        
        # Validate title lengths
        if data.get('title_uz') and len(data['title_uz'].strip()) < 3:
            errors['title_uz'] = "Uzbek title must be at least 3 characters long."
        if data.get('title_ko') and len(data['title_ko'].strip()) < 3:
            errors['title_ko'] = "Korean title must be at least 3 characters long."
        
        # Validate content lengths
        if data.get('content_uz') and len(data['content_uz'].strip()) < 10:
            errors['content_uz'] = "Uzbek content must be at least 10 characters long."
        if data.get('content_ko') and len(data['content_ko'].strip()) < 10:
            errors['content_ko'] = "Korean content must be at least 10 characters long."
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data
    
    def to_internal_value(self, data):
        """Clean and process form data"""
        # Handle multipart form data safely
        if hasattr(data, 'getlist'):
            # Create a new dict, preserving file objects
            processed_data = {}
            for key in data.keys():
                values = data.getlist(key)
                if len(values) == 1:
                    processed_data[key] = values[0]
                else:
                    processed_data[key] = values
            data = processed_data
        
        # Clean text fields only (avoid processing file fields)
        text_fields = ['title_uz', 'title_ko', 'content_uz', 'content_ko']
        for field in text_fields:
            if field in data and data[field] and hasattr(data[field], 'strip'):
                data[field] = data[field].strip()
        
        return super().to_internal_value(data)


class TranslationCreateUpdateSerializer(serializers.ModelSerializer):
    # Add explicit field definitions for better form handling
    title_uz = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=200,
        help_text="Title in Uzbek language"
    )
    title_ko = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=200,
        help_text="Title in Korean language"
    )
    content_uz = serializers.CharField(
        required=False,
        allow_blank=True,
        style={'base_template': 'textarea.html'},
        help_text="Content in Uzbek language"
    )
    content_ko = serializers.CharField(
        required=False,
        allow_blank=True,
        style={'base_template': 'textarea.html'},
        help_text="Content in Korean language"
    )
    image = serializers.ImageField(
        required=False,
        allow_null=True,
        help_text="Upload translation image (JPG, PNG, GIF formats supported)"
    )
    
    class Meta:
        model = Translation
        fields = [
            'title_uz', 'title_ko', 'content_uz', 'content_ko',
            'image', 'university'
        ]
    
    def validate_image(self, value):
        """Validate image file"""
        if value:
            # Check file size (max 5MB)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError(
                    "Image file size must be less than 5MB."
                )
            
            # Check image dimensions
            try:
                width, height = get_image_dimensions(value)
                if width and height:
                    if width > 2048 or height > 2048:
                        raise serializers.ValidationError(
                            "Image dimensions must be less than 2048x2048 pixels."
                        )
            except Exception:
                raise serializers.ValidationError(
                    "Invalid image file. Please upload a valid image."
                )
        return value
    
    def validate(self, data):
        """Enhanced validation with better error messages"""
        errors = {}
        
        # Check if at least one language version is provided for title
        if not data.get('title_uz') and not data.get('title_ko'):
            errors['title'] = "Please provide a title in at least one language (Uzbek or Korean)."
        
        # Check if at least one language version is provided for content
        if not data.get('content_uz') and not data.get('content_ko'):
            errors['content'] = "Please provide content in at least one language (Uzbek or Korean)."
        
        # Validate title lengths
        if data.get('title_uz') and len(data['title_uz'].strip()) < 3:
            errors['title_uz'] = "Uzbek title must be at least 3 characters long."
        if data.get('title_ko') and len(data['title_ko'].strip()) < 3:
            errors['title_ko'] = "Korean title must be at least 3 characters long."
        
        # Validate content lengths
        if data.get('content_uz') and len(data['content_uz'].strip()) < 10:
            errors['content_uz'] = "Uzbek content must be at least 10 characters long."
        if data.get('content_ko') and len(data['content_ko'].strip()) < 10:
            errors['content_ko'] = "Korean content must be at least 10 characters long."
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data
    
    def to_internal_value(self, data):
        """Clean and process form data"""
        # Handle multipart form data safely
        if hasattr(data, 'getlist'):
            # Create a new dict, preserving file objects
            processed_data = {}
            for key in data.keys():
                values = data.getlist(key)
                if len(values) == 1:
                    processed_data[key] = values[0]
                else:
                    processed_data[key] = values
            data = processed_data
        
        # Clean text fields only (avoid processing file fields)
        text_fields = ['title_uz', 'title_ko', 'content_uz', 'content_ko']
        for field in text_fields:
            if field in data and data[field] and hasattr(data[field], 'strip'):
                data[field] = data[field].strip()
        
        return super().to_internal_value(data)


class InformationCreateUpdateSerializer(serializers.ModelSerializer):
    # Add explicit field definitions for better form handling
    title_uz = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=200,
        help_text="Title in Uzbek language"
    )
    title_ko = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=200,
        help_text="Title in Korean language"
    )
    content_uz = serializers.CharField(
        required=False,
        allow_blank=True,
        style={'base_template': 'textarea.html'},
        help_text="Content in Uzbek language"
    )
    content_ko = serializers.CharField(
        required=False,
        allow_blank=True,
        style={'base_template': 'textarea.html'},
        help_text="Content in Korean language"
    )
    image = serializers.ImageField(
        required=False,
        allow_null=True,
        help_text="Upload information image (JPG, PNG, GIF formats supported)"
    )
    
    class Meta:
        model = Information
        fields = [
            'title_uz', 'title_ko', 'content_uz', 'content_ko',
            'image', 'university'
        ]
    
    def validate_image(self, value):
        """Validate image file"""
        if value:
            # Check file size (max 5MB)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError(
                    "Image file size must be less than 5MB."
                )
            
            # Check image dimensions
            try:
                width, height = get_image_dimensions(value)
                if width and height:
                    if width > 2048 or height > 2048:
                        raise serializers.ValidationError(
                            "Image dimensions must be less than 2048x2048 pixels."
                        )
            except Exception:
                raise serializers.ValidationError(
                    "Invalid image file. Please upload a valid image."
                )
        return value
    
    def validate(self, data):
        """Enhanced validation with better error messages"""
        errors = {}
        
        # Check if at least one language version is provided for title
        if not data.get('title_uz') and not data.get('title_ko'):
            errors['title'] = "Please provide a title in at least one language (Uzbek or Korean)."
        
        # Check if at least one language version is provided for content
        if not data.get('content_uz') and not data.get('content_ko'):
            errors['content'] = "Please provide content in at least one language (Uzbek or Korean)."
        
        # Validate title lengths
        if data.get('title_uz') and len(data['title_uz'].strip()) < 3:
            errors['title_uz'] = "Uzbek title must be at least 3 characters long."
        if data.get('title_ko') and len(data['title_ko'].strip()) < 3:
            errors['title_ko'] = "Korean title must be at least 3 characters long."
        
        # Validate content lengths
        if data.get('content_uz') and len(data['content_uz'].strip()) < 10:
            errors['content_uz'] = "Uzbek content must be at least 10 characters long."
        if data.get('content_ko') and len(data['content_ko'].strip()) < 10:
            errors['content_ko'] = "Korean content must be at least 10 characters long."
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data
    
    def to_internal_value(self, data):
        """Clean and process form data"""
        # Handle multipart form data safely
        if hasattr(data, 'getlist'):
            # Create a new dict, preserving file objects
            processed_data = {}
            for key in data.keys():
                values = data.getlist(key)
                if len(values) == 1:
                    processed_data[key] = values[0]
                else:
                    processed_data[key] = values
            data = processed_data
        
        # Clean text fields only (avoid processing file fields)
        text_fields = ['title_uz', 'title_ko', 'content_uz', 'content_ko']
        for field in text_fields:
            if field in data and data[field] and hasattr(data[field], 'strip'):
                data[field] = data[field].strip()
        
        return super().to_internal_value(data)


class InformationDocumentsCreateUpdateSerializer(serializers.ModelSerializer):
    # Add explicit field definitions for better form handling
    document_uz = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=200,
        help_text="Document title in Uzbek language"
    )
    document_ko = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=200,
        help_text="Document title in Korean language"
    )
    file = serializers.FileField(
        required=True,
        help_text="Upload document file (PDF, DOC, DOCX, XLS, XLSX formats supported)",
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'rtf']
            )
        ]
    )
    
    class Meta:
        model = InformationDocuments
        fields = [
            'information', 'document_uz', 'document_ko', 'file'
        ]
    
    def validate_file(self, value):
        """Validate document file"""
        if value:
            # Check file size (max 10MB for documents)
            if value.size > 10 * 1024 * 1024:
                raise serializers.ValidationError(
                    "Document file size must be less than 10MB."
                )
            
            # Check file name length
            if len(value.name) > 100:
                raise serializers.ValidationError(
                    "File name is too long. Please use a shorter file name (max 100 characters)."
                )
        return value
    
    def validate(self, data):
        """Enhanced validation with better error messages"""
        errors = {}
        
        # Check if at least one language version is provided for document title
        if not data.get('document_uz') and not data.get('document_ko'):
            errors['document_title'] = "Please provide a document title in at least one language (Uzbek or Korean)."
        
        # Validate document title lengths
        if data.get('document_uz') and len(data['document_uz'].strip()) < 3:
            errors['document_uz'] = "Uzbek document title must be at least 3 characters long."
        if data.get('document_ko') and len(data['document_ko'].strip()) < 3:
            errors['document_ko'] = "Korean document title must be at least 3 characters long."
        
        # Validate information exists
        if not data.get('information'):
            errors['information'] = "Please select an information item to attach this document to."
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data
    
    def to_internal_value(self, data):
        """Clean and process form data"""
        # Handle multipart form data safely
        if hasattr(data, 'getlist'):
            # Create a new dict, preserving file objects
            processed_data = {}
            for key in data.keys():
                values = data.getlist(key)
                if len(values) == 1:
                    processed_data[key] = values[0]
                else:
                    processed_data[key] = values
            data = processed_data
        
        # Clean text fields only (avoid processing file fields)
        text_fields = ['document_uz', 'document_ko']
        for field in text_fields:
            if field in data and data[field] and hasattr(data[field], 'strip'):
                data[field] = data[field].strip()
        
        return super().to_internal_value(data)