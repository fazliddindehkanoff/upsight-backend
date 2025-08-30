from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .serializers import (
    NewsSerializer,
    NoticeSerializer,
    TranslationSerializer,
    InformationSerializer,
    InformationDocumentsSerializer,
    NewsCreateUpdateSerializer,
    NoticeCreateUpdateSerializer,
    TranslationCreateUpdateSerializer,
    InformationCreateUpdateSerializer,
    InformationDocumentsCreateUpdateSerializer
)
from .models import News, Notice, Translation, Information, InformationDocuments
from management.models import UniversityManager


def get_user_university(user):
    """Get university for university_staff users"""
    try:
        if user.groups.filter(name="university_staff").exists():
            manager = UniversityManager.objects.get(user=user)
            return manager.university
    except UniversityManager.DoesNotExist:
        pass
    return None


def process_form_data(data):
    """Process and clean form data from multipart/form requests"""
    if hasattr(data, 'getlist'):
        # Handle QueryDict properly, preserving file objects
        processed_data = {}
        for key in data.keys():
            values = data.getlist(key)
            if len(values) == 1:
                processed_data[key] = values[0]
            else:
                processed_data[key] = values
    else:
        processed_data = dict(data) if data else {}
    
    # Clean empty strings and convert to None for better validation
    # Only process text fields, avoid corrupting file objects
    for key, value in processed_data.items():
        if isinstance(value, str) and value.strip() == '':
            processed_data[key] = None
        elif isinstance(value, str):
            processed_data[key] = value.strip()
    
    return processed_data


def format_serializer_errors(errors):
    """Format serializer errors into user-friendly messages"""
    formatted_errors = {}
    
    for field, error_list in errors.items():
        if isinstance(error_list, list):
            formatted_errors[field] = error_list[0] if error_list else "Invalid value"
        elif isinstance(error_list, dict):
            # Handle nested errors
            formatted_errors[field] = format_serializer_errors(error_list)
        else:
            formatted_errors[field] = str(error_list)
    
    return formatted_errors


def filter_by_permissions(queryset, user):
    """Filter queryset based on user permissions"""
    if user.groups.filter(name="upsight_staff").exists():
        return queryset  # upsight_staff can see all
    
    university = get_user_university(user)
    if university:
        return queryset.filter(university=university)
    
    return queryset.none()  # No access if no proper role


