from rest_framework.response import Response
from rest_framework.views import APIView

from movies.apps.movies import services, models
from movies.utils import paginate_iterable, parse_date


class MoviesView(APIView):
    def get(self, request, *args, **kwargs):
        queryset = models.Movie.objects.all()

        order = self.request.GET.get('order')
        if order:
            queryset = queryset.order_by_external_field(order)

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.search(search)

        year = self.request.GET.get('year')
        if year:
            queryset = queryset.filter_by_year(year)

        page = self.request.GET.get('page', 1)
        queryset = paginate_iterable(queryset, page)

        return Response(
            data={
                'results': [m.serialize() for m in queryset]
            },
            status=200
        )

    def post(self, request, *args, **kwargs):
        movie_title = request.data.get('title')
        if not movie_title:
            return Response(
                data={'title': 'This field is required.'},
                status=400
            )
        movie_data, error = services.get_or_create_movie_by_title(movie_title)
        if error:
            return Response(
                data={'error': error},
                status=404
            )
        else:
            return Response(
                data=movie_data,
                status=200
            )


class CommentsView(APIView):
    def get(self, request, *args, **kwargs):
        queryset = models.Comment.objects.all()

        movie_id = request.GET.get('movie')
        if movie_id:
            queryset = queryset.filter_by_movie_id(movie_id)

        page = self.request.GET.get('page', 1)
        queryset = paginate_iterable(queryset, page)

        return Response(
            data={
                'results': [c.serialize() for c in queryset]
            },
            status=200
        )

    def post(self, request, *args, **kwargs):
        movie_id = request.data.get('movie')
        comment_text = request.data.get('comment')

        comment, error = services.add_comment_to_movie(movie_id, comment_text)

        if isinstance(error, models.Movie.DoesNotExist):
            return Response(
                data={'error': str(error)},
                status=404
            )
        else:
            return Response(
                data=comment,
                status=200
            )


class TopView(APIView):
    def get(self, request, *args, **kwargs):
        queryset = models.Movie.objects.all()

        from_date = request.GET.get('from')
        to_date = request.GET.get('to')
        errors = {}
        if from_date:
            from_date, from_error = parse_date(from_date)
            if from_error:
                errors['from'] = "This field needs to be a valid ISO 8601 date in UTC."
        else:
            errors['from'] = "This query parameter is required."
        if to_date:
            to_date, to_error = parse_date(to_date)
            if to_error:
                errors['to'] = "This field needs to be a valid ISO 8601 date in UTC."
        else:
            errors['to'] = "This query parameter is required."

        if errors:
            return Response(
                data={'errors': errors},
                status=400
            )
        queryset = queryset.ranked(from_date, to_date)

        page = self.request.GET.get('page', 1)
        queryset = paginate_iterable(queryset, page)

        return Response(
            data={
                'results': [m.serialize_ranked() for m in queryset]
            },
            status=200
        )
