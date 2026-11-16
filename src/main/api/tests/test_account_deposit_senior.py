import pytest
from sqlalchemy.orm import Session

from src.main.api.generator.model_generator import RandomModelGenerator
from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.db.crud.account_crud import AccountCrudDb
from src.main.db.crud.transaction_crud import TransactionCrudDb


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
        assert deposit.balance == expected_balance, (f'В ответе API баланс {deposit.balance}, '
                                                             f'а ожидали {expected_balance}')

        account_after = api_manager.user_steps.get_account(user, account.id)
        assert account_after.balance == expected_balance, (f'Баланс счёта {account_after.balance}, '
                                                          f'а ожидали {expected_balance}')

        # --- Проверка: выписка по счёту ---
        deposits = [t for t in account_after.transactions if t.type == 'deposit']
        assert len(deposits) == 1, f'Фактически получили список пополнений {len(deposits)}, а ожидали 1 {deposits}'
        assert deposits[0].amount == deposit_request.amount, (f'Сумма пополнения в истории API {deposits[0].amount}, '
                                                              f'ожидали {deposit_request.amount}')
        assert deposits[0].toAccountId == account.id, (f'Пополнение пришло на счёт {deposits[0].toAccountId}, '
                                                       f'а ожидали {account.id}')

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
        assert deposits_from_db[0].amount == deposit_request.amount, (
            f'Сумма пополнения в БД {deposits_from_db[0].amount}, '
            f'ожидали {deposit_request.amount}'
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
        assert deposit.balance == expected_balance, (f'В ответе API баланс {deposit.balance}, '
                                                             f'а ожидали {expected_balance}')

        account_after = api_manager.user_steps.get_account(user, account.id)
        assert account_after.balance == expected_balance, (f'Баланс счёта {account_after.balance}, '
                                                          f'а ожидали {expected_balance}')

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
        assert 'Amount must be between 1000 and 9000' in deposit.text, (f'Ожидали текст "Amount must be between 1000 and 9000", '
                                                                       f'а получили {deposit.text}')

        account_after = api_manager.user_steps.get_account(user, account.id)
        assert account_after.balance == expected_balance, (f'Баланс счёта {account_after.balance}, '
                                                          f'а ожидали {expected_balance}')

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
        assert deposit.status_code == 401, f'Ожидали статус 401, а получили {deposit.status_code}'
        assert 'JWT Token not found' in deposit.text, (f'Ожидали "JWT Token not found", '
                                                       f'а получили {deposit.text}')
