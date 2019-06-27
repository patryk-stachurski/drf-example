import unittest
import datetime
import json
from unittest.mock import patch

import requests
import requests_mock

from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.serializers import DateTimeField

from moviesapp.omdb import OMDB
from . import models


BATMAN_OMDB_JSON_RESPONSE = {
    'Title': 'Batman',
    'Year': '1989',
    'Rated': 'PG-13',
    'Released': '23 Jun 1989',
    'Runtime': '126 min',
    'Genre': 'Action, Adventure',
    'Director': 'Tim Burton',
    'Writer': 'Bob Kane (Batman characters), Sam Hamm (story), Sam Hamm (screenplay), Warren Skaaren (screenplay)',
    'Actors': 'Michael Keaton, Jack Nicholson, Kim Basinger, Robert Wuhl',
    'Plot': "Gotham City.",
    'Language': 'English, French, Spanish', 'Country': 'USA, UK',
    'Awards': 'Won 1 Oscar. Another 8 wins & 26 nominations.',
    'Poster': 'https://m.media-amazon.com/images/M/MV5BMTYwNjAyODIyMF5BMl5BanBnXkFtZTYwNDMwMDk2._V1_SX300.jpg',
    'Ratings': [
        {'Source': 'Internet Movie Database', 'Value': '7.6/10'},
        {'Source': 'Rotten Tomatoes', 'Value': '71%'},
        {'Source': 'Metacritic', 'Value': '69/100'}],
    'Metascore': '69',
    'imdbRating': '7.6',
    'imdbVotes': '311,189',
    'imdbID': 'tt0096895',
    'Type': 'movie',
    'DVD': '25 Mar 1997',
    'BoxOffice': 'N/A',
    'Production': 'Warner Bros. Pictures',
    'Website': 'N/A',
    'Response': 'True'
}

BATMAN_API_JSON_RESPONSE = {
    'actors': 'Michael Keaton, Jack Nicholson, Kim Basinger, Robert Wuhl',
    'awards': 'Won 1 Oscar. Another 8 wins & 26 nominations.',
    'box_office': 'N/A',
    'country': 'USA, UK',
    'director': 'Tim Burton',
    'dvd': '25 Mar 1997',
    'genre': 'Action, Adventure',
    'imdb_id': 'tt0096895',
    'imdb_rating': '7.6',
    'imdb_votes': 311189,
    'language': 'English, French, Spanish',
    'metascore': 69,
    'plot': 'Gotham City.',
    'poster': 'https://m.media-amazon.com/images/M/MV5BMTYwNjAyODIyMF5BMl5BanBnXkFtZTYwNDMwMDk2._V1_SX300.jpg',
    'production': 'Warner Bros. Pictures',
    'rated': 'PG-13',
    'ratings': [{'source': 'Internet Movie Database', 'value': '7.6/10'},
                {'source': 'Metacritic', 'value': '69/100'},
                {'source': 'Rotten Tomatoes', 'value': '71%'}],
    'released': '1989-06-23',
    'runtime': '126 min',
    'title': 'Batman',
    'type': 'movie',
    'website': 'N/A',
    'writer': 'Bob Kane (Batman characters), Sam Hamm (story), Sam Hamm '
              '(screenplay), Warren Skaaren (screenplay)',
    'year': 1989
}


def remove_key(obj, key):
    if isinstance(obj, dict):
        result = obj.copy()
        result.pop(key, None)
        return result

    elif isinstance(obj, list):
        return [remove_key(item, key) for item in obj]

    else:
        return obj


def remove_ids(obj):
    return remove_key(obj, 'id')


def dt_to_rest_repr(dt):
    return DateTimeField().to_representation(dt)


class PatchServerTime(object):
    def __init__(self, desired_time=None):
        if desired_time is None:
            desired_time = timezone.now()
        self.desired_time = desired_time

    def __enter__(self):
        self.patch = patch('django.utils.timezone.now')
        self.mock = self.patch.__enter__()
        self.mock.return_value = self.desired_time
        return self.desired_time

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.patch.__exit__(exc_type, exc_val, exc_tb)


patch_server_time = PatchServerTime


