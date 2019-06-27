import re
import os
import collections

import requests
from dateutil.parser import parse as datetime_from_string


class OMDB(object):
    API_BASE_URL = 'http://www.omdbapi.com/'
    API_KEY = os.environ['OMDB_API_KEY']

    NON_DIGIT_PATTERN = re.compile(r'\D')

    @classmethod
    def _to_snake_case(cls, text):
        s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', text)
        return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    @classmethod
    def _dict_keys_to_snake_case(cls, d):
        data = {cls._to_snake_case(key): value for key, value in d.items()}

        for k, v in data.items():
            # Skip string values as they are iterable also
            if isinstance(v, str):
                continue

            if isinstance(v, dict):
                data[k] = cls._dict_keys_to_snake_case(v)

            elif isinstance(v, collections.Iterable):
                new_items = []
                for item in v:
                    if isinstance(item, (dict, collections.Iterable)):
                        new_items.append(cls._dict_keys_to_snake_case(item))
                    else:
                        new_items.append(item)

                data[k] = new_items

        return data

    @classmethod
    def _convert_data(cls, data):
        data = {cls._to_snake_case(key): value for key, value in data.items()}

        data['released'] = datetime_from_string(data['released']).date()
        data['imdb_votes'] = int(cls.NON_DIGIT_PATTERN.sub('', data['imdb_votes']))
        data['metascore'] = int(cls.NON_DIGIT_PATTERN.sub('', data['metascore']))

        return data

    @classmethod
    def get_movie_by_title(cls, title):
        params = {
            'apikey': cls.API_KEY,
            't': title,
            'plot': 'full'
        }
        response = requests.get(cls.API_BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        data = cls._dict_keys_to_snake_case(data)

        response_status = data.pop('response', None)
        if response_status != 'True':
            raise requests.HTTPError('movie with title %r not found' % title)

        return cls._convert_data(data)
