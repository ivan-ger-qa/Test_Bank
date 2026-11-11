import pytest

from src.main.api.generator.model_generator import RandomModelGenerator
from src.main.api.models.create_user_request import CreateUserRequest


@pytest.fixture
def create_user_request(api_manager):
    def _make(role: str = 'ROLE_USER'):
        user = RandomModelGenerator.generate(CreateUserRequest)
        user.role = role
        api_manager.admin_steps.create_user(user)
        return user
    return _make
