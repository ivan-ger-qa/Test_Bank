import pytest
from sqlalchemy.orm import Session

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generator.model_generator import RandomModelGenerator
from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.utils import find_transaction_by_type
from src.main.db.crud.account_crud import AccountCrudDb
from src.main.db.crud.transaction_crud import TransactionCrudDb


@pytest.mark.apis
class TestAccountDepositSenior:
    def test_account_deposit(self, api_manager: ApiManager, user: CreateUserRequest, account: CreateAccountResponse,
                             db_session: Session) -> None:
        # --- Подготовка: пользователь и счёт ---

        deposit_request = RandomModelGenerator.generate(AccountDepositRequest)
        deposit_request.accountId = account.id

        expected_balance = account.balance + deposit_request.amount

        # --- Действие: пополняем счёт ---
        deposit = api_manager.user_steps.deposit_account(user, deposit_request)

        # --- Проверка: ответ API ---
        assert deposit.balance == expected_balance, (f'В ответе API баланс {deposit.balance}, '
                                                     f'а ожидали {expected_balance}')

        # --- Проверка: выписка по счёту ---
        account_after = api_manager.user_steps.get_account(user, account.id)
        deposits = find_transaction_by_type(account_after.transactions, 'deposit')
        assert len(deposits) == 1, f'Фактически получили список пополнений {len(deposits)}, а ожидали 1 {deposits}'

        # --- Проверка: база данных ---
        account_from_db = AccountCrudDb.get_account_by_id(db_session, account_id=account.id)
        assert account_from_db is not None, f'Счет {account.id} не найден в БД'
        assert account_from_db.balance == expected_balance, (
            f'Актуальный баланс в БД {account_from_db.balance}, ожидали {expected_balance}'
        )
        deposits_from_db = TransactionCrudDb.get_deposits(db_session, account_id=account.id)
        assert len(deposits_from_db) == 1, (
            f'Пополнений счёта {account.id} в БД {len(deposits_from_db)}, '
            f'ожидали 1: {deposits_from_db}'
        )

    @pytest.mark.parametrize('amount', [1000.0, 4500.0, 9000.0])
    def test_account_deposit_valid(self, api_manager: ApiManager, user: CreateUserRequest,
                                   account: CreateAccountResponse, amount: float, db_session: Session) -> None:
        # --- Подготовка: пользователь и счёт ---
        deposit_request = AccountDepositRequest(accountId=account.id, amount=amount)

        expected_balance = account.balance + deposit_request.amount

        # --- Действие: пополняем счёт ---
        deposit = api_manager.user_steps.deposit_account(user, deposit_request)

        # --- Проверка: ответ API ---
        assert deposit.balance == expected_balance, (f'В ответе API баланс {deposit.balance}, '
                                                     f'а ожидали {expected_balance}')

        # --- Проверка: база данных ---
        account_from_db = AccountCrudDb.get_account_by_id(db_session, account_id=account.id)
        assert account_from_db is not None, f'Счет {account.id} не найден в БД'
        assert account_from_db.balance == expected_balance, (
            f'Актуальный баланс в БД {account_from_db.balance}, ожидали {expected_balance}'
        )

    @pytest.mark.parametrize('amount', [450.0, 999.0, 9001.0, 15000.0])
    def test_account_deposit_invalid(self, api_manager: ApiManager, user: CreateUserRequest,
                                     account: CreateAccountResponse, amount: float, db_session: Session) -> None:
        # --- Подготовка: пользователь и счёт ---
        deposit_request = AccountDepositRequest(accountId=account.id, amount=amount)

        expected_balance = account.balance

        # --- Действие: пополняем счёт суммой вне лимита ---
        deposit = api_manager.user_steps.deposit_account_invalid_over_money(user, deposit_request)

        # --- Проверка: ответ API ---
        assert 'Amount must be between 1000 and 9000' in deposit.text, (
            f'Ожидали текст "Amount must be between 1000 and 9000", '
            f'а получили {deposit.text}')

        # --- Проверка: база данных ---
        account_from_db = AccountCrudDb.get_account_by_id(db_session, account_id=account.id)
        assert account_from_db is not None, f'Счет {account.id} не найден в БД'
        assert account_from_db.balance == expected_balance, (
            f'Актуальный баланс в БД {account_from_db.balance}, ожидали {expected_balance}'
        )

    def test_account_deposit_invalid_unauth(self, api_manager: ApiManager, db_session: Session) -> None:
        # --- Подготовка: запрос на пополнение ---
        deposit_request = RandomModelGenerator.generate(AccountDepositRequest)

        # --- Действие: пополняем без авторизации ---
        deposit = api_manager.user_steps.deposit_account_invalid_unauth(deposit_request)

        # --- Проверка: ответ API ---
        assert 'JWT Token not found' in deposit.text, (f'Ожидали "JWT Token not found", '
                                                       f'а получили {deposit.text}')
