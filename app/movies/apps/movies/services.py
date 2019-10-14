import json

import requests
from django.conf import settings
from django.utils import timezone

from movies.apps.movies import models


class OMDBAPI:
    url = "http://www.omdbapi.com"

    def get_movie(self, title):
        """
        :param title: title of movie to be requested.
        :return: (dict, None or string)  # Tuple of response content and error. Error is None if request was successful.
        """
        response = requests.get(
            OMDBAPI.url,
            params={
                't': title,
                'apikey': settings.OMDB_API_KEY
            }
        )
        content = json.loads(response.content)
        if 'Error' in content:
            return {}, content['Error']
        else:
            return content, None


def get_or_create_movie_by_title(title):
    movie = models.Movie.objects.filter(external_data__title__iexact=title).first()

    # movie doesn't exist in database, get data from external API
    if movie is None:
        movie_data, error = OMDBAPI().get_movie(title)

        # fetched movie data successfully, create it in database
        if error is None:
            movie = models.Movie.objects.create_with_external_data(movie_data)
            return movie.serialize(), None
        # fetch failed, return empty dict and error
        else:
            return {}, error
    # movie exists in database, return it
    else:
        return movie.serialize(), None


def add_comment_to_movie(movie_id, comment):
    movie = models.Movie.objects.filter(pk=movie_id).first()

    if movie:
        comment = models.Comment.objects.create(movie=movie, comment=comment, added_on=timezone.now())
        return comment.serialize(), None
    else:
        return {}, models.Movie.DoesNotExist(f'Movie with id {movie_id} does not exist.')
