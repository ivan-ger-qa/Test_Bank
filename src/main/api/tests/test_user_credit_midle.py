import random

import pytest

from src.main.api.models.account_credit_request import AccountCreditRequest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.request.account_credit_requester import AccountCreditRequester
from src.main.api.request.create_account_requester import CreateAccountRequester
from src.main.api.request.create_user_requester import CreateUserRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


def generate_username():
    return f'ivangg{random.randint(1, 999999)}'


@pytest.mark.api
class TestUserCreditMidle:
    def test_user_credit_midle_valid(self):
        username = generate_username()

        create_user_request = CreateUserRequest(username=username, password='Pas!sw0rd', role='ROLE_CREDIT_SECRET')

        response = CreateUserRequester(
            request_spec=RequestSpecs.auth_headers(username='admin', password='123456'),
            response_spec = ResponseSpecs.request_ok()
        ).post(create_user_request)

        create_account_response = CreateAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.request_create()
        ).post()


        '''Ждём 201, ответ распаковывается в UserCreditResponse. В Swagger поле номера счёта
            в ответе называется accountId, но API на самом деле возвращает id —
            расхождение документации и реального ответа. Модель сделана по факту (поле id).'''

        account_credit_request = AccountCreditRequest(accountId=create_account_response.id, amount=14999.0,
                                                      termMonths=12)

        response = AccountCreditRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.request_create()
        ).post(account_credit_request)

        assert response.balance == create_account_response.balance + account_credit_request.amount



    def test_user_credit_middle_invalid(self):
        username = generate_username()

        create_user_request = CreateUserRequest(username=username, password='Pas!sw0rd', role='ROLE_CREDIT_SECRET')

        response = CreateUserRequester(
            request_spec=RequestSpecs.auth_headers(username='admin', password='123456'),
            response_spec=ResponseSpecs.request_ok()
        ).post(create_user_request)

        create_account_response = CreateAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.request_create()
        ).post()

        account_credit_request = AccountCreditRequest(accountId=create_account_response.id, amount=15001.0,
                                                      termMonths=12)
        response = AccountCreditRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.request_bad() # расхождение со свагером, должна быть 422 ошибка
        ).post(account_credit_request)

        assert "Amount must be between 5000 and 15000" in response.text



