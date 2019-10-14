import os

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View

from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    def get(self, request, *args, **kwargs):
        return Response(
            data={
                'alive': True,
                'environment_type': os.environ.get('APPLICATION_ENVIRONMENT')
            },
            status=200
        )


class HomeView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('movies:movies'))
