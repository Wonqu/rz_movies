from django.contrib.postgres.fields import JSONField
from django.core.exceptions import FieldError
from django.db import models
from django.db.models import Q, Count, Window, F
from django.db.models.functions import Rank


class MovieQuerySet(models.QuerySet):
    def search(self, search):
        search_fields = ['Title', 'Director', 'Writer', 'Actors', 'Production']
        query = Q()
        for field in search_fields:
            query |= Q(**{f'external_data__{field}__icontains': search})
        return self.filter(query)

    def filter_by_year(self, year):
        return self.filter(external_data__Year__iexact=year)

    def order_by_external_field(self, field):
        if field.startswith('-'):
            prefix, *field = field
            field = ''.join(field)
        else:
            prefix, field = '', field

        # don't fail in case of invalid field name, such as 'Ye ar'
        try:
            return self.order_by(f'{prefix}external_data__{field}')
        except FieldError:
            return self

    def ranked(self, from_date, to_date):
        queryset = self
        queryset = queryset.filter(comment__added_on__gte=from_date, comment__added_on__lte=to_date)

        rank_by_total_comments = Window(
            expression=Rank(),
            order_by=F('total_comments').desc()
        )

        return queryset.annotate(
            total_comments=Count('comment')
        ).annotate(
            rank=rank_by_total_comments
        ).order_by('rank', 'id')


class MovieManager(models.Manager):
    def get_queryset(self):
        return MovieQuerySet(self.model, using=self._db).order_by('pk')

    def create_with_external_data(self, external_data):
        return self.create(external_data=external_data)


class Movie(models.Model):
    objects = MovieManager()

    external_data = JSONField()

    def serialize(self):
        return {
            **self.external_data,
            'id': self.pk
        }

    def serialize_ranked(self):
        return {
            'movie_id': self.pk,
            'rank': self.rank,
            'total_comments': self.total_comments,
        }


class CommentQuerySet(models.QuerySet):
    def filter_by_movie_id(self, id_):
        return self.filter(movie_id=id_)


class CommentManager(models.Manager):
    def get_queryset(self):
        return CommentQuerySet(self.model, using=self._db).order_by('pk')


class Comment(models.Model):
    objects = CommentManager()
    movie = models.ForeignKey(Movie, on_delete=models.DO_NOTHING)
    comment = models.TextField()
    added_on = models.DateTimeField()

    def serialize(self):
        return {
            'movie_id': self.movie_id,
            'comment': self.comment,
            'added_on': self.added_on.isoformat(),
            'id': self.pk,
        }
