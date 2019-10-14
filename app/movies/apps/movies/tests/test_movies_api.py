import json
from datetime import datetime

import pytest
import pytz

from movies.apps.movies import api_views, models
from movies.utils_tests import request_factory, freeze_now

pytestmark = pytest.mark.django_db
usefixtures = pytest.mark.usefixtures

fixture_names = ['django_db_setup', 'mock_omdb_api', 'request_factory', 'freeze_now']


def dt(y, m, d):
    return datetime(year=y, month=m, day=d, tzinfo=pytz.UTC)


@pytest.fixture(scope='module')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        movies = models.Movie.objects.bulk_create(
            models.Movie(**data)
            for data in [
                {'external_data': {'Title': 'Pirates of the Caribbean', 'Director': 'Gore Verbinski', 'Year': '2003'}},
                {'external_data': {'Title': 'Game of Thrones', 'Director': 'N/A', 'Year': '2011-'}},
                {'external_data': {'Title': 'Django', 'Director': 'Sergio Corbucci', 'Year': '1966'}},
                {'external_data': {'Title': 'Matrix', 'Director': 'N/A', 'Year': '1993-'}},
                {'external_data': {'Title': 'Cube', 'Director': 'Vincenzo Natali', 'Year': '1997'}},
                {'external_data': {'Title': 'Star Wars: Episode IV - A New Hope', 'Director': 'George Lucas', 'Year': '1977'}},
                {'external_data': {'Title': 'Star Wars: Episode V - The Empire Strikes Back', 'Director': 'Irvin Kershner', 'Year': '1980'}},
                {'external_data': {'Title': 'Fight Club', 'Director': 'David Fincher', 'Year': '1999'}},
                {'external_data': {'Title': '2001: A Space Odyssey', 'Director': 'Stanley Kubrick', 'Year': '1968'}},
                {'external_data': {'Title': 'Jumanji', 'Director': 'Joe Johnston', 'Year': '1995'}},
                {'external_data': {'Title': 'The Chronicles of Narnia: The Lion, the Witch and the Wardrobe', 'Director': '"Andrew Adamson"', 'Year': '2005'}},
                {'external_data': {'Title': 'Bridge to Terabithia', 'Director': 'Gabor Csupo', 'Year': '2007'}},
            ]
        )

        models.Comment.objects.bulk_create(
            models.Comment(**data)
            for data in [
                # 0
                {'movie_id': movies[0].pk, 'comment': '10/10', 'added_on': dt(2019, 10, 10)},
                {'movie_id': movies[0].pk, 'comment': 'Ok', 'added_on': dt(2019, 10, 11)},
                {'movie_id': movies[0].pk, 'comment': 'Worth it.', 'added_on': dt(2019, 10, 12)},
                # 1
                {'movie_id': movies[1].pk, 'comment': 'Bad.', 'added_on': dt(2019, 10, 10)},
                {'movie_id': movies[1].pk, 'comment': 'OK.', 'added_on': dt(2019, 10, 12)},
                # 2
                {'movie_id': movies[2].pk, 'comment': 'Enjoyed it.', 'added_on': dt(2019, 10, 11)},
                {'movie_id': movies[2].pk, 'comment': 'Could be better.', 'added_on': dt(2019, 10, 11)},
                {'movie_id': movies[2].pk, 'comment': '3/10', 'added_on': dt(2019, 10, 11)},
                {'movie_id': movies[2].pk, 'comment': 'Worth watching.', 'added_on': dt(2019, 10, 12)},
                {'movie_id': movies[2].pk, 'comment': 'Really good.', 'added_on': dt(2019, 10, 12)},
                # 3
                {'movie_id': movies[3].pk, 'comment': 'Dropped halfway through.', 'added_on': dt(2019, 10, 9)},
                {'movie_id': movies[3].pk, 'comment': 'Not that bad.', 'added_on': dt(2019, 10, 9)},
                {'movie_id': movies[3].pk, 'comment': '5/10 would not recommend.', 'added_on': dt(2019, 10, 9)},
                {'movie_id': movies[3].pk, 'comment': 'Don\'t watch', 'added_on': dt(2019, 10, 10)},
                {'movie_id': movies[3].pk, 'comment': 'Pretty good.', 'added_on': dt(2019, 10, 11)},
                # 4
                {'movie_id': movies[4].pk, 'comment': 'Got lost in it.', 'added_on': dt(2019, 10, 9)},
                {'movie_id': movies[4].pk, 'comment': 'Too scary.', 'added_on': dt(2019, 10, 10)},
            ]
        )


@pytest.fixture(scope='function')
def mock_omdb_api(monkeypatch):
    def fake_get_movie(self, title):
        if title == 'Existing':
            return {'Title': 'Existing'}, None
        else:
            return {}, 'Movie does not exist.'

    monkeypatch.setattr("movies.apps.movies.services.OMDBAPI.get_movie", fake_get_movie)


