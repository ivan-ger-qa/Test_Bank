from typing import Any

import pytest

from src.main.api.classes.api_manager import ApiManager


# Фасад над шагами API
@pytest.fixture
def api_manager(created_obj: list[Any]) -> ApiManager:
    return ApiManager(created_obj)
