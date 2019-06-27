from django.db import models
from django.core import validators


class Movie(models.Model):
    actors = models.CharField(max_length=200)
    awards = models.CharField(max_length=200)
    box_office = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    dvd = models.CharField(max_length=200)
    director = models.CharField(max_length=200)
    genre = models.CharField(max_length=200)
    language = models.CharField(max_length=200)
    metascore = models.IntegerField(validators=[
        validators.MinValueValidator(0),
        validators.MaxValueValidator(100),
    ])
    plot = models.CharField(max_length=1000)
    poster = models.CharField(max_length=200)
    production = models.CharField(max_length=200)
    rated = models.CharField(max_length=200)
    released = models.DateField()
    runtime = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    website = models.CharField(max_length=200)
    writer = models.CharField(max_length=200)
    year = models.IntegerField()
    imdb_id = models.CharField(max_length=200)
    imdb_rating = models.DecimalField(decimal_places=1, max_digits=3)
    imdb_votes = models.IntegerField(validators=[
        validators.MinValueValidator(0),
    ])

    class Meta:
        ordering = ['id']

    def __str__(self):
        return '{self.title} (id={self.id})'.format(self=self)


class Rating(models.Model):
    movie = models.ForeignKey(Movie, related_name='ratings', on_delete=models.CASCADE)

    source = models.CharField(max_length=200)
    value = models.CharField(max_length=200)

    class Meta:
        ordering = ['source']


class Comment(models.Model):
    movie = models.ForeignKey(Movie, related_name='comments', on_delete=models.CASCADE)

    content = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['movie', 'created_at']