@usefixtures(*fixture_names)
def test_movies_post_title_valid(rf):
    request = rf.post('/movies', data={'title': 'Existing'})
    response = api_views.MoviesView.as_view()(request)
    assert response.status_code == 200
    assert response.data == {'Title': 'Existing', 'id': models.Movie.objects.all().last().pk}


@usefixtures(*fixture_names)
def test_movies_post_title_invalid(rf):
    request = rf.post('/movies', data={'title': 'Non-existent'})
    response = api_views.MoviesView.as_view()(request)
    assert response.status_code == 404
    assert response.data == {'error': 'Movie does not exist.'}


@usefixtures(*fixture_names)
def test_movies_post_no_title(rf):
    request = rf.post('/movies', data={})
    response = api_views.MoviesView.as_view()(request)
    assert response.status_code == 400
    assert response.data == {'title': 'This field is required.'}


@usefixtures(*fixture_names)
def test_movies_get(rf):
    request = rf.get('/movies')
    response = api_views.MoviesView.as_view()(request)
    response_content = response.data
    assert response.status_code == 200
    assert len(response_content['results']) == 10
    assert response_content == {
        'results': [
            {'id': 1, 'Title': 'Pirates of the Caribbean', 'Director': 'Gore Verbinski', 'Year': '2003'},
            {'id': 2, 'Title': 'Game of Thrones', 'Director': 'N/A', 'Year': '2011-'},
            {'id': 3, 'Title': 'Django', 'Director': 'Sergio Corbucci', 'Year': '1966'},
            {'id': 4, 'Title': 'Matrix', 'Director': 'N/A', 'Year': '1993-'},
            {'id': 5, 'Title': 'Cube', 'Director': 'Vincenzo Natali', 'Year': '1997'},
            {'id': 6, 'Title': 'Star Wars: Episode IV - A New Hope', 'Director': 'George Lucas', 'Year': '1977'},
            {'id': 7, 'Title': 'Star Wars: Episode V - The Empire Strikes Back', 'Director': 'Irvin Kershner', 'Year': '1980'},
            {'id': 8, 'Title': 'Fight Club', 'Director': 'David Fincher', 'Year': '1999'},
            {'id': 9, 'Title': '2001: A Space Odyssey', 'Director': 'Stanley Kubrick', 'Year': '1968'},
            {'id': 10, 'Title': 'Jumanji', 'Director': 'Joe Johnston', 'Year': '1995'},
        ]
    }


@usefixtures(*fixture_names)
def test_movies_get_page(rf):
    request = rf.get('/movies', data={'page': 2})
    response = api_views.MoviesView.as_view()(request)
    response_content = response.data
    assert response.status_code == 200
    assert len(response_content['results']) == 2
    assert response_content == {
        'results': [
            {'id': 11, 'Title': 'The Chronicles of Narnia: The Lion, the Witch and the Wardrobe', 'Director': '"Andrew Adamson"', 'Year': '2005'},
            {'id': 12, 'Title': 'Bridge to Terabithia', 'Director': 'Gabor Csupo', 'Year': '2007'},
        ]
    }


@usefixtures(*fixture_names)
def test_movies_get_order_title(rf):
    request = rf.get('/movies', data={'order': 'Title'})
    response = api_views.MoviesView.as_view()(request)
    response_content = response.data
    assert response.status_code == 200
    assert len(response_content['results']) == 10
    assert response_content['results'][0] == {
        'id': 9,
        'Title': '2001: A Space Odyssey',
        'Director': 'Stanley Kubrick',
        'Year': '1968'
    }


@usefixtures(*fixture_names)
def test_movies_get_search(rf):
    request = rf.get('/movies', data={'search': 'lu'})
    response = api_views.MoviesView.as_view()(request)
    response_content = response.data
    assert response.status_code == 200
    assert len(response_content['results']) == 2
    assert response_content == {
        'results': [
            {'id': 6, 'Title': 'Star Wars: Episode IV - A New Hope', 'Director': 'George Lucas', 'Year': '1977'},
            {'id': 8, 'Title': 'Fight Club', 'Director': 'David Fincher', 'Year': '1999'}
        ]
    }


@usefixtures(*fixture_names)
def test_post_comments_valid_id(rf):
    request = rf.post('/comments', data={'movie': 1, 'comment': 'Great movie!'})
    response = api_views.CommentsView.as_view()(request)
    response_content = response.data
    assert response.status_code == 200
    assert response_content == {
        'movie_id': 1,
        'comment': 'Great movie!',
        'added_on': datetime(year=2019, month=10, day=14, hour=7, minute=30, tzinfo=pytz.UTC).isoformat(),
        'id': 18
    }


