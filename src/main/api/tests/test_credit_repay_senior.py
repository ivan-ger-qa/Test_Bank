import pytest

from src.main.api.models.account_credit_request import AccountCreditRequest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.credit_repay_request import CreditRepayRequest


@pytest.mark.apis
class TestCreditRepay:
    def test_credit_repay_valid(self, api_manager):
        user = CreateUserRequest(username='Ivangg2221', password='Pas!sw0rd', role='ROLE_CREDIT_SECRET')
        api_manager.admin_steps.create_user(user)

        account = api_manager.user_steps.create_account(user)
        assert account.balance == 0

        credit_request = AccountCreditRequest(accountId=account.id, amount=10000.0, termMonths=12)
        credit = api_manager.user_steps.credit_user_valid(user, credit_request)
        assert credit.balance == 10000.0


        repay_request = CreditRepayRequest(creditId=credit.creditId, accountId=account.id, amount=10000.0)
        repay = api_manager.user_steps.repay_credit_valid(user, repay_request)

        assert repay.creditId == credit.creditId
        assert repay.amountDeposited == repay_request.amount

    def test_credit_repay_invalid(self, api_manager):
        user = CreateUserRequest(username='Ivangg221', password='Pas!sw0rd', role='ROLE_CREDIT_SECRET')
        api_manager.admin_steps.create_user(user)

        account = api_manager.user_steps.create_account(user)
        assert account.balance == 0

        credit_request = AccountCreditRequest(accountId=account.id, amount=10000.0, termMonths=12)
        credit = api_manager.user_steps.credit_user_valid(user, credit_request)
        assert credit.balance == 10000.0

        repay_request = CreditRepayRequest(creditId=credit.creditId, accountId=account.id, amount=9999.0)
        repay = api_manager.user_steps.repay_credit_invalid(user, repay_request)

        assert 'The amount is not enough' in repay.text



