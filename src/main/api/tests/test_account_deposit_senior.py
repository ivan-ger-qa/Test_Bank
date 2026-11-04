import pytest

from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.create_user_request import CreateUserRequest


@pytest.mark.apis
class TestAccountDepositSenior:
    def test_account_deposit_valid(self, api_manager):
        user = CreateUserRequest(username="igg12121232", password="Pas!sw0rd", role="ROLE_USER")
        api_manager.admin_steps.create_user(user)

        account = api_manager.user_steps.create_account(user)

        deposit_request = AccountDepositRequest(accountId=account.id, amount=5000.0)
        deposit = api_manager.user_steps.deposit_account(user, deposit_request)

        assert deposit.balance == 5000.0

    def test_account_deposit_invalid_unauth(self, api_manager):
        deposit_request = AccountDepositRequest(accountId=1, amount=5000.0) # id не важен
        deposit = api_manager.user_steps.deposit_account_invalid_unauth(deposit_request)

        assert deposit.status_code == 401
        assert 'JWT Token not found' in deposit.text

    def test_account_deposit_invalid_over_money(self, api_manager):
        user = CreateUserRequest(username="igg1212asd", password="Pas!sw0rd", role="ROLE_USER")
        api_manager.admin_steps.create_user(user)

        account = api_manager.user_steps.create_account(user)

        deposit_request = AccountDepositRequest(accountId=account.id, amount=9001.0)
        deposit = api_manager.user_steps.deposit_account_invalid_over_mone(user, deposit_request)

        assert deposit.status_code == 400
        assert 'Amount must be between 1000 and 9000' in deposit.text
