import json

import pytest

from movies import api_views
from movies.utils_tests import request_factory

usefixtures = pytest.mark.usefixtures

fixture_names = ['request_factory']


def test_discovery():
    # test that tests are at least discovered
    assert True


@usefixtures(*fixture_names)
def test_top_missing_from(rf):
    request = rf.get('/health')
    response = api_views.HealthCheckView.as_view()(request)
    response_content = response.data
    assert response.status_code == 200
    assert response_content == {
        'alive': True,
        'environment_type': 'test'
    }
