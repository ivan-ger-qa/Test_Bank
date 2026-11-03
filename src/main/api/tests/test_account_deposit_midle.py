import random
from http import HTTPStatus

import pytest

from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.request.account_deposit_requester import AccountDepositRequester
from src.main.api.request.create_account_requester import CreateAccountRequester
from src.main.api.request.create_user_requester import CreateUserRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


def generate_name():
    return f'ivangg{random.randint(1, 909999)}'


@pytest.mark.api
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


        """теперь мы делаем пополнение акаунта, который создали выше, нап тысячу рублей.
                создалит акаунт деп реквест в модель реквест, дальше в респонсе выполняем наш реквестер и через спеки вытаскиваем пост запрос из акаунт депозита рееквест"""


        account_deposit_request= AccountDepositRequest(accountId=create_account_response.id,amount=1000.0)

        response = AccountDepositRequester(
            request_spec= RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.request_ok()
        ).post(account_deposit_request)

        assert response.balance == account_deposit_request.amount
        assert create_account_response.id == response.id


    def test_account_deposit_invalid(self):
        username = generate_name()

        create_user_request = CreateUserRequest(username=username, password='Pas!sw0rd',role='ROLE_USER')

        response = CreateUserRequester(
            request_spec= RequestSpecs.auth_headers(username='admin', password='123456'),
            response_spec=ResponseSpecs.request_ok()
        ).post(create_user_request)

        create_account_response = CreateAccountRequester(
            request_spec= RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.request_create()
        ).post()

        account_deposit_request = AccountDepositRequest(accountId=create_account_response.id,amount=9001.0)

        response = AccountDepositRequester(
            request_spec= RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.request_bad()
        ).post(account_deposit_request)

        assert create_account_response.balance == 0.0
        assert response.status_code == HTTPStatus.BAD_REQUEST













