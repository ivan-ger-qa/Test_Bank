import random

from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.money_transfer_request import MoneyTransferRequest
from src.main.api.request.account_deposit_requester import AccountDepositRequester
from src.main.api.request.create_account_requester import CreateAccountRequester
from src.main.api.request.create_user_requester import CreateUserRequester
from src.main.api.request.money_transfer_requester import MoneyTransferRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs



def generate_name():
    return f'ivangg{random.randint(1, 909999)}'


class TestTransferMoneyMidl:

    def test_transfer_money_midl_valid(self):
        username = generate_name()

        create_user_request = CreateUserRequest(username=username, password='Pas!sw0rd',role='ROLE_USER')

        response = CreateUserRequester(
            request_spec=RequestSpecs.auth_headers(username='admin', password='123456'),
            response_spec= ResponseSpecs.request_ok()
        ).post(create_user_request)


        create_account_one_response = CreateAccountRequester(
            request_spec= RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec= ResponseSpecs.request_create()
        ).post()

        create_account_two_response = CreateAccountRequester(
            request_spec= RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec= ResponseSpecs.request_create()
        ).post()



        account_deposit_request = AccountDepositRequest(accountId=create_account_one_response.id, amount=5000.0)

        response = AccountDepositRequester(
            request_spec= RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec= ResponseSpecs.request_ok()
        ).post(account_deposit_request)


        money_transfer_request = MoneyTransferRequest(
            fromAccountId=create_account_one_response.id,
            toAccountId=create_account_two_response.id,
            amount=2000.0)

        response = MoneyTransferRequester(
            request_spec= RequestSpecs.auth_headers(username=username, password='Pas!sw0rd'),
            response_spec= ResponseSpecs.request_ok()
        ).post(money_transfer_request)









