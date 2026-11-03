import pytest

from src.main.api.classes.api_manager import ApiManager


@pytest.fixture
def api_manager(create_obj):
    return ApiManager(create_obj)