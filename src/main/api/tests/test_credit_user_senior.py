import pytest
from sqlalchemy.orm import Session

from src.main.api.generator.model_generator import RandomModelGenerator
from src.main.api.models.account_credit_request import AccountCreditRequest
from src.main.db.crud.credit_crud import CreditCrudDb


@pytest.mark.apis
class TestCreditUser:
    def test_credit_user(self, api_manager, create_user_request, db_session: Session):
        # --- Подготовка: пользователь с ролью кредита и счёт ---
        user = create_user_request(role='ROLE_CREDIT_SECRET')

        account = api_manager.user_steps.create_account(user)

        credit_request = RandomModelGenerator.generate(AccountCreditRequest)
        credit_request.accountId = account.id
        expected_debt = -credit_request.amount

        # --- Действие: берём кредит ---
        credit = api_manager.user_steps.credit_user_valid(user, credit_request)

        # --- Проверка: ответ API ---
        assert credit.balance == credit_request.amount, (f'В ответе API баланс кредита {credit.balance}, '
                                                        f'а ожидали {credit_request.amount}')
        assert credit.id == account.id, f'Кредит привязан к счёту {credit.id}, а ожидали {account.id}'

        # --- Проверка: история кредитов ---
        credit_history = api_manager.user_steps.get_credit(user)
        credits = [c for c in credit_history.credits if c.creditId == credit.creditId]
        assert len(credits) == 1, f'В истории ожидали 1 кредит, а нашли {len(credits)}'
        assert credits[0].balance == expected_debt, (f'Долг в истории {credits[0].balance}, '
                                                  f'а ожидали {expected_debt}')

        # --- Проверка: база данных ---
        credit_from_db = CreditCrudDb.get_credit_by_id(db_session, credit.creditId)
        assert credit_from_db is not None, f'Кредит {credit.creditId} не найден в БД'
        assert credit_from_db.account_id == account.id, (f'В БД кредит привязан к счету{credit_from_db.id}, '
                                                         f'а ожидаем счет  {account.id}')
        assert credit_from_db.balance == expected_debt, (f'В БД долг по кредиту {credit_from_db.balance},'
                                                         f'а ожидаемый долг {expected_debt} ')

    @pytest.mark.parametrize(
        'amount,termMonths',
        [
            (5000.0, 1),
            (5001.0, 15),
            (7500.0, 30),
            (14999.0, 59),
            (15000.0, 60)
        ]
    )
    def test_credit_user_valid(self, api_manager, create_user_request, amount, termMonths):
        # --- Подготовка: пользователь с ролью кредита и счёт ---
        user = create_user_request(role='ROLE_CREDIT_SECRET')

        account = api_manager.user_steps.create_account(user)
        assert account.balance == 0, f'Начальный баланс счёта {account.balance}, а ожидали 0'

        credit_request = AccountCreditRequest(accountId=account.id, amount=amount, termMonths=termMonths)

        # --- Действие: берём кредит в допустимых границах ---
        credit = api_manager.user_steps.credit_user_valid(user, credit_request)

        # --- Проверка: ответ API ---
        assert credit.balance == credit_request.amount, (f'В ответе API баланс кредита {credit.balance}, '
                                                        f'а ожидали {credit_request.amount}')
        assert credit.id == account.id, f'Кредит привязан к счёту {credit.id}, а ожидали {account.id}'

    @pytest.mark.parametrize(
        'amount,termMonths,error_text',
        [
            (1.0, 12, 'Amount must be between 5000 and 15000'),
            (4999.0, 12, 'Amount must be between 5000 and 15000'),
            (15001.0, 12, 'Amount must be between 5000 and 15000'),
            (150000.0, 12, 'Amount must be between 5000 and 15000'),
            (10000.0, 61, 'Term months must be between 1 and 60'),
            (10000.0, 150, 'Term months must be between 1 and 60'),
            (-1, 12, 'Amount must be greater than 0'),
            (0, 12, 'Amount must be greater than 0'),
            (5000.0, -1, 'Term months must be between 1 and 60')
        ]
    )
    def test_credit_user_invalid(self, api_manager, create_user_request, amount, termMonths, error_text):
        # --- Подготовка: пользователь с ролью кредита и счёт ---
        user = create_user_request(role='ROLE_CREDIT_SECRET')

        account = api_manager.user_steps.create_account(user)
        assert account.balance == 0, f'Начальный баланс счёта {account.balance}, а ожидали 0'

        credit_request = AccountCreditRequest(accountId=account.id, amount=amount, termMonths=termMonths)

        # --- Действие: берём кредит вне лимита ---
        credit = api_manager.user_steps.credit_user_out_of_limit(user, credit_request)

        # --- Проверка: ответ API ---
        assert error_text in credit.text, f'Ожидали текст "{error_text}", а получили {credit.text}'

        account_after = api_manager.user_steps.get_account(user, account.id)
        assert account_after.balance == account.balance, (f'Баланс счёта после отказа {account_after.balance}, '
                                                           f'а ожидали {account.balance}')

    def test_credit_user_forbidden(self, api_manager, create_user_request, db_session: Session):
        # --- Подготовка: пользователь без роли кредита и счёт ---
        user = create_user_request()

        account = api_manager.user_steps.create_account(user)

        credit_request = AccountCreditRequest(accountId=account.id, amount=10000.0, termMonths=12)

        # --- Действие: берём кредит без нужной роли ---
        credit = api_manager.user_steps.credit_user_invalid(user, credit_request)

        # --- Проверка: ответ API ---
        assert 'ROLE_CREDIT access required' in credit.text, (f'Ожидали "ROLE_CREDIT access required", '
                                                               f'а получили {credit.text}')

        account_after = api_manager.user_steps.get_account(user, account.id)
        assert account_after.balance == account.balance, (f'Баланс счёта после отказа {account_after.balance}, '
                                                           f'а ожидали {account.balance}')
        assert account_after.transactions == [], (f'Ожидали пустую историю транзакций, '
                                                   f'а получили {account_after.transactions}')

        # --- Проверка: база данных ---
        assert CreditCrudDb.get_credit_by_account(db_session, account.id) == [], (f'У счета {account.id} появился кредит, '
                                                                                  f'хотя запрос отклонен')