class OMDBClientTests(unittest.TestCase):
    maxDiff = None

    def test_to_snake_case(self):
        self.assertEqual(
            OMDB._to_snake_case('Title'),
            'title'
        )
        self.assertEqual(
            OMDB._to_snake_case('imdbRating'),
            'imdb_rating'
        )
        self.assertEqual(
            OMDB._to_snake_case('DVD'),
            'dvd'
        )
        self.assertEqual(
            OMDB._to_snake_case('already_snake_case'),
            'already_snake_case'
        )

    def test_dict_keys_to_snake_case(self):
        self.assertEqual(
            OMDB._dict_keys_to_snake_case(
                {
                    'Title': '',
                    'imdbRating': '',
                    'Ratings': [
                        {'Source': '', 'Value': ''},
                        {'Source': '', 'Value': ''}
                    ]
                }
            ),
            {
                'title': '',
                'imdb_rating': '',
                'ratings': [
                    {'source': '', 'value': ''},
                    {'source': '', 'value': ''}
                ]
            }
        )

    def test_get_movie_successfully(self):
        with requests_mock.mock() as m:
            m.get('http://www.omdbapi.com/', json=BATMAN_OMDB_JSON_RESPONSE)

            response_data = OMDB.get_movie_by_title('batman')

        self.assertEqual(
            response_data,
            {
                'actors': 'Michael Keaton, Jack Nicholson, Kim Basinger, Robert Wuhl',
                'awards': 'Won 1 Oscar. Another 8 wins & 26 nominations.',
                'box_office': 'N/A',
                'country': 'USA, UK',
                'director': 'Tim Burton',
                'dvd': '25 Mar 1997',
                'genre': 'Action, Adventure',
                'imdb_id': 'tt0096895',
                'imdb_rating': '7.6',
                'imdb_votes': 311189,
                'language': 'English, French, Spanish',
                'metascore': 69,
                'plot': 'Gotham City.',
                'poster': 'https://m.media-amazon.com/images/M/MV5BMTYwNjAyODIyMF5BMl5BanBnXkFtZTYwNDMwMDk2._V1_SX300.jpg',
                'production': 'Warner Bros. Pictures',
                'rated': 'PG-13',
                'ratings': [{'source': 'Internet Movie Database', 'value': '7.6/10'},
                            {'source': 'Rotten Tomatoes', 'value': '71%'},
                            {'source': 'Metacritic', 'value': '69/100'}],
                'released': datetime.date(1989, 6, 23),
                'runtime': '126 min',
                'title': 'Batman',
                'type': 'movie',
                'website': 'N/A',
                'writer': 'Bob Kane (Batman characters), Sam Hamm (story), Sam Hamm '
                          '(screenplay), Warren Skaaren (screenplay)',
                'year': '1989'
            }
        )

    def test_get_movie_which_can_not_be_found(self):
        with requests_mock.mock() as m:
            m.get('http://www.omdbapi.com/', json={'Response': 'False'})

            with self.assertRaises(requests.exceptions.HTTPError):
                OMDB.get_movie_by_title('movie title that for sure will not be found')

    def test_get_movie_with_no_response(self):
        with requests_mock.mock() as m:
            m.get('http://www.omdbapi.com/')

            with self.assertRaises(json.decoder.JSONDecodeError):
                OMDB.get_movie_by_title('batman')

    def test_get_movie_with_empty_response(self):
        with requests_mock.mock() as m:
            m.get('http://www.omdbapi.com/', json={})

            with self.assertRaises(requests.exceptions.HTTPError):
                OMDB.get_movie_by_title('batman')


def create_batman_movie():
    data = BATMAN_API_JSON_RESPONSE.copy()
    ratings = data.pop('ratings')

    movie = models.Movie.objects.create(
        **data
    )
    for rating_data in ratings:
        models.Rating.objects.create(movie=movie, **rating_data)
    return movie


def create_comment(movie, content):
    comment = models.Comment.objects.create(
        movie=movie,
        content=content
    )
    return comment


