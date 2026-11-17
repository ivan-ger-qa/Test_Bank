import pytest
from sqlalchemy.orm import Session

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generator.model_generator import RandomModelGenerator
from src.main.api.models.account_credit_request import AccountCreditRequest
from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.db.crud.credit_crud import CreditCrudDb


@pytest.mark.apis
class TestCreditUser:
    def test_credit_user(self, api_manager: ApiManager, credit_user: CreateUserRequest,
                         credit_account: CreateAccountResponse, db_session: Session) -> None:
        # --- Подготовка: пользователь с ролью кредита и счёт ---

        credit_request = RandomModelGenerator.generate(AccountCreditRequest)
        credit_request.accountId = credit_account.id
        expected_debt = -credit_request.amount

        # --- Действие: берём кредит ---
        credit = api_manager.user_steps.credit_user_valid(credit_user, credit_request)

        # --- Проверка: ответ API ---
        assert credit.balance == credit_request.amount, (f'В ответе API баланс кредита {credit.balance}, '
                                                         f'а ожидали {credit_request.amount}')
        assert credit.id == credit_account.id, f'Кредит привязан к счёту {credit.id}, а ожидали {credit_account.id}'

        # --- Проверка: база данных ---
        credit_from_db = CreditCrudDb.get_credit_by_id(db_session, credit.creditId)
        assert credit_from_db is not None, f'Кредит {credit.creditId} не найден в БД'
        assert credit_from_db.account_id == credit_account.id, (f'В БД кредит привязан к счету{credit_from_db.id}, '
                                                                f'а ожидаем счет  {credit_account.id}')
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
    def test_credit_user_valid(self, api_manager: ApiManager, credit_user: CreateUserRequest,
                               credit_account: CreateAccountResponse, amount: float, termMonths: int) -> None:
        # --- Подготовка: пользователь с ролью кредита и счёт ---

        credit_request = AccountCreditRequest(accountId=credit_account.id, amount=amount, termMonths=termMonths)

        # --- Действие: берём кредит в допустимых границах ---
        credit = api_manager.user_steps.credit_user_valid(credit_user, credit_request)

        # --- Проверка: ответ API ---
        assert credit.balance == credit_request.amount, (f'В ответе API баланс кредита {credit.balance}, '
                                                         f'а ожидали {credit_request.amount}')

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
    def test_credit_user_invalid(self, api_manager: ApiManager, credit_user: CreateUserRequest,
                                 credit_account: CreateAccountResponse, amount: float, termMonths: int,
                                 error_text: str) -> None:
        # --- Подготовка: пользователь с ролью кредита и счёт ---

        credit_request = AccountCreditRequest(accountId=credit_account.id, amount=amount, termMonths=termMonths)

        # --- Действие: берём кредит вне лимита ---
        credit = api_manager.user_steps.credit_user_out_of_limit(credit_user, credit_request)

        # --- Проверка: ответ API ---
        assert error_text in credit.text, f'Ожидали текст "{error_text}", а получили {credit.text}'

    def test_credit_user_forbidden(self, api_manager: ApiManager, user: CreateUserRequest,
                                   account: CreateAccountResponse, db_session: Session) -> None:
        # --- Подготовка: пользователь без роли кредита и счёт ---

        credit_request = AccountCreditRequest(accountId=account.id, amount=10000.0, termMonths=12)

        # --- Действие: берём кредит без нужной роли ---
        credit = api_manager.user_steps.credit_user_invalid(user, credit_request)

        # --- Проверка: ответ API ---
        assert 'ROLE_CREDIT access required' in credit.text, (f'Ожидали "ROLE_CREDIT access required", '
                                                              f'а получили {credit.text}')

        # --- Проверка: база данных ---
        assert CreditCrudDb.get_credit_by_account(db_session, account.id) == [], (
            f'У счета {account.id} появился кредит, '
            f'хотя запрос отклонен')