@usefixtures(*fixture_names)
def test_post_comments_invalid_id(rf):
    request = rf.post('/comments', data={'movie': 9999999, 'comment': 'Great movie!'})
    response = api_views.CommentsView.as_view()(request)
    response_content = response.data
    assert response.status_code == 404
    assert response_content == {'error': 'Movie with id 9999999 does not exist.'}


@usefixtures(*fixture_names)
def test_get_comments(rf):
    request = rf.get('/comments')
    response = api_views.CommentsView.as_view()(request)
    response_content = response.data
    assert response.status_code == 200
    assert len(response_content['results']) == 10
    assert response_content == {
        'results': [
            {'id': 1, 'movie_id': 1, 'comment': '10/10', 'added_on': dt(2019, 10, 10).isoformat()},
            {'id': 2, 'movie_id': 1, 'comment': 'Ok', 'added_on': dt(2019, 10, 11).isoformat()},
            {'id': 3, 'movie_id': 1, 'comment': 'Worth it.', 'added_on': dt(2019, 10, 12).isoformat()},
            {'id': 4, 'movie_id': 2, 'comment': 'Bad.', 'added_on': dt(2019, 10, 10).isoformat()},
            {'id': 5, 'movie_id': 2, 'comment': 'OK.', 'added_on': dt(2019, 10, 12).isoformat()},
            {'id': 6, 'movie_id': 3, 'comment': 'Enjoyed it.', 'added_on': dt(2019, 10, 11).isoformat()},
            {'id': 7, 'movie_id': 3, 'comment': 'Could be better.', 'added_on': dt(2019, 10, 11).isoformat()},
            {'id': 8, 'movie_id': 3, 'comment': '3/10', 'added_on': dt(2019, 10, 11).isoformat()},
            {'id': 9, 'movie_id': 3, 'comment': 'Worth watching.', 'added_on': dt(2019, 10, 12).isoformat()},
            {'id': 10, 'movie_id': 3, 'comment': 'Really good.', 'added_on': dt(2019, 10, 12).isoformat()},
        ]
    }


@usefixtures(*fixture_names)
def test_get_comments_filter_existing_id(rf):
    request = rf.get('/comments', data={'movie': 2})
    response = api_views.CommentsView.as_view()(request)
    response_content = response.data
    assert response.status_code == 200
    assert len(response_content['results']) == 2
    assert response_content == {
        'results': [
            {'id': 4, 'movie_id': 2, 'comment': 'Bad.', 'added_on': dt(2019, 10, 10).isoformat()},
            {'id': 5, 'movie_id': 2, 'comment': 'OK.', 'added_on': dt(2019, 10, 12).isoformat()},
        ]
    }


@usefixtures(*fixture_names)
def test_get_comments_filter_non_existing_id(rf):
    request = rf.get('/comments', data={'movie': 99999})
    response = api_views.CommentsView.as_view()(request)
    response_content = response.data
    assert response.status_code == 200
    assert len(response_content['results']) == 0
    assert response_content == {'results': []}


@usefixtures(*fixture_names)
def test_top_valid_range(rf):
    request = rf.get(
        '/top',
        data={
            'from': dt(2019, 10, 9).isoformat(),
            'to': dt(2019, 10, 11).isoformat(),
        }
    )
    response = api_views.TopView.as_view()(request)
    response_content = response.data
    assert response.status_code == 200
    assert len(response_content['results']) == 5
    assert response_content == {
        'results': [
            {'movie_id': 4, 'rank': 1, 'total_comments': 5},
            {'movie_id': 3, 'rank': 2, 'total_comments': 3},
            {'movie_id': 1, 'rank': 3, 'total_comments': 2},
            {'movie_id': 5, 'rank': 3, 'total_comments': 2},
            {'movie_id': 2, 'rank': 5, 'total_comments': 1}
        ]
    }


@usefixtures(*fixture_names)
def test_top_missing_to(rf):
    request = rf.get('/top', data={'from': dt(2019, 10, 14).isoformat()})
    response = api_views.TopView.as_view()(request)
    response_content = response.data
    assert response.status_code == 400
    assert response_content == {
        'errors': {
            'to': "This query parameter is required.",
        }
    }


@usefixtures(*fixture_names)
def test_top_missing_from(rf):
    request = rf.get('/top', data={'to': dt(2019, 10, 14).isoformat()})
    response = api_views.TopView.as_view()(request)
    response_content = response.data
    assert response.status_code == 400
    assert response_content == {
        'errors': {
            'from': "This query parameter is required.",
        }
    }


@usefixtures(*fixture_names)
def test_top_invalids(rf):
    request = rf.get('/top', data={'from': '2019 Fb 18', 'to': '2020 Jn 1'})
    response = api_views.TopView.as_view()(request)
    response_content = response.data
    assert response.status_code == 400
    assert response_content == {
        'errors': {
            'from': "This field needs to be a valid ISO 8601 date in UTC.",
            'to': "This field needs to be a valid ISO 8601 date in UTC.",
        }
    }

