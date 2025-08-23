from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Carousel, News, Person, Gallery, AboutUs, Feedback, GalleryItem, Report
from .serializers import CarouselSerializer, NewsSerializer, FeedbackSerializer, ExperienceSerializer, PersonSerializer, GallerySerializer, GalleryItemSerializer, AboutUsSerializer, ReportSerializer


class CarouselViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Carousel.objects.all()
    serializer_class = CarouselSerializer


class NewsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = News.objects.all().order_by('-id')
    serializer_class = NewsSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['language'] = self.request.GET.get('language', 'ko')  # Default to Korean
        return context


class PersonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['language'] = self.request.GET.get('language', 'ko')  # Default to Korean
        return context

    @action(detail=True, methods=['get'])
    def experiences(self, request, pk=None):
        person = self.get_object()
        experiences = person.experiences.all()
        serializer = ExperienceSerializer(experiences, many=True, context={'language': self.request.GET.get('language', 'ko')})
        return Response(serializer.data)


class GalleryItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GalleryItem.objects.all()
    serializer_class = GalleryItemSerializer

    def retrieve(self, request, gallery_pk=None, pk=None):
        queryset = self.get_queryset().filter(gallery_id=gallery_pk)
        gallery_item = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(gallery_item)
        return Response(serializer.data)
        
        
class GalleryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['language'] = self.request.GET.get('language', 'ko')  # Default to Korean
        return context

    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        gallery = self.get_object()
        items = gallery.items.all()
        serializer = GalleryItemSerializer(items, many=True, context={'language': self.request.GET.get('language', 'ko')})
        return Response(serializer.data)


class AboutUsViewSet(viewsets.ModelViewSet):
    queryset = AboutUs.objects.all()
    serializer_class = AboutUsSerializer


class FeedbackViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['language'] = self.request.GET.get('language', 'ko')  # Default to Korean
        return context
        
        
class ReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer