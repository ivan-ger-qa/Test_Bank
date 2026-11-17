import logging
from collections.abc import Iterator
from typing import Any

import pytest

from src.main.api.models.create_user_response import CreateUserResponse
from src.main.api.steps.admin_steps import AdminSteps

logger = logging.getLogger(__name__)


# Список созданных объектов
@pytest.fixture
def created_obj() -> Iterator[list[Any]]:
    objects: list[Any] = []
    yield objects
    clean_user(objects)


def clean_user(objects: list[Any]) -> None:
    api_manager = AdminSteps(objects)
    for u in objects:
        if isinstance(u, CreateUserResponse):
            api_manager.delete_user(u.id)
        else:
            logger.warning(f'Error in delete_user: {type(u)}')
