from django.urls import include, path

from movies import api_views
from movies.apps.movies.urls import urlpatterns as movies_urlpatterns, app_name as movies_app_name

urlpatterns = [
    path('health', api_views.HealthCheckView.as_view(), name='health'),
    path('', api_views.HomeView.as_view(), name='home'),
    path('', include((movies_urlpatterns, movies_app_name), namespace='movies')),
]
