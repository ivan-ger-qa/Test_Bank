import logging
from typing import Any

import pytest

from src.main.api.models.create_user_response import CreateUserResponse
from src.main.api.steps.admin_steps import AdminSteps


@pytest.fixture
def created_obj():
    objects: list[Any] = []
    yield objects
    clean_user(objects)


def clean_user(objects: list[Any]):
    api_manager = AdminSteps(objects)
    for u in objects:
        if isinstance(u, CreateUserResponse):
            api_manager.delete_user(u.id)
        else:
            logging.warning(f'Error in delete_user: {type(u)}')

