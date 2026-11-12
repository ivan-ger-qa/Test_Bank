import pytest
from sqlalchemy.orm import Session

from src.main.api.generator.model_generator import RandomModelGenerator
from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.db.crud.account_crud import AccountCrudDb


@pytest.mark.apis
class TestAccountDepositSenior:
    def test_account_deposit(self, api_manager, create_user_request, db_session: Session):
        # --- Подготовка: пользователь и счёт ---
        user = create_user_request()

        account = api_manager.user_steps.create_account(user)

        deposit_request = RandomModelGenerator.generate(AccountDepositRequest)
        deposit_request.accountId = account.id

        expected_balance = account.balance + deposit_request.amount

        # --- Действие: пополняем счёт ---
        deposit = api_manager.user_steps.deposit_account(user, deposit_request)

        # --- Проверка: ответ API ---
        assert deposit.balance == expected_balance

        account_after = api_manager.user_steps.get_account(user, account.id)
        assert account_after.balance == account.balance + deposit_request.amount

        # --- Проверка: база данных ---
        account_from_db = AccountCrudDb.get_account_by_id(db_session, account_id=account.id)
        assert account_from_db is not None, f'Счет {account.id} не найден в БД'
        assert account_from_db.balance == expected_balance, (
            f'Актуальный баланс в БД {account_from_db.balance}, ожидали {expected_balance}'
        )

    @pytest.mark.parametrize('amount', [1000.0, 4500.0, 9000.0])
    def test_account_deposit_valid(self, api_manager, create_user_request, amount, db_session: Session):
        # --- Подготовка: пользователь и счёт ---
        user = create_user_request()

        account = api_manager.user_steps.create_account(user)

        deposit_request = AccountDepositRequest(accountId=account.id, amount=amount)

        expected_balance = account.balance + deposit_request.amount

        # --- Действие: пополняем счёт ---
        deposit = api_manager.user_steps.deposit_account(user, deposit_request)

        # --- Проверка: ответ API ---
        assert deposit.balance == expected_balance

        account_after = api_manager.user_steps.get_account(user, account.id)
        assert account_after.balance == expected_balance

        # --- Проверка: база данных ---
        account_from_db = AccountCrudDb.get_account_by_id(db_session, account_id=account.id)
        assert account_from_db is not None, f'Счет {account.id} не найден в БД'
        assert account_from_db.balance == expected_balance, (
            f'Актуальный баланс в БД {account_from_db.balance}, ожидали {expected_balance}'
        )

    @pytest.mark.parametrize('amount', [450.0, 999.0, 9001.0, 15000.0])
    def test_account_deposit_invalid(self, api_manager, create_user_request, amount, db_session: Session):
        # --- Подготовка: пользователь и счёт ---
        user = create_user_request()

        account = api_manager.user_steps.create_account(user)

        deposit_request = AccountDepositRequest(accountId=account.id, amount=amount)

        expected_balance = account.balance

        # --- Действие: пополняем счёт суммой вне лимита ---
        deposit = api_manager.user_steps.deposit_account_invalid_over_money(user, deposit_request)

        # --- Проверка: ответ API ---
        assert 'Amount must be between 1000 and 9000' in deposit.text

        account_after = api_manager.user_steps.get_account(user, account.id)
        assert account_after.balance == expected_balance

        # --- Проверка: база данных ---
        account_from_db = AccountCrudDb.get_account_by_id(db_session, account_id=account.id)
        assert account_from_db is not None, f'Счет {account.id} не найден в БД'
        assert account_from_db.balance == expected_balance, (
            f'Актуальный баланс в БД {account_from_db.balance}, ожидали {expected_balance}'
        )

    def test_account_deposit_invalid_unauth(self, api_manager, db_session: Session):
        # --- Подготовка: запрос на пополнение ---
        deposit_request = RandomModelGenerator.generate(AccountDepositRequest)

        # --- Действие: пополняем без авторизации ---
        deposit = api_manager.user_steps.deposit_account_invalid_unauth(deposit_request)

        # --- Проверка: ответ API ---
        assert deposit.status_code == 401
        assert 'JWT Token not found' in deposit.text
