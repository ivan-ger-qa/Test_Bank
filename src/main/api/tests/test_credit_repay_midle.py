import random

from src.main.api.models.account_credit_request import AccountCreditRequest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.request.account_credit_requester import AccountCreditRequester
from src.main.api.request.create_account_requester import CreateAccountRequester
from src.main.api.request.create_user_requester import CreateUserRequester
from src.main.api.request.credit_repay_requester import CreditRepayRequest, CreditRepayRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


def generate_username():
    return f'ivangg{random.randint(0, 9000000)}'


class TestCreditRepayMidle:

    def test_credit_repay_valid(self):
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

        account_credit_request = AccountCreditRequest(accountId=create_account_response.id, amount=14999.0,
                                                      termMonths=12)
        response = AccountCreditRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.request_create()
        ).post(account_credit_request)


        credit_repay_request = CreditRepayRequest(creditId=response.creditId, accountId=response.id, amount=14999.0)

        response = CreditRepayRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.request_ok()
        ).post(credit_repay_request)

        assert create_account_response.balance == response.amountDeposited - account_credit_request.amount

    def test_credit_repay_invalid(self):
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

        account_credit_request = AccountCreditRequest(accountId=create_account_response.id, amount=14999.0,
                                                      termMonths=12)
        response = AccountCreditRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.request_create()
        ).post(account_credit_request)

        credit_repay_request = CreditRepayRequest(creditId=response.creditId, accountId=response.id, amount=14998.0)

        response = CreditRepayRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec=ResponseSpecs.request_no_limit()
        ).post(credit_repay_request)

        assert "The amount is not enough" in response.text
