import dateutil.parser

from django.conf import settings
from django.core.paginator import InvalidPage, Paginator


def paginate_iterable(iterable, page_number):
    p = Paginator(iterable, settings.PAGE_SIZE)
    try:
        page = p.page(page_number)
    except InvalidPage:
        return {}

    return page.object_list


def parse_date(date_string):
    try:
        date = dateutil.parser.parse(date_string)
    except ValueError as e:
        return None, str(e)
    return date, None
