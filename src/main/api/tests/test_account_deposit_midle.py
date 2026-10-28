import pytest
import requests
import random

from src.main.api.models import login_user_response, create_user_response, create_account_response
from src.main.api.models.create_user_response import CreateUserResponse
from src.main.api.models.login_user_request import LoginUserRequest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.login_user_response import LoginUserResponse
from src.main.api.request.login_user_requester import LoginUserRequester
from src.main.api.specs import request_specs
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.api.request.create_user_requester import CreateUserRequester
from src.main.api.request.create_account_requester import CreateAccountRequester


def generate_name():
    return f'ivangg{random.randint(1, 909999)}'


class TestAccountDepositMidl:
    # присваиваем сгенерированное имя при старте метода
    def test_account_deposit_valid(self):
        username = generate_name()
        """Создаем юзера, через логин админа сразу через реквест спеку """
        create_user_request = CreateUserRequest(username=username, password='Pas!sw0rd',role='ROLE_USER')

        response = CreateUserRequester(
            request_spec= RequestSpecs.auth_headers(username='admin', password='123456'),
            response_spec=ResponseSpecs.request_ok()
        ).post(create_user_request)

        """создаем счет за юзера который создался выше"""

        create_account_response = CreateAccountRequester(
            request_spec= RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.request_create()
        ).post()

        assert create_account_response.balance == 0.0






