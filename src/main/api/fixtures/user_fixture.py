from collections.abc import Callable

import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generator.model_generator import RandomModelGenerator
from src.main.api.models.create_user_request import CreateUserRequest


# Фабрика пользователя с ролью
@pytest.fixture
def create_user_request(api_manager: ApiManager) -> Callable[..., CreateUserRequest]:
    def _make(role: str = 'ROLE_USER') -> CreateUserRequest:
        user = RandomModelGenerator.generate(CreateUserRequest)
        user.role = role
        api_manager.admin_steps.create_user(user)
        return user

    return _make


# Обычный пользователь ROLE_USER
@pytest.fixture
def user(create_user_request: Callable[..., CreateUserRequest]) -> CreateUserRequest:
    return create_user_request()


# Пользователь с ролью кредита
@pytest.fixture
def credit_user(
        create_user_request: Callable[..., CreateUserRequest]) -> CreateUserRequest:
    return create_user_request(role='ROLE_CREDIT_SECRET')
