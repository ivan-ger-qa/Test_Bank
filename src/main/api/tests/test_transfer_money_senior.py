import pytest
from sqlalchemy.orm import Session

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.account_deposit_response import AccountDepositResponse
from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.money_transfer_request import MoneyTransferRequest
from src.main.api.utils import find_transaction_by_type
from src.main.db.crud.account_crud import AccountCrudDb


@pytest.mark.apis
class TestMoneyTransferSenior:
    def test_money_transfer(self, api_manager: ApiManager, user: CreateUserRequest,
                            funded_account: AccountDepositResponse, second_account: CreateAccountResponse,
                            db_session: Session) -> None:
        # --- Подготовка: пользователь, два счёта, деньги на счёте отправителя ---

        transfer_request = MoneyTransferRequest(fromAccountId=funded_account.id,
                                                toAccountId=second_account.id,
                                                amount=funded_account.balance / 2)

        expected_sender_balance = funded_account.balance - transfer_request.amount
        expected_receiver_balance = second_account.balance + transfer_request.amount

        # --- Действие: перевод ---
        transfer = api_manager.user_steps.money_transfer_valid(user, transfer_request)

        # --- Проверка: ответ API ---
        assert transfer.fromAccountIdBalance == expected_sender_balance, (f'В ответе API баланс отправителя '
                                                                          f'{transfer.fromAccountIdBalance}, '
                                                                          f'а ожидали {expected_sender_balance}')

        account_two_after = api_manager.user_steps.get_account(user, second_account.id)

        # --- Проверка: выписка по счёту ---
        account_one_after = api_manager.user_steps.get_account(user, funded_account.id)
        transfers_out = find_transaction_by_type(account_one_after.transactions, 'transfer_out')
        assert len(transfers_out) == 1, (f'Переводов out у отправителя {len(transfers_out)}, '
                                         f'а ожидали 1')

        transfers_in = find_transaction_by_type(account_two_after.transactions, 'transfer_in')
        assert len(transfers_in) == 1, (f'Переводов in у получателя {len(transfers_in)}, '
                                        f'а ожидали 1')

        # --- Проверка: база данных ---
        sender_from_db = AccountCrudDb.get_account_by_id(db_session, funded_account.id)
        assert sender_from_db is not None, f'Счет {funded_account.id} не найден в БД'

        receiver_from_db = AccountCrudDb.get_account_by_id(db_session, second_account.id)
        assert receiver_from_db is not None, f'Счет {second_account.id} не найден в БД'

        assert sender_from_db.balance == expected_sender_balance, (
            f'Баланс отправителя в БД {sender_from_db.balance}, ожидали {expected_sender_balance}'
        )
        assert receiver_from_db.balance == expected_receiver_balance, (
            f'Баланс получателя в БД {receiver_from_db.balance}, ожидали {expected_receiver_balance}'
        )


    @pytest.mark.parametrize('amount', [500.0, 501.0, 5000.0, 9999.0, 10000.0])
    def test_money_transfer_valid(self, api_manager: ApiManager, user: CreateUserRequest,
                                  max_funded_account: AccountDepositResponse, second_account: CreateAccountResponse,
                                  amount: float) -> None:
        # --- Подготовка: пользователь, два счёта, деньги на счёте отправителя ---
        transfer_request = MoneyTransferRequest(fromAccountId=max_funded_account.id,
                                                toAccountId=second_account.id,
                                                amount=amount)

        expected_sender_balance = max_funded_account.balance - transfer_request.amount
        expected_receiver_balance = second_account.balance + transfer_request.amount

        # --- Действие: перевод ---
        transfer = api_manager.user_steps.money_transfer_valid(user, transfer_request)

        # --- Проверка: ответ API ---
        assert transfer.fromAccountIdBalance == expected_sender_balance, (f'В ответе API баланс отправителя '
                                                                          f'{transfer.fromAccountIdBalance}, '
                                                                          f'а ожидали {expected_sender_balance}')

        account_two_after = api_manager.user_steps.get_account(user, second_account.id)
        assert account_two_after.balance == expected_receiver_balance, (
            f'Баланс получателя {account_two_after.balance}, '
            f'а ожидали {expected_receiver_balance}')

    def test_money_transfer_invalid_zero(self, api_manager: ApiManager, user: CreateUserRequest,
                                         funded_account: AccountDepositResponse,
                                         second_account: CreateAccountResponse) -> None:
        # --- Подготовка: пользователь, два счёта, деньги на счёте отправителя ---
        transfer_request = MoneyTransferRequest(fromAccountId=funded_account.id,
                                                toAccountId=second_account.id,
                                                amount=0)

        # --- Действие: перевод нуля ---
        transfer = api_manager.user_steps.money_transfer_invalid_zero(user, transfer_request)

        # --- Проверка: ответ API ---
        assert 'Amount must be greater than 0' in transfer.text, (f'Ожидали текст "Amount must be greater than 0", '
                                                                  f'а получили {transfer.text}')

        account_one_after = api_manager.user_steps.get_account(user, funded_account.id)
        assert account_one_after.balance == funded_account.balance, (f'Баланс отправителя {account_one_after.balance}, '
                                                                     f'а ожидали {funded_account.balance}')


    @pytest.mark.parametrize('amount', [250.0, 499.0, 10001.0, 15000.0])
    def test_money_transfer_invalid(self, api_manager: ApiManager, user: CreateUserRequest,
                                    max_funded_account: AccountDepositResponse, second_account: CreateAccountResponse,
                                    amount: float, db_session: Session) -> None:
        # --- Подготовка: пользователь, два счёта, деньги на счёте отправителя ---

        transfer_request = MoneyTransferRequest(fromAccountId=max_funded_account.id,
                                                toAccountId=second_account.id,
                                                amount=amount)

        sender_balance_before_db = AccountCrudDb.get_account_by_id(db_session, max_funded_account.id).balance
        receiver_balance_before_db = AccountCrudDb.get_account_by_id(db_session, second_account.id).balance

        # --- Действие: перевод суммой вне лимита ---
        transfer = api_manager.user_steps.money_transfer_invalid_zero(user, transfer_request)

        # --- Проверка: ответ API ---
        assert 'Amount must be between 500 and 10000' in transfer.text, (
            f'Ожидали текст "Amount must be between 500 and 10000", '
            f'а получили {transfer.text}')

        # --- Проверка: база данных ---
        db_session.expunge_all()
        sender_from_db = AccountCrudDb.get_account_by_id(db_session, max_funded_account.id)
        assert sender_from_db is not None, f'Счет отправителя {max_funded_account.id} не найден'
        assert sender_balance_before_db == sender_from_db.balance, (f'Баланс отправителя в БД до перевода '
                                                                    f'{sender_balance_before_db}, а после '
                                                                    f'{sender_from_db.balance}')

        receiver_from_db = AccountCrudDb.get_account_by_id(db_session, second_account.id)
        assert receiver_from_db is not None, f'Счет получателя {second_account.id} не найден'
        assert receiver_from_db.balance == receiver_balance_before_db, (f'Баланс получателя в БД до перевода '
                                                                        f'{receiver_balance_before_db}, а после '
                                                                        f'{receiver_from_db.balance}')

