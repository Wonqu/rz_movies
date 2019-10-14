from django.urls import path

from movies.apps.movies import api_views

app_name = 'movies'

urlpatterns = [
    path('comments', api_views.CommentsView.as_view(), name='comments'),
    path('movies', api_views.MoviesView.as_view(), name='movies'),
    path('top', api_views.TopView.as_view(), name='top'),
]
