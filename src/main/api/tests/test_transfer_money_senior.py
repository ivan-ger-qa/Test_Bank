import pytest

from src.main.api.generator.model_generator import RandomModelGenerator
from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.money_transfer_request import MoneyTransferRequest

MAX_DEPOSIT = 9000.0  # максимальная сумма пополнения по требованиям проекта 9000


@pytest.mark.apis
class TestMoneyTransferSenior:
    def test_money_transfer(self, api_manager, create_user_request):
        user = create_user_request()

        account_one = api_manager.user_steps.create_account(user)
        assert account_one.balance == 0

        account_two = api_manager.user_steps.create_account(user)
        assert account_two.balance == 0

        deposit_request = RandomModelGenerator.generate(AccountDepositRequest)
        deposit_request.accountId = account_one.id
        deposit = api_manager.user_steps.deposit_account(user, deposit_request)
        assert deposit.balance == account_one.balance + deposit_request.amount

        transfer_request = MoneyTransferRequest(fromAccountId=account_one.id, toAccountId=account_two.id,
                                                amount=deposit.balance / 2)
        transfer = api_manager.user_steps.money_transfer_valid(user, transfer_request)
        assert transfer.fromAccountIdBalance == deposit.balance - transfer_request.amount

        account_two_after = api_manager.user_steps.get_account(user, account_two.id)
        assert account_two_after.balance == account_two.balance + transfer_request.amount

    @pytest.mark.parametrize("amount", [500.0, 501.0, 5000.0, 9999.0, 10000.0])
    def test_money_transfer_valid(self, api_manager, create_user_request, amount):
        user = create_user_request()

        account_one = api_manager.user_steps.create_account(user)
        assert account_one.balance == 0

        account_two = api_manager.user_steps.create_account(user)
        assert account_two.balance == 0

        deposit_request_first = AccountDepositRequest(accountId=account_one.id, amount=MAX_DEPOSIT)
        api_manager.user_steps.deposit_account(user, deposit_request_first)

        deposit_request_second = AccountDepositRequest(accountId=account_one.id, amount=MAX_DEPOSIT)
        deposit = api_manager.user_steps.deposit_account(user, deposit_request_second)

        transfer_request = MoneyTransferRequest(fromAccountId=account_one.id, toAccountId=account_two.id, amount=amount)
        transfer = api_manager.user_steps.money_transfer_valid(user, transfer_request)
        assert transfer.fromAccountIdBalance == deposit.balance - transfer_request.amount

        account_two_after = api_manager.user_steps.get_account(user, account_two.id)
        assert account_two_after.balance == account_two.balance + transfer_request.amount

    def test_money_transfer_invalid_zero(self, api_manager, create_user_request):
        user = create_user_request()

        account_one = api_manager.user_steps.create_account(user)

        account_two = api_manager.user_steps.create_account(user)

        deposit_request = RandomModelGenerator.generate(AccountDepositRequest)
        deposit_request.accountId = account_one.id
        deposit = api_manager.user_steps.deposit_account(user, deposit_request)

        transfer_request = MoneyTransferRequest(fromAccountId=account_one.id, toAccountId=account_two.id, amount=0)
        transfer = api_manager.user_steps.money_transfer_invalid_zero(user, transfer_request)

        assert 'Amount must be greater than 0' in transfer.text

        account_two_after = api_manager.user_steps.get_account(user, account_two.id)
        account_one_after = api_manager.user_steps.get_account(user, account_one.id)
        assert account_two_after.balance == account_two.balance
        assert account_one_after.balance == deposit.balance

    @pytest.mark.parametrize("amount", [250.0, 499.0, 10001.0, 15000.0])
    def test_money_transfer_invalid(self, api_manager, create_user_request, amount):
        user = create_user_request()

        account_one = api_manager.user_steps.create_account(user)
        assert account_one.balance == 0

        account_two = api_manager.user_steps.create_account(user)
        assert account_two.balance == 0

        deposit_request_first = AccountDepositRequest(accountId=account_one.id, amount=MAX_DEPOSIT)
        api_manager.user_steps.deposit_account(user, deposit_request_first)

        deposit_request_second = AccountDepositRequest(accountId=account_one.id, amount=MAX_DEPOSIT)
        deposit_second = api_manager.user_steps.deposit_account(user, deposit_request_second)

        transfer_request = MoneyTransferRequest(fromAccountId=account_one.id, toAccountId=account_two.id, amount=amount)
        transfer = api_manager.user_steps.money_transfer_invalid_zero(user, transfer_request)
        assert 'Amount must be between 500 and 10000' in transfer.text

        first_after = api_manager.user_steps.get_account(user, account_one.id)
        second_after = api_manager.user_steps.get_account(user, account_two.id)

        assert first_after.balance == deposit_second.balance
        assert second_after.balance == account_two.balance
