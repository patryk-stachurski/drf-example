from rest_framework import routers

from moviesapp import views


router = routers.DefaultRouter()
router.register(r'movies', views.MovieViewset)
router.register(r'comments', views.CommentViewset)
router.register(r'top-movies', views.TopMovieViewset, 'top-movies')
