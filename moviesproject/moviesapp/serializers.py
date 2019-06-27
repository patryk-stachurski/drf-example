from rest_framework import serializers

from . import models


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Rating
        fields = ('source', 'value',)


class MovieListSerializer(serializers.ModelSerializer):
    ratings = RatingSerializer(many=True)

    class Meta:
        model = models.Movie
        fields = (
            'id', 'actors', 'awards', 'box_office', 'country', 'dvd', 'director', 'genre', 'language', 'metascore', 'plot',
            'poster', 'production', 'rated', 'released', 'runtime', 'title', 'type', 'website', 'writer', 'year',
            'imdb_id', 'imdb_rating', 'imdb_votes', 'ratings',
        )

    def create(self, validated_data):
        ratings = validated_data.pop('ratings')

        movie = models.Movie.objects.create(**validated_data)

        for rating_data in ratings:
            models.Rating.objects.create(movie=movie, **rating_data)
        return movie


class MovieCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Movie
        fields = ('title',)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Comment
        fields = ('content', 'movie', 'created_at',)


class TopMovieSerializer(serializers.ModelSerializer):
    movie_id = serializers.IntegerField(source='id')
    total_comments = serializers.IntegerField()
    rank = serializers.IntegerField()

    class Meta:
        model = models.Movie
        fields = (
            'movie_id', 'total_comments', 'rank'
        )
