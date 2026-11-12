import pytest
from sqlalchemy.orm import Session

from src.main.api.generator.model_generator import RandomModelGenerator
from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.money_transfer_request import MoneyTransferRequest
from src.main.db.crud.account_crud import AccountCrudDb
from src.main.db.crud.transaction_crud import TransactionCrudDb

MAX_DEPOSIT = 9000.0  # максимальная сумма пополнения по требованиям проекта 9000


@pytest.mark.apis
class TestMoneyTransferSenior:
    def test_money_transfer(self, api_manager, create_user_request, db_session: Session):
        # --- Подготовка: пользователь, два счёта, деньги на счёте отправителя ---
        user = create_user_request()

        account_one = api_manager.user_steps.create_account(user)
        assert account_one.balance == 0

        account_two = api_manager.user_steps.create_account(user)
        assert account_two.balance == 0

        deposit_request = RandomModelGenerator.generate(AccountDepositRequest)
        deposit_request.accountId = account_one.id
        deposit = api_manager.user_steps.deposit_account(user, deposit_request)
        assert deposit.balance == account_one.balance + deposit_request.amount

        transfer_request = MoneyTransferRequest(fromAccountId=account_one.id,
                                                toAccountId=account_two.id,
                                                amount=deposit.balance / 2)

        expected_sender_balance = deposit.balance - transfer_request.amount
        expected_receiver_balance = account_two.balance + transfer_request.amount

        # --- Действие: перевод ---
        transfer = api_manager.user_steps.money_transfer_valid(user, transfer_request)

        # --- Проверка: ответ API ---
        assert transfer.fromAccountIdBalance == expected_sender_balance

        account_two_after = api_manager.user_steps.get_account(user, account_two.id)
        assert account_two_after.balance == expected_receiver_balance

        # --- Проверка: база данных ---
        sender_from_db = AccountCrudDb.get_account_by_id(db_session, account_one.id)
        assert sender_from_db is not None, f'Счет {account_one.id} не найден в БД'

        receiver_from_db = AccountCrudDb.get_account_by_id(db_session, account_two.id)
        assert receiver_from_db is not None, f'Счет {account_two.id} не найден в БД'

        assert sender_from_db.balance == expected_sender_balance, (
            f'Баланс отправителя в БД {sender_from_db.balance}, ожидали {expected_sender_balance}'
        )
        assert receiver_from_db.balance == expected_receiver_balance, (
            f'Баланс получателя в БД {receiver_from_db.balance}, ожидали {expected_receiver_balance}'
        )

        transfer_from_db = TransactionCrudDb.get_transfer(db_session,
                                                          from_account_id=account_one.id,
                                                          to_account_id=account_two.id)
        assert transfer_from_db is not None, (
            f'Перевод со счёта {account_one.id} на счёт {account_two.id} не найден в БД'
        )
        assert transfer_from_db.amount == transfer_request.amount, (
            f'Сумма перевода в БД {transfer_from_db.amount}, ожидали {transfer_request.amount}'
        )

    @pytest.mark.parametrize('amount', [500.0, 501.0, 5000.0, 9999.0, 10000.0])
    def test_money_transfer_valid(self, api_manager, create_user_request, amount):
        # --- Подготовка: пользователь, два счёта, деньги на счёте отправителя ---
        user = create_user_request()

        account_one = api_manager.user_steps.create_account(user)
        assert account_one.balance == 0

        account_two = api_manager.user_steps.create_account(user)
        assert account_two.balance == 0

        deposit_request_first = AccountDepositRequest(accountId=account_one.id, amount=MAX_DEPOSIT)
        api_manager.user_steps.deposit_account(user, deposit_request_first)

        deposit_request_second = AccountDepositRequest(accountId=account_one.id, amount=MAX_DEPOSIT)
        deposit = api_manager.user_steps.deposit_account(user, deposit_request_second)

        transfer_request = MoneyTransferRequest(fromAccountId=account_one.id,
                                                toAccountId=account_two.id,
                                                amount=amount)

        expected_sender_balance = deposit.balance - transfer_request.amount
        expected_receiver_balance = account_two.balance + transfer_request.amount

        # --- Действие: перевод ---
        transfer = api_manager.user_steps.money_transfer_valid(user, transfer_request)

        # --- Проверка: ответ API ---
        assert transfer.fromAccountIdBalance == expected_sender_balance

        account_two_after = api_manager.user_steps.get_account(user, account_two.id)
        assert account_two_after.balance == expected_receiver_balance

    def test_money_transfer_invalid_zero(self, api_manager, create_user_request):
        # --- Подготовка: пользователь, два счёта, деньги на счёте отправителя ---
        user = create_user_request()

        account_one = api_manager.user_steps.create_account(user)

        account_two = api_manager.user_steps.create_account(user)

        deposit_request = RandomModelGenerator.generate(AccountDepositRequest)
        deposit_request.accountId = account_one.id
        deposit = api_manager.user_steps.deposit_account(user, deposit_request)

        transfer_request = MoneyTransferRequest(fromAccountId=account_one.id,
                                                toAccountId=account_two.id,
                                                amount=0)

        # --- Действие: перевод нуля ---
        transfer = api_manager.user_steps.money_transfer_invalid_zero(user, transfer_request)

        # --- Проверка: ответ API ---
        assert 'Amount must be greater than 0' in transfer.text

        account_one_after = api_manager.user_steps.get_account(user, account_one.id)
        assert account_one_after.balance == deposit.balance

        account_two_after = api_manager.user_steps.get_account(user, account_two.id)
        assert account_two_after.balance == account_two.balance

    @pytest.mark.parametrize('amount', [250.0, 499.0, 10001.0, 15000.0])
    def test_money_transfer_invalid(self, api_manager, create_user_request, amount):
        # --- Подготовка: пользователь, два счёта, деньги на счёте отправителя ---
        user = create_user_request()

        account_one = api_manager.user_steps.create_account(user)
        assert account_one.balance == 0

        account_two = api_manager.user_steps.create_account(user)
        assert account_two.balance == 0

        deposit_request_first = AccountDepositRequest(accountId=account_one.id, amount=MAX_DEPOSIT)
        api_manager.user_steps.deposit_account(user, deposit_request_first)

        deposit_request_second = AccountDepositRequest(accountId=account_one.id, amount=MAX_DEPOSIT)
        deposit_second = api_manager.user_steps.deposit_account(user, deposit_request_second)

        transfer_request = MoneyTransferRequest(fromAccountId=account_one.id,
                                                toAccountId=account_two.id,
                                                amount=amount)

        # --- Действие: перевод суммой вне лимита ---
        transfer = api_manager.user_steps.money_transfer_invalid_zero(user, transfer_request)

        # --- Проверка: ответ API ---
        assert 'Amount must be between 500 and 10000' in transfer.text

        first_after = api_manager.user_steps.get_account(user, account_one.id)
        assert first_after.balance == deposit_second.balance

        second_after = api_manager.user_steps.get_account(user, account_two.id)
        assert second_after.balance == account_two.balance
