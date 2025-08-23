from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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
def news_create(request):
    """Create news item"""
    try:
        # Check permissions
        if not (request.user.groups.filter(name="upsight_staff").exists() or 
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {"error": "Permission denied. Only staff can create news."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        data = request.data.copy()
        
        # Set university for university_staff
        if request.user.groups.filter(name="university_staff").exists():
            user_university = get_user_university(request.user)
            if not user_university:
                return Response(
                    {"error": "University not found for user."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            data['university'] = user_university.id
        
        serializer = NewsCreateUpdateSerializer(data=data)
        if serializer.is_valid():
            news = serializer.save()
            response_serializer = NewsSerializer(news, context={"request": request})
            
            return Response(
                {
                    "message": "News created successfully",
                    "news": response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            {"error": "Invalid data", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except Exception as e:
        return Response(
            {"error": "Failed to create news", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def news_update(request, news_id):
    """Update news item"""
    try:
        # Check permissions
        if not (request.user.groups.filter(name="upsight_staff").exists() or 
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {"error": "Permission denied. Only staff can update news."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        news = News.objects.get(id=news_id)
        
        # Check if user can update this news
        if request.user.groups.filter(name="university_staff").exists():
            user_university = get_user_university(request.user)
            if user_university != news.university:
                return Response(
                    {"error": "Permission denied. You can only update your university's news."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        data = request.data.copy()
        
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
                    "message": "News updated successfully",
                    "news": response_serializer.data
                },
                status=status.HTTP_200_OK
            )
        
        return Response(
            {"error": "Invalid data", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except News.DoesNotExist:
        return Response(
            {"error": "News not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "Failed to update news", "details": str(e)},
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
def notice_create(request):
    """Create notice item"""
    try:
        if not (request.user.groups.filter(name="upsight_staff").exists() or
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {"error": "Permission denied. Only staff can create notices."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        data = request.data.copy()
        
        if request.user.groups.filter(name="university_staff").exists():
            user_university = get_user_university(request.user)
            if not user_university:
                return Response(
                    {"error": "University not found for user."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            data['university'] = user_university.id
        
        serializer = NoticeCreateUpdateSerializer(data=data)
        if serializer.is_valid():
            notice = serializer.save()
            response_serializer = NoticeSerializer(notice, context={"request": request})
            
            return Response(
                {
                    "message": "Notice created successfully",
                    "notice": response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            {"error": "Invalid data", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except Exception as e:
        return Response(
            {"error": "Failed to create notice", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def notice_update(request, notice_id):
    """Update notice item"""
    try:
        if not (request.user.groups.filter(name="upsight_staff").exists() or
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {"error": "Permission denied. Only staff can update notices."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        notice = Notice.objects.get(id=notice_id)
        
        if request.user.groups.filter(name="university_staff").exists():
            user_university = get_user_university(request.user)
            if user_university != notice.university:
                return Response(
                    {"error": "Permission denied. You can only update your university's notices."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        data = request.data.copy()
        
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
                    "message": "Notice updated successfully",
                    "notice": response_serializer.data
                },
                status=status.HTTP_200_OK
            )
        
        return Response(
            {"error": "Invalid data", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except Notice.DoesNotExist:
        return Response(
            {"error": "Notice not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "Failed to update notice", "details": str(e)},
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
def translation_create(request):
    """Create translation item"""
    try:
        if not (request.user.groups.filter(name="upsight_staff").exists() or
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {"error": "Permission denied. Only staff can create translations."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        data = request.data.copy()
        
        if request.user.groups.filter(name="university_staff").exists():
            user_university = get_user_university(request.user)
            if not user_university:
                return Response(
                    {"error": "University not found for user."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            data['university'] = user_university.id
        
        serializer = TranslationCreateUpdateSerializer(data=data)
        if serializer.is_valid():
            translation = serializer.save()
            response_serializer = TranslationSerializer(translation, context={"request": request})
            
            return Response(
                {
                    "message": "Translation created successfully",
                    "translation": response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            {"error": "Invalid data", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except Exception as e:
        return Response(
            {"error": "Failed to create translation", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def translation_update(request, translation_id):
    """Update translation item"""
    try:
        if not (request.user.groups.filter(name="upsight_staff").exists() or
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {"error": "Permission denied. Only staff can update translations."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        translation = Translation.objects.get(id=translation_id)
        
        if request.user.groups.filter(name="university_staff").exists():
            user_university = get_user_university(request.user)
            if user_university != translation.university:
                return Response(
                    {"error": "Permission denied. You can only update your university's translations."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        data = request.data.copy()
        
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
                    "message": "Translation updated successfully",
                    "translation": response_serializer.data
                },
                status=status.HTTP_200_OK
            )
        
        return Response(
            {"error": "Invalid data", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except Translation.DoesNotExist:
        return Response(
            {"error": "Translation not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "Failed to update translation", "details": str(e)},
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
def information_create(request):
    """Create information item"""
    try:
        if not (request.user.groups.filter(name="upsight_staff").exists() or
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {"error": "Permission denied. Only staff can create information."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        data = request.data.copy()
        
        if request.user.groups.filter(name="university_staff").exists():
            user_university = get_user_university(request.user)
            if not user_university:
                return Response(
                    {"error": "University not found for user."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            data['university'] = user_university.id
        
        serializer = InformationCreateUpdateSerializer(data=data)
        if serializer.is_valid():
            information = serializer.save()
            response_serializer = InformationSerializer(information, context={"request": request})
            
            return Response(
                {
                    "message": "Information created successfully",
                    "information": response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            {"error": "Invalid data", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except Exception as e:
        return Response(
            {"error": "Failed to create information", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def information_update(request, information_id):
    """Update information item"""
    try:
        if not (request.user.groups.filter(name="upsight_staff").exists() or
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {"error": "Permission denied. Only staff can update information."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        information = Information.objects.get(id=information_id)
        
        if request.user.groups.filter(name="university_staff").exists():
            user_university = get_user_university(request.user)
            if user_university != information.university:
                return Response(
                    {"error": "Permission denied. You can only update your university's information."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        data = request.data.copy()
        
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
                    "message": "Information updated successfully",
                    "information": response_serializer.data
                },
                status=status.HTTP_200_OK
            )
        
        return Response(
            {"error": "Invalid data", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except Information.DoesNotExist:
        return Response(
            {"error": "Information not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "Failed to update information", "details": str(e)},
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
def information_document_create(request):
    """Create information document item"""
    try:
        if not (request.user.groups.filter(name="upsight_staff").exists() or
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {"error": "Permission denied. Only staff can create information documents."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        data = request.data.copy()
        
        # Validate information belongs to user's university for university_staff
        if request.user.groups.filter(name="university_staff").exists():
            user_university = get_user_university(request.user)
            try:
                information = Information.objects.get(id=data.get('information'))
                if user_university != information.university:
                    return Response(
                        {"error": "Permission denied. You can only create documents "
                                  "for your university's information."},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Information.DoesNotExist:
                return Response(
                    {"error": "Information not found."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = InformationDocumentsCreateUpdateSerializer(data=data)
        if serializer.is_valid():
            document = serializer.save()
            response_serializer = InformationDocumentsSerializer(document, context={"request": request})
            
            return Response(
                {
                    "message": "Information document created successfully",
                    "document": response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            {"error": "Invalid data", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except Exception as e:
        return Response(
            {"error": "Failed to create information document", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def information_document_update(request, document_id):
    """Update information document item"""
    try:
        if not (request.user.groups.filter(name="upsight_staff").exists() or
                request.user.groups.filter(name="university_staff").exists()):
            return Response(
                {"error": "Permission denied. Only staff can update information documents."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        document = InformationDocuments.objects.select_related('information__university').get(id=document_id)
        
        if request.user.groups.filter(name="university_staff").exists():
            user_university = get_user_university(request.user)
            if user_university != document.information.university:
                return Response(
                    {"error": "Permission denied. You can only update your university's information documents."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = InformationDocumentsCreateUpdateSerializer(
            document,
            data=request.data,
            partial=(request.method == "PATCH")
        )
        
        if serializer.is_valid():
            updated_document = serializer.save()
            response_serializer = InformationDocumentsSerializer(updated_document, context={"request": request})
            
            return Response(
                {
                    "message": "Information document updated successfully",
                    "document": response_serializer.data
                },
                status=status.HTTP_200_OK
            )
        
        return Response(
            {"error": "Invalid data", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except InformationDocuments.DoesNotExist:
        return Response(
            {"error": "Information document not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "Failed to update information document", "details": str(e)},
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