class MovieListCreateTests(APITestCase):
    maxDiff = None
    url = reverse('api:movie-list')

    def test_put_is_not_allowed(self):
        response = self.client.put(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_delete_is_not_allowed(self):
        response = self.client.delete(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_list_empty(self):
        with self.assertNumQueries(1):
            response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            response.json(),
            []
        )

    def test_list_single(self):
        create_batman_movie()

        with self.assertNumQueries(2):
            response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            remove_ids(response.json()),
            [BATMAN_API_JSON_RESPONSE]
        )

    def test_list_many(self):
        create_batman_movie()
        create_batman_movie()
        create_batman_movie()

        with self.assertNumQueries(2):
            response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            remove_ids(response.json()),
            [BATMAN_API_JSON_RESPONSE, BATMAN_API_JSON_RESPONSE, BATMAN_API_JSON_RESPONSE]
        )

    def test_create_first(self):
        data = {'title': 'batman'}

        with self.assertNumQueries(5):
            with requests_mock.mock() as m:
                m.get('http://www.omdbapi.com/', json=BATMAN_OMDB_JSON_RESPONSE)

                response = self.client.post(self.url, data, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
        self.assertEqual(
            remove_ids(response.json()),
            BATMAN_API_JSON_RESPONSE
        )

        with self.assertNumQueries(2):
            response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            remove_ids(response.json()),
            [BATMAN_API_JSON_RESPONSE]
        )

    def test_create_another(self):
        create_batman_movie()

        data = {'title': 'batman'}

        with self.assertNumQueries(5):
            with requests_mock.mock() as m:
                m.get('http://www.omdbapi.com/', json=BATMAN_OMDB_JSON_RESPONSE)

                response = self.client.post(self.url, data, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
        self.assertEqual(
            remove_ids(response.json()),
            BATMAN_API_JSON_RESPONSE
        )

        with self.assertNumQueries(2):
            response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            remove_ids(response.json()),
            [BATMAN_API_JSON_RESPONSE, BATMAN_API_JSON_RESPONSE]
        )

    def test_create_no_input(self):
        with self.assertNumQueries(0):
            response = self.client.post(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            response.json(),
            {
                'title': ['This field is required.']
            }
        )

    def test_create_not_existing(self):
        data = {'title': 'NotExistingMovieTitle'}

        with self.assertNumQueries(0):
            with requests_mock.mock() as m:
                m.get('http://www.omdbapi.com/', json={'Response': 'False'})

                response = self.client.post(self.url, data, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            response.content,
            b''
        )

        with self.assertNumQueries(1):
            response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            response.json(),
            []
        )


