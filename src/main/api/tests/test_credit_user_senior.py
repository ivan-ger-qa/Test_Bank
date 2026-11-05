import pytest

from src.main.api.models.account_credit_request import AccountCreditRequest
from src.main.api.models.create_user_request import CreateUserRequest



@pytest.mark.apis
class TestCreditUser:
    def test_credit_user_valid(self, api_manager):
        user = CreateUserRequest(username='IVamasd12123', password='Pas!sw0rd', role='ROLE_CREDIT_SECRET')
        api_manager.admin_steps.create_user(user)

        account = api_manager.user_steps.create_account(user)

        credit_request = AccountCreditRequest(accountId=account.id,amount=10000.0, termMonths=12)
        credit = api_manager.user_steps.credit_user_valid(user, credit_request)

        assert credit.amount == credit_request.amount


    def test_credit_user_invalid(self, api_manager):
        user = CreateUserRequest(username='IVamasd12', password='Pas!sw0rd', role='ROLE_USER')
        api_manager.admin_steps.create_user(user)

        account = api_manager.user_steps.create_account(user)

        credit_request = AccountCreditRequest(accountId=account.id,amount=10000.0, termMonths=12)
        credit = api_manager.user_steps.credit_user_invalid(user, credit_request)

        assert 'ROLE_CREDIT access required' in credit.text