# News Views
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def news_list(request):
    """Get list of news based on user role"""
    try:
        # Check permissions
        if not (request.user.groups.filter(name="upsight_staff").exists() or 
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {"error": "Permission denied. Only staff can view news."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        news = News.objects.select_related('university').all().order_by('-date')
        news = filter_by_permissions(news, request.user)
        serializer = NewsSerializer(news, many=True, context={"request": request})
        
        return Response(
            {
                "news": serializer.data,
                "total_count": len(serializer.data),
            },
            status=status.HTTP_200_OK,
        )
    
    except Exception as e:
        return Response(
            {"error": "Failed to fetch news", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def news_detail(request, news_id):
    """Get news details based on user role"""
    try:
        # Check permissions
        if not (request.user.groups.filter(name="upsight_staff").exists() or 
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {"error": "Permission denied. Only staff can view news details."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        news = News.objects.select_related('university').get(id=news_id)
        
        # Check if user can access this news
        if request.user.groups.filter(name="university_staff").exists():
            user_university = get_user_university(request.user)
            if user_university != news.university:
                return Response(
                    {"error": "Permission denied. You can only view your university's news."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = NewsSerializer(news, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except News.DoesNotExist:
        return Response(
            {"error": "News not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "Failed to fetch news", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def news_create(request):
    """Create news item with enhanced form data handling"""
    try:
        # Check permissions
        if not (request.user.groups.filter(name="upsight_staff").exists() or
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {
                    "error": "Permission denied",
                    "message": "Only staff members can create news items."
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Process form data
        data = process_form_data(request.data)
        
        # Set university for university_staff
        if request.user.groups.filter(name="university_staff").exists():
            user_university = get_user_university(request.user)
            if not user_university:
                return Response(
                    {
                        "error": "University not found",
                        "message": "Your user account is not associated with any university. Please contact support."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            data['university'] = user_university.id
        
        serializer = NewsCreateUpdateSerializer(data=data)
        if serializer.is_valid():
            news = serializer.save()
            response_serializer = NewsSerializer(news, context={"request": request})
            
            return Response(
                {
                    "success": True,
                    "message": "News item created successfully",
                    "data": {
                        "news": response_serializer.data
                    }
                },
                status=status.HTTP_201_CREATED
            )
        
        # Enhanced error response
        return Response(
            {
                "success": False,
                "error": "Validation failed",
                "message": "Please check the form data and try again.",
                "field_errors": format_serializer_errors(serializer.errors)
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except Exception as e:
        return Response(
            {
                "success": False,
                "error": "Server error",
                "message": "An unexpected error occurred while creating the news item.",
                "details": str(e) if hasattr(e, '__str__') else "Unknown error"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def news_update(request, news_id):
    """Update news item with enhanced form data handling"""
    try:
        # Check permissions
        if not (request.user.groups.filter(name="upsight_staff").exists() or
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {
                    "error": "Permission denied",
                    "message": "Only staff members can update news items."
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            news = News.objects.get(id=news_id)
        except News.DoesNotExist:
            return Response(
                {
                    "error": "News not found",
                    "message": f"News item with ID {news_id} does not exist."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user can update this news
        if request.user.groups.filter(name="university_staff").exists():
            user_university = get_user_university(request.user)
            if user_university != news.university:
                return Response(
                    {
                        "error": "Permission denied",
                        "message": "You can only update news items from your own university."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Process form data
        data = process_form_data(request.data)
        
        # Ensure university doesn't change for university_staff
        if request.user.groups.filter(name="university_staff").exists():
            data['university'] = news.university.id
        
        serializer = NewsCreateUpdateSerializer(
            news,
            data=data,
            partial=(request.method == "PATCH")
        )
        
        if serializer.is_valid():
            updated_news = serializer.save()
            response_serializer = NewsSerializer(updated_news, context={"request": request})
            
            return Response(
                {
                    "success": True,
                    "message": "News item updated successfully",
                    "data": {
                        "news": response_serializer.data
                    }
                },
                status=status.HTTP_200_OK
            )
        
        # Enhanced error response
        return Response(
            {
                "success": False,
                "error": "Validation failed",
                "message": "Please check the form data and try again.",
                "field_errors": format_serializer_errors(serializer.errors)
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except Exception as e:
        return Response(
            {
                "success": False,
                "error": "Server error",
                "message": "An unexpected error occurred while updating the news item.",
                "details": str(e) if hasattr(e, '__str__') else "Unknown error"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def news_delete(request, news_id):
    """Delete news item"""
    try:
        # Check permissions
        if not (request.user.groups.filter(name="upsight_staff").exists() or 
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {"error": "Permission denied. Only staff can delete news."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        news = News.objects.get(id=news_id)
        
        # Check if user can delete this news
        if request.user.groups.filter(name="university_staff").exists():
            user_university = get_user_university(request.user)
            if user_university != news.university:
                return Response(
                    {"error": "Permission denied. You can only delete your university's news."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        news.delete()
        
        return Response(
            {"message": "News deleted successfully"},
            status=status.HTTP_200_OK
        )
    
    except News.DoesNotExist:
        return Response(
            {"error": "News not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "Failed to delete news", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# Notice Views (similar structure as News)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def notices_list(request):
    """Get list of notices based on user role"""
    try:
        if not (request.user.groups.filter(name="upsight_staff").exists() or 
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {"error": "Permission denied. Only staff can view notices."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        notices = Notice.objects.select_related('university').all().order_by('-date')
        notices = filter_by_permissions(notices, request.user)
        serializer = NoticeSerializer(notices, many=True, context={"request": request})
        
        return Response(
            {
                "notices": serializer.data,
                "total_count": len(serializer.data),
            },
            status=status.HTTP_200_OK,
        )
    
    except Exception as e:
        return Response(
            {"error": "Failed to fetch notices", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def notice_detail(request, notice_id):
    """Get notice details based on user role"""
    try:
        if not (request.user.groups.filter(name="upsight_staff").exists() or 
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {"error": "Permission denied. Only staff can view notice details."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        notice = Notice.objects.select_related('university').get(id=notice_id)
        
        if request.user.groups.filter(name="university_staff").exists():
            user_university = get_user_university(request.user)
            if user_university != notice.university:
                return Response(
                    {"error": "Permission denied. You can only view your university's notices."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = NoticeSerializer(notice, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Notice.DoesNotExist:
        return Response(
            {"error": "Notice not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "Failed to fetch notice", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def notice_create(request):
    """Create notice item with enhanced form data handling"""
    try:
        if not (request.user.groups.filter(name="upsight_staff").exists() or
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {
                    "error": "Permission denied",
                    "message": "Only staff members can create notice items."
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Process form data
        data = process_form_data(request.data)
        
        if request.user.groups.filter(name="university_staff").exists():
            user_university = get_user_university(request.user)
            if not user_university:
                return Response(
                    {
                        "error": "University not found",
                        "message": "Your user account is not associated with any university. Please contact support."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            data['university'] = user_university.id
        
        serializer = NoticeCreateUpdateSerializer(data=data)
        if serializer.is_valid():
            notice = serializer.save()
            response_serializer = NoticeSerializer(notice, context={"request": request})
            
            return Response(
                {
                    "success": True,
                    "message": "Notice created successfully",
                    "data": {
                        "notice": response_serializer.data
                    }
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            {
                "success": False,
                "error": "Validation failed",
                "message": "Please check the form data and try again.",
                "field_errors": format_serializer_errors(serializer.errors)
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except Exception as e:
        return Response(
            {
                "success": False,
                "error": "Server error",
                "message": "An unexpected error occurred while creating the notice.",
                "details": str(e) if hasattr(e, '__str__') else "Unknown error"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def notice_update(request, notice_id):
    """Update notice item with enhanced form data handling"""
    try:
        if not (request.user.groups.filter(name="upsight_staff").exists() or
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {
                    "error": "Permission denied",
                    "message": "Only staff members can update notice items."
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            notice = Notice.objects.get(id=notice_id)
        except Notice.DoesNotExist:
            return Response(
                {
                    "error": "Notice not found",
                    "message": f"Notice with ID {notice_id} does not exist."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        if request.user.groups.filter(name="university_staff").exists():
            user_university = get_user_university(request.user)
            if user_university != notice.university:
                return Response(
                    {
                        "error": "Permission denied",
                        "message": "You can only update notices from your own university."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Process form data
        data = process_form_data(request.data)
        
        if request.user.groups.filter(name="university_staff").exists():
            data['university'] = notice.university.id
        
        serializer = NoticeCreateUpdateSerializer(
            notice,
            data=data,
            partial=(request.method == "PATCH")
        )
        
        if serializer.is_valid():
            updated_notice = serializer.save()
            response_serializer = NoticeSerializer(updated_notice, context={"request": request})
            
            return Response(
                {
                    "success": True,
                    "message": "Notice updated successfully",
                    "data": {
                        "notice": response_serializer.data
                    }
                },
                status=status.HTTP_200_OK
            )
        
        return Response(
            {
                "success": False,
                "error": "Validation failed",
                "message": "Please check the form data and try again.",
                "field_errors": format_serializer_errors(serializer.errors)
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except Exception as e:
        return Response(
            {
                "success": False,
                "error": "Server error",
                "message": "An unexpected error occurred while updating the notice.",
                "details": str(e) if hasattr(e, '__str__') else "Unknown error"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def notice_delete(request, notice_id):
    """Delete notice item"""
    try:
        if not (request.user.groups.filter(name="upsight_staff").exists() or
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {"error": "Permission denied. Only staff can delete notices."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        notice = Notice.objects.get(id=notice_id)
        
        if request.user.groups.filter(name="university_staff").exists():
            user_university = get_user_university(request.user)
            if user_university != notice.university:
                return Response(
                    {"error": "Permission denied. You can only delete your university's notices."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        notice.delete()
        
        return Response(
            {"message": "Notice deleted successfully"},
            status=status.HTTP_200_OK
        )
    
    except Notice.DoesNotExist:
        return Response(
            {"error": "Notice not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "Failed to delete notice", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# Translation Views
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def translations_list(request):
    """Get list of translations based on user role"""
    try:
        if not (request.user.groups.filter(name="upsight_staff").exists() or
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {"error": "Permission denied. Only staff can view translations."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        translations = Translation.objects.select_related('university').all()
        translations = filter_by_permissions(translations, request.user)
        serializer = TranslationSerializer(translations, many=True, context={"request": request})
        
        return Response(
            {
                "translations": serializer.data,
                "total_count": len(serializer.data),
            },
            status=status.HTTP_200_OK,
        )
    
    except Exception as e:
        return Response(
            {"error": "Failed to fetch translations", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def translation_detail(request, translation_id):
    """Get translation details based on user role"""
    try:
        if not (request.user.groups.filter(name="upsight_staff").exists() or
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {"error": "Permission denied. Only staff can view translation details."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        translation = Translation.objects.select_related('university').get(id=translation_id)
        
        if request.user.groups.filter(name="university_staff").exists():
            user_university = get_user_university(request.user)
            if user_university != translation.university:
                return Response(
                    {"error": "Permission denied. You can only view your university's translations."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = TranslationSerializer(translation, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Translation.DoesNotExist:
        return Response(
            {"error": "Translation not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "Failed to fetch translation", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def translation_create(request):
    """Create translation item with enhanced form data handling"""
    try:
        if not (request.user.groups.filter(name="upsight_staff").exists() or
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {
                    "error": "Permission denied",
                    "message": "Only staff members can create translation items."
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Process form data
        data = process_form_data(request.data)
        
        if request.user.groups.filter(name="university_staff").exists():
            user_university = get_user_university(request.user)
            if not user_university:
                return Response(
                    {
                        "error": "University not found",
                        "message": "Your user account is not associated with any university. Please contact support."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            data['university'] = user_university.id
        
        serializer = TranslationCreateUpdateSerializer(data=data)
        if serializer.is_valid():
            translation = serializer.save()
            response_serializer = TranslationSerializer(translation, context={"request": request})
            
            return Response(
                {
                    "success": True,
                    "message": "Translation created successfully",
                    "data": {
                        "translation": response_serializer.data
                    }
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            {
                "success": False,
                "error": "Validation failed",
                "message": "Please check the form data and try again.",
                "field_errors": format_serializer_errors(serializer.errors)
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except Exception as e:
        return Response(
            {
                "success": False,
                "error": "Server error",
                "message": "An unexpected error occurred while creating the translation.",
                "details": str(e) if hasattr(e, '__str__') else "Unknown error"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def translation_update(request, translation_id):
    """Update translation item with enhanced form data handling"""
    try:
        if not (request.user.groups.filter(name="upsight_staff").exists() or
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {
                    "error": "Permission denied",
                    "message": "Only staff members can update translation items."
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            translation = Translation.objects.get(id=translation_id)
        except Translation.DoesNotExist:
            return Response(
                {
                    "error": "Translation not found",
                    "message": f"Translation with ID {translation_id} does not exist."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        if request.user.groups.filter(name="university_staff").exists():
            user_university = get_user_university(request.user)
            if user_university != translation.university:
                return Response(
                    {
                        "error": "Permission denied",
                        "message": "You can only update translations from your own university."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Process form data
        data = process_form_data(request.data)
        
        if request.user.groups.filter(name="university_staff").exists():
            data['university'] = translation.university.id
        
        serializer = TranslationCreateUpdateSerializer(
            translation,
            data=data,
            partial=(request.method == "PATCH")
        )
        
        if serializer.is_valid():
            updated_translation = serializer.save()
            response_serializer = TranslationSerializer(updated_translation, context={"request": request})
            
            return Response(
                {
                    "success": True,
                    "message": "Translation updated successfully",
                    "data": {
                        "translation": response_serializer.data
                    }
                },
                status=status.HTTP_200_OK
            )
        
        return Response(
            {
                "success": False,
                "error": "Validation failed",
                "message": "Please check the form data and try again.",
                "field_errors": format_serializer_errors(serializer.errors)
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except Exception as e:
        return Response(
            {
                "success": False,
                "error": "Server error",
                "message": "An unexpected error occurred while updating the translation.",
                "details": str(e) if hasattr(e, '__str__') else "Unknown error"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def translation_delete(request, translation_id):
    """Delete translation item"""
    try:
        if not (request.user.groups.filter(name="upsight_staff").exists() or
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {"error": "Permission denied. Only staff can delete translations."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        translation = Translation.objects.get(id=translation_id)
        
        if request.user.groups.filter(name="university_staff").exists():
            user_university = get_user_university(request.user)
            if user_university != translation.university:
                return Response(
                    {"error": "Permission denied. You can only delete your university's translations."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        translation.delete()
        
        return Response(
            {"message": "Translation deleted successfully"},
            status=status.HTTP_200_OK
        )
    
    except Translation.DoesNotExist:
        return Response(
            {"error": "Translation not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "Failed to delete translation", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# Information Views
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def information_list(request):
    """Get list of information based on user role"""
    try:
        if not (request.user.groups.filter(name="upsight_staff").exists() or
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {"error": "Permission denied. Only staff can view information."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        information = (Information.objects.select_related('university')
                       .prefetch_related('documents').all().order_by('-date'))
        information = filter_by_permissions(information, request.user)
        serializer = InformationSerializer(information, many=True, context={"request": request})
        
        return Response(
            {
                "information": serializer.data,
                "total_count": len(serializer.data),
            },
            status=status.HTTP_200_OK,
        )
    
    except Exception as e:
        return Response(
            {"error": "Failed to fetch information", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def information_detail(request, information_id):
    """Get information details based on user role"""
    try:
        if not (request.user.groups.filter(name="upsight_staff").exists() or
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {"error": "Permission denied. Only staff can view information details."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        information = (Information.objects.select_related('university')
                       .prefetch_related('documents').get(id=information_id))
        
        if request.user.groups.filter(name="university_staff").exists():
            user_university = get_user_university(request.user)
            if user_university != information.university:
                return Response(
                    {"error": "Permission denied. You can only view your university's information."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = InformationSerializer(information, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Information.DoesNotExist:
        return Response(
            {"error": "Information not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "Failed to fetch information", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def information_create(request):
    """Create information item with enhanced form data handling"""
    try:
        if not (request.user.groups.filter(name="upsight_staff").exists() or
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {
                    "error": "Permission denied",
                    "message": "Only staff members can create information items."
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Process form data
        data = process_form_data(request.data)
        
        if request.user.groups.filter(name="university_staff").exists():
            user_university = get_user_university(request.user)
            if not user_university:
                return Response(
                    {
                        "error": "University not found",
                        "message": "Your user account is not associated with any university. Please contact support."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            data['university'] = user_university.id
        
        serializer = InformationCreateUpdateSerializer(data=data)
        if serializer.is_valid():
            information = serializer.save()
            response_serializer = InformationSerializer(information, context={"request": request})
            
            return Response(
                {
                    "success": True,
                    "message": "Information created successfully",
                    "data": {
                        "information": response_serializer.data
                    }
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            {
                "success": False,
                "error": "Validation failed",
                "message": "Please check the form data and try again.",
                "field_errors": format_serializer_errors(serializer.errors)
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except Exception as e:
        return Response(
            {
                "success": False,
                "error": "Server error",
                "message": "An unexpected error occurred while creating the information.",
                "details": str(e) if hasattr(e, '__str__') else "Unknown error"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def information_update(request, information_id):
    """Update information item with enhanced form data handling"""
    try:
        if not (request.user.groups.filter(name="upsight_staff").exists() or
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {
                    "error": "Permission denied",
                    "message": "Only staff members can update information items."
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            information = Information.objects.get(id=information_id)
        except Information.DoesNotExist:
            return Response(
                {
                    "error": "Information not found",
                    "message": f"Information with ID {information_id} does not exist."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        if request.user.groups.filter(name="university_staff").exists():
            user_university = get_user_university(request.user)
            if user_university != information.university:
                return Response(
                    {
                        "error": "Permission denied",
                        "message": "You can only update information from your own university."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Process form data
        data = process_form_data(request.data)
        
        if request.user.groups.filter(name="university_staff").exists():
            data['university'] = information.university.id
        
        serializer = InformationCreateUpdateSerializer(
            information,
            data=data,
            partial=(request.method == "PATCH")
        )
        
        if serializer.is_valid():
            updated_information = serializer.save()
            response_serializer = InformationSerializer(updated_information, context={"request": request})
            
            return Response(
                {
                    "success": True,
                    "message": "Information updated successfully",
                    "data": {
                        "information": response_serializer.data
                    }
                },
                status=status.HTTP_200_OK
            )
        
        return Response(
            {
                "success": False,
                "error": "Validation failed",
                "message": "Please check the form data and try again.",
                "field_errors": format_serializer_errors(serializer.errors)
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except Exception as e:
        return Response(
            {
                "success": False,
                "error": "Server error",
                "message": "An unexpected error occurred while updating the information.",
                "details": str(e) if hasattr(e, '__str__') else "Unknown error"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def information_delete(request, information_id):
    """Delete information item"""
    try:
        if not (request.user.groups.filter(name="upsight_staff").exists() or
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {"error": "Permission denied. Only staff can delete information."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        information = Information.objects.get(id=information_id)
        
        if request.user.groups.filter(name="university_staff").exists():
            user_university = get_user_university(request.user)
            if user_university != information.university:
                return Response(
                    {"error": "Permission denied. You can only delete your university's information."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        information.delete()
        
        return Response(
            {"message": "Information deleted successfully"},
            status=status.HTTP_200_OK
        )
    
    except Information.DoesNotExist:
        return Response(
            {"error": "Information not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "Failed to delete information", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# Information Documents Views
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def information_documents_list(request):
    """Get list of information documents based on user role"""
    try:
        if not (request.user.groups.filter(name="upsight_staff").exists() or
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {"error": "Permission denied. Only staff can view information documents."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        documents = InformationDocuments.objects.select_related('information__university').all()
        
        # Filter based on user permissions
        if request.user.groups.filter(name="university_staff").exists():
            user_university = get_user_university(request.user)
            if user_university:
                documents = documents.filter(information__university=user_university)
            else:
                documents = documents.none()
        
        serializer = InformationDocumentsSerializer(documents, many=True, context={"request": request})
        
        return Response(
            {
                "documents": serializer.data,
                "total_count": len(serializer.data),
            },
            status=status.HTTP_200_OK,
        )
    
    except Exception as e:
        return Response(
            {"error": "Failed to fetch information documents", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def information_document_detail(request, document_id):
    """Get information document details based on user role"""
    try:
        if not (request.user.groups.filter(name="upsight_staff").exists() or
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {"error": "Permission denied. Only staff can view information document details."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        document = InformationDocuments.objects.select_related('information__university').get(id=document_id)
        
        if request.user.groups.filter(name="university_staff").exists():
            user_university = get_user_university(request.user)
            if user_university != document.information.university:
                return Response(
                    {"error": "Permission denied. You can only view your university's information documents."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = InformationDocumentsSerializer(document, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except InformationDocuments.DoesNotExist:
        return Response(
            {"error": "Information document not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "Failed to fetch information document", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def information_document_create(request):
    """Create information document item with enhanced form data handling"""
    try:
        if not (request.user.groups.filter(name="upsight_staff").exists() or
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {
                    "error": "Permission denied",
                    "message": "Only staff members can create information documents."
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Process form data
        data = process_form_data(request.data)
        
        # Validate information belongs to user's university for university_staff
        if request.user.groups.filter(name="university_staff").exists():
            user_university = get_user_university(request.user)
            try:
                information = Information.objects.get(id=data.get('information'))
                if user_university != information.university:
                    return Response(
                        {
                            "error": "Permission denied",
                            "message": "You can only create documents for information from your own university."
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Information.DoesNotExist:
                return Response(
                    {
                        "error": "Information not found",
                        "message": "The specified information item does not exist."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            except (ValueError, TypeError):
                return Response(
                    {
                        "error": "Invalid information ID",
                        "message": "Please provide a valid information ID."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = InformationDocumentsCreateUpdateSerializer(data=data)
        if serializer.is_valid():
            document = serializer.save()
            response_serializer = InformationDocumentsSerializer(document, context={"request": request})
            
            return Response(
                {
                    "success": True,
                    "message": "Information document created successfully",
                    "data": {
                        "document": response_serializer.data
                    }
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            {
                "success": False,
                "error": "Validation failed",
                "message": "Please check the form data and try again.",
                "field_errors": format_serializer_errors(serializer.errors)
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except Exception as e:
        return Response(
            {
                "success": False,
                "error": "Server error",
                "message": "An unexpected error occurred while creating the document.",
                "details": str(e) if hasattr(e, '__str__') else "Unknown error"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def information_document_update(request, document_id):
    """Update information document item with enhanced form data handling"""
    try:
        if not (request.user.groups.filter(name="upsight_staff").exists() or
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {
                    "error": "Permission denied",
                    "message": "Only staff members can update information documents."
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            document = InformationDocuments.objects.select_related('information__university').get(id=document_id)
        except InformationDocuments.DoesNotExist:
            return Response(
                {
                    "error": "Document not found",
                    "message": f"Information document with ID {document_id} does not exist."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        if request.user.groups.filter(name="university_staff").exists():
            user_university = get_user_university(request.user)
            if user_university != document.information.university:
                return Response(
                    {
                        "error": "Permission denied",
                        "message": "You can only update documents from your own university."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Process form data
        data = process_form_data(request.data)
        
        serializer = InformationDocumentsCreateUpdateSerializer(
            document,
            data=data,
            partial=(request.method == "PATCH")
        )
        
        if serializer.is_valid():
            updated_document = serializer.save()
            response_serializer = InformationDocumentsSerializer(updated_document, context={"request": request})
            
            return Response(
                {
                    "success": True,
                    "message": "Information document updated successfully",
                    "data": {
                        "document": response_serializer.data
                    }
                },
                status=status.HTTP_200_OK
            )
        
        return Response(
            {
                "success": False,
                "error": "Validation failed",
                "message": "Please check the form data and try again.",
                "field_errors": format_serializer_errors(serializer.errors)
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except Exception as e:
        return Response(
            {
                "success": False,
                "error": "Server error",
                "message": "An unexpected error occurred while updating the document.",
                "details": str(e) if hasattr(e, '__str__') else "Unknown error"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def information_document_delete(request, document_id):
    """Delete information document item"""
    try:
        if not (request.user.groups.filter(name="upsight_staff").exists() or
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {"error": "Permission denied. Only staff can delete information documents."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        document = InformationDocuments.objects.select_related('information__university').get(id=document_id)
        
        if request.user.groups.filter(name="university_staff").exists():
            user_university = get_user_university(request.user)
            if user_university != document.information.university:
                return Response(
                    {"error": "Permission denied. You can only delete your university's information documents."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        document.delete()
        
        return Response(
            {"message": "Information document deleted successfully"},
            status=status.HTTP_200_OK
        )
    
    except InformationDocuments.DoesNotExist:
        return Response(
            {"error": "Information document not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "Failed to delete information document", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
