from django.db.models import Window, Count, Q, F
from django.db.models.functions import DenseRank

from moviesproject import filters

from . import models


class CommentFilterSet(filters.FilterSet):
    movie = filters.ModelChoiceFilter(queryset=models.Movie.objects.all())
    search = filters.CharFilter(field_name='content', lookup_expr='icontains')


class TopMovieFilterSet(filters.FilterSet):
    movie_id = filters.NumberInFilter(field_name='id', lookup_expr='in')

    comments_after = filters.DateTimeFilter(required=True, method='filter_comments_after')
    comments_before = filters.DateTimeFilter(required=True, method='no_filter')

    @staticmethod
    def no_filter(query, field_name, value):
        return query

    def filter_comments_after(self, query, field_name, value):
        before_str = self.request.query_params.get('comments_before', None)

        before = self.declared_filters['comments_before'].field.to_python(before_str)

        return query.annotate(
            total_comments=Count(
                expression='comments',
                filter=Q(
                    comments__created_at__gt=value,
                    comments__created_at__lt=before
                )
            ),
            rank=Window(
                expression=DenseRank(),
                order_by=F('total_comments').desc()
            )
        )
