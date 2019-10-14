import pytest
import pytz

from datetime import datetime

from django.test import RequestFactory


@pytest.fixture(scope='module')
def request_factory():
    return RequestFactory()


@pytest.fixture(scope='function')
def freeze_now(monkeypatch):
    def fake_now():
        return datetime(year=2019, month=10, day=14, hour=7, minute=30, tzinfo=pytz.UTC)

    monkeypatch.setattr("django.utils.timezone.now", fake_now)
