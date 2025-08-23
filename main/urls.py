from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CarouselViewSet, NewsViewSet, PersonViewSet, GalleryViewSet, AboutUsViewSet, FeedbackViewSet, GalleryItemViewSet, ReportViewSet

router = DefaultRouter()
router.register(r'carousel', CarouselViewSet)
router.register(r'news', NewsViewSet)
router.register(r'person', PersonViewSet)
router.register(r'gallery', GalleryViewSet)
router.register(r'aboutus', AboutUsViewSet)
router.register(r'feedback', FeedbackViewSet)
router.register(r'report', ReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('news/<int:pk>/', NewsViewSet.as_view({'get': 'retrieve',})),
    path('gallery/<int:gallery_pk>/items/<int:pk>/', GalleryItemViewSet.as_view({'get': 'retrieve'}), name='gallery-item-detail'),
]

