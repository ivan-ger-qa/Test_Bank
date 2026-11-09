import pytest

from src.main.api.generator.model_generator import RandomModelGenerator
from src.main.api.models.account_deposit_request import AccountDepositRequest


@pytest.mark.apis
class TestAccountDepositSenior:
    def test_account_deposit(self, api_manager, create_user_request):
        user = create_user_request()

        account = api_manager.user_steps.create_account(user)

        deposit_request = RandomModelGenerator.generate(AccountDepositRequest)
        deposit_request.accountId = account.id
        deposit = api_manager.user_steps.deposit_account(user, deposit_request)
        assert deposit.balance == account.balance + deposit_request.amount

    @pytest.mark.parametrize('amount', [1000.0, 4500.0, 9000.0])
    def test_account_deposit_valid(self, api_manager, create_user_request, amount):
        user = create_user_request()

        account = api_manager.user_steps.create_account(user)

        deposit_request = AccountDepositRequest(accountId=account.id, amount=amount)
        deposit = api_manager.user_steps.deposit_account(user, deposit_request)
        assert deposit.balance == account.balance + deposit_request.amount

    @pytest.mark.parametrize('amount', [450.0, 999.0, 9001.0, 15000.0])
    def test_account_deposit_invalid(self, api_manager, create_user_request, amount):
        user = create_user_request()

        account = api_manager.user_steps.create_account(user)

        deposit_request = AccountDepositRequest(accountId=account.id, amount=amount)
        deposit = api_manager.user_steps.deposit_account_invalid_over_mone(user, deposit_request)
        assert 'Amount must be between 1000 and 9000' in deposit.text

    def test_account_deposit_invalid_unauth(self, api_manager):
        deposit_request = RandomModelGenerator.generate(AccountDepositRequest)
        deposit = api_manager.user_steps.deposit_account_invalid_unauth(deposit_request)
        assert deposit.status_code == 401
        assert 'JWT Token not found' in deposit.text
