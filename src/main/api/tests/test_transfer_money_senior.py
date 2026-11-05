import pytest

from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.money_transfer_request import MoneyTransferRequest


@pytest.mark.apis
class TestMoneyTransferSenior:
    def test_money_transfer_valid(self, api_manager):
        user = CreateUserRequest(username="igg12121232", password="Pas!sw0rd", role="ROLE_USER")
        api_manager.admin_steps.create_user(user)

        account_one = api_manager.user_steps.create_account(user)
        assert account_one.balance == 0

        account_two = api_manager.user_steps.create_account(user)
        assert account_two.balance == 0

        deposite_request = AccountDepositRequest(accountId=account_one.id, amount=5000.0)
        deposit = api_manager.user_steps.deposit_account(user, deposite_request)
        assert deposit.balance == 5000.0

        transfer_request = MoneyTransferRequest(fromAccountId=account_one.id, toAccountId=account_two.id, amount=2000.0)
        transfer = api_manager.user_steps.money_transfer_valid(user, transfer_request)

        assert transfer.fromAccountIdBalance == deposit.balance - transfer_request.amount

    def test_money_transfer_invalid(self, api_manager):
        user = CreateUserRequest(username="igg12121232", password="Pas!sw0rd", role="ROLE_USER")
        api_manager.admin_steps.create_user(user)

        account_one = api_manager.user_steps.create_account(user)
        assert account_one.balance == 0

        account_two = api_manager.user_steps.create_account(user)
        assert account_two.balance == 0

        deposit_requset = AccountDepositRequest(accountId=account_one.id, amount=5000.0)
        deposit = api_manager.user_steps.deposit_account(user, deposit_requset)
        assert deposit.balance == 5000.0

        tranfer_request = MoneyTransferRequest(fromAccountId=account_one.id, toAccountId=account_two.id, amount=5001.0)
        transfer = api_manager.user_steps.money_transfer_invalid(user, tranfer_request)
        assert 'Insufficient funds' in transfer.text


    def test_money_transfer_invalid_zero(self, api_manager):
        user = CreateUserRequest(username="igg12121232", password="Pas!sw0rd", role="ROLE_USER")
        api_manager.admin_steps.create_user(user)

        account_one = api_manager.user_steps.create_account(user)

        account_two = api_manager.user_steps.create_account(user)

        deposit_request = AccountDepositRequest(accountId=account_one.id, amount=5000.0)
        deposit = api_manager.user_steps.deposit_account(user, deposit_request)

        transfer_request = MoneyTransferRequest(fromAccountId=account_one.id, toAccountId=account_two.id, amount=0)
        transfer = api_manager.user_steps.money_transfer_invalid_zero(user, transfer_request)

        assert 'Amount must be greater than 0' in transfer.text