class CommentListCreateTests(APITestCase):
    url = reverse('api:comment-list')
    maxDiff = None

    def create_batman_movie(self):
        movie_url = reverse('api:movie-list')
        data = {'title': 'batman'}

        response = self.client.post(movie_url, data, format='json')
        return response.json()

    def test_put_is_not_allowed(self):
        response = self.client.put(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_delete_is_not_allowed(self):
        response = self.client.delete(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_list_empty(self):
        with self.assertNumQueries(1):
            response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            response.json(),
            []
        )

    def test_list_single(self):
        movie = create_batman_movie()

        comment = create_comment(movie, 'First comment!')

        with self.assertNumQueries(1):
            response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            response.json(),
            [
                {
                    'content': 'First comment!',
                    'movie': movie.id,
                    'created_at': dt_to_rest_repr(comment.created_at)
                }
            ]
        )

    def test_list_many(self):
        first_movie = create_batman_movie()
        second_movie = create_batman_movie()

        first_comment = create_comment(first_movie, 'First comment!')
        second_comment = create_comment(first_movie, 'Second comment.')
        third_comment = create_comment(second_movie, 'Third comment but to second movie')

        with self.assertNumQueries(1):
            response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            response.json(),
            [
                {
                    'content': 'First comment!',
                    'movie': first_movie.id,
                    'created_at': dt_to_rest_repr(first_comment.created_at)
                },
                {
                    'content': 'Second comment.',
                    'movie': first_movie.id,
                    'created_at': dt_to_rest_repr(second_comment.created_at)
                },
                {
                    'content': 'Third comment but to second movie',
                    'movie': second_movie.id,
                    'created_at': dt_to_rest_repr(third_comment.created_at)
                }
            ]
        )

    def test_list_filtered_by_movie(self):
        first_movie = create_batman_movie()
        second_movie = create_batman_movie()

        first_comment = create_comment(first_movie, 'First comment!')
        second_comment = create_comment(first_movie, 'Second comment.')
        third_comment = create_comment(second_movie, 'Third comment but to second movie')

        with self.assertNumQueries(3):
            response = self.client.get(self.url, {'movie': first_movie.id})

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            response.json(),
            [
                {
                    'content': 'First comment!',
                    'movie': first_movie.id,
                    'created_at': dt_to_rest_repr(first_comment.created_at)
                },
                {
                    'content': 'Second comment.',
                    'movie': first_movie.id,
                    'created_at': dt_to_rest_repr(second_comment.created_at)
                }
            ]
        )

        with self.assertNumQueries(3):
            response = self.client.get(self.url, {'movie': second_movie.id})

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            response.json(),
            [
                {
                    'content': 'Third comment but to second movie',
                    'movie': second_movie.id,
                    'created_at': dt_to_rest_repr(third_comment.created_at)
                }
            ]
        )

    def test_create_first(self):
        movie = create_batman_movie()

        input_data = {
            'movie': movie.id,
            'content': 'First comment!!!'
        }

        with self.assertNumQueries(2):
            with patch_server_time() as patched_time:
                response = self.client.post(self.url, input_data, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
        self.assertEqual(
            response.json(),
            {
                'content': 'First comment!!!',
                'movie': movie.id,
                'created_at': dt_to_rest_repr(patched_time)
            }
        )

    def test_create_another(self):
        movie = create_batman_movie()
        first_comment = create_comment(movie, 'First already existing comment')

        input_data = {
            'movie': movie.id,
            'content': 'Second comment.'
        }

        with self.assertNumQueries(2):
            with patch_server_time() as patched_time:
                response = self.client.post(self.url, input_data, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
        self.assertEqual(
            response.json(),
            {
                'content': 'Second comment.',
                'movie': movie.id,
                'created_at': dt_to_rest_repr(patched_time)
            }
        )

        with self.assertNumQueries(1):
            response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            response.json(),
            [
                {
                    'content': first_comment.content,
                    'movie': movie.id,
                    'created_at': dt_to_rest_repr(first_comment.created_at)
                },
                {
                    'content': 'Second comment.',
                    'movie': movie.id,
                    'created_at': dt_to_rest_repr(patched_time)
                }
            ]
        )

    def test_create_no_input(self):
        with self.assertNumQueries(0):
            response = self.client.post(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            response.json(),
            {
                'content': ['This field is required.'],
                'movie': ['This field is required.']
            }
        )

    def test_create_wrong_movie(self):
        input_data = {
            'movie': 123456789,
            'content': 'First comment!!!'
        }

        with self.assertNumQueries(1):
            response = self.client.post(self.url, input_data, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            response.json(),
            {
                'movie': ['Invalid pk "123456789" - object does not exist.']
            }
        )


class TopMovieTests(APITestCase):
    url = reverse('api:top-movies-list')
    maxDiff = None

    def test_put_is_not_allowed(self):
        response = self.client.put(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_post_is_not_allowed(self):
        response = self.client.post(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_delete_is_not_allowed(self):
        response = self.client.delete(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_list_no_params(self):
        with self.assertNumQueries(0):
            response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            response.json(),
            {
                'comments_after': ['This field is required.'],
                'comments_before': ['This field is required.']
            }
        )

    def test_list_empty(self):
        params = {
            'comments_after': '2019-06-30',
            'comments_before': '2019-07-31'
        }

        with self.assertNumQueries(1):
            response = self.client.get(self.url, params)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            response.json(),
            []
        )

    def test_list_single(self):
        first_movie = create_batman_movie()
        second_movie = create_batman_movie()

        first_comment = create_comment(first_movie, 'First comment!')
        first_time = first_comment.created_at.astimezone(timezone.get_current_timezone())

        params = {
            'comments_after': first_time.strftime('%Y-%m-%d %H:%M:%S'),
            'comments_before': (first_time + datetime.timedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S'),
        }

        with self.assertNumQueries(1):
            response = self.client.get(self.url, params)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            response.json(),
            [
                {'movie_id': first_movie.id, 'rank': 1, 'total_comments': 1},
                {'movie_id': second_movie.id, 'rank': 2, 'total_comments': 0}
            ]
        )

        params['comments_after'] = (first_time + datetime.timedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S'),
        params['comments_before'] = (first_time + datetime.timedelta(seconds=2)).strftime('%Y-%m-%d %H:%M:%S'),

        with self.assertNumQueries(1):
            response = self.client.get(self.url, params)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            response.json(),
            [
                {'movie_id': first_movie.id, 'rank': 1, 'total_comments': 0},
                {'movie_id': second_movie.id, 'rank': 1, 'total_comments': 0}
            ]
        )
