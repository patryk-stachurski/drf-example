from django.http import HttpResponseBadRequest

from rest_framework import viewsets, mixins, status
from rest_framework.response import Response


from . import models
from . import serializers
from . import filters
from .omdb import OMDB


class MovieViewset(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   viewsets.GenericViewSet):

    queryset = models.Movie.objects.all().prefetch_related('ratings')

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.MovieCreateSerializer

        elif self.action == 'list':
            return serializers.MovieListSerializer

        raise NotImplementedError('the viewset does not implement action {action!r}'.format(action=self.action))

    def create(self, request, *args, **kwargs):
        write_serializer = serializers.MovieCreateSerializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)

        try:
            full_data = OMDB.get_movie_by_title(write_serializer.data['title'])
        except:
            return HttpResponseBadRequest()

        read_serializer = serializers.MovieListSerializer(data=full_data)
        read_serializer.is_valid(raise_exception=True)
        instance = read_serializer.save()

        return Response(serializers.MovieListSerializer(instance).data, status=status.HTTP_201_CREATED)


class CommentViewset(mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                     viewsets.GenericViewSet):

    queryset = models.Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    filterset_class = filters.CommentFilterSet


class TopMovieViewset(mixins.ListModelMixin,
                      viewsets.GenericViewSet):

    queryset = models.Movie.objects
    serializer_class = serializers.TopMovieSerializer
    filterset_class = filters.TopMovieFilterSet
