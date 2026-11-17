import pytest
from sqlalchemy.orm import Session

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.account_credit_response import AccountCreditResponse
from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.credit_repay_request import CreditRepayRequest
from src.main.api.utils import find_credit_by_id
from src.main.db.crud.account_crud import AccountCrudDb
from src.main.db.crud.credit_crud import CreditCrudDb
from src.main.db.crud.transaction_crud import TransactionCrudDb


@pytest.mark.apis
class TestCreditRepay:
    def test_credit_repay_valid(self, api_manager: ApiManager, credit_user: CreateUserRequest,
                                credit_account: CreateAccountResponse, credit: AccountCreditResponse,
                                db_session: Session) -> None:
        # --- Подготовка: пользователь с ролью кредита, счёт и кредит ---

        repay_request = CreditRepayRequest(creditId=credit.creditId,
                                           accountId=credit_account.id,
                                           amount=credit.amount)
        expected_debt = -credit.amount + repay_request.amount

        # --- Действие: погашаем кредит полностью ---
        repay = api_manager.user_steps.repay_credit_valid(credit_user, repay_request)

        # --- Проверка: ответ API ---
        assert repay.amountDeposited == repay_request.amount, (f'В ответе API зачислено {repay.amountDeposited}, '
                                                               f'а ожидали {repay_request.amount}')

        # --- Проверка: база данных ---
        credit_from_db = CreditCrudDb.get_credit_by_id(db_session, credit.creditId)
        assert credit_from_db is not None, f'Кредит {credit.creditId} не найден в БД'
        assert credit_from_db.balance == expected_debt, (f'В БД по факту {credit_from_db.balance}, '
                                                         f'а ожидали {expected_debt}')

    @pytest.mark.parametrize(
        'offset, error_text', [
            (1.0, 'Repayment amount exceeds remaining debt'),
            (500.0, 'Repayment amount exceeds remaining debt'),
            (-1.0, 'The amount is not enough'),
            (-500.0, 'The amount is not enough'),
        ]
    )
    def test_credit_repay_invalid(self, api_manager: ApiManager, credit_user: CreateUserRequest,
                                  credit_account: CreateAccountResponse, funded_credit: AccountCreditResponse,
                                  offset: float, error_text: str) -> None:
        # --- Подготовка: пользователь с ролью кредита, счёт, деньги и кредит ---

        repay_request = CreditRepayRequest(creditId=funded_credit.creditId,
                                           accountId=credit_account.id,
                                           amount=funded_credit.amount + offset)

        # --- Действие: погашаем кредит неполной или излишней суммой ---
        repay = api_manager.user_steps.repay_credit_invalid(credit_user, repay_request)

        # --- Проверка: ответ API ---
        assert error_text in repay.text, f'Ожидали текст "{error_text}", а получили {repay.text}'

        # --- Проверка: история кредитов ---
        credit_history = api_manager.user_steps.get_credit(credit_user)
        credits = find_credit_by_id(credit_history.credits, funded_credit.creditId)
        assert len(credits) == 1, f'В истории ожидали 1 кредит, а нашли {len(credits)}'
        assert credits[0].balance == -funded_credit.amount, (f'Долг в истории {credits[0].balance}, '
                                                             f'а ожидали {-funded_credit.amount}')

    @pytest.mark.usefixtures('spent_credit')
    def test_credit_repay_no_limit(self, api_manager: ApiManager, credit_user: CreateUserRequest,
                                   credit_account: CreateAccountResponse,
                                   credit: AccountCreditResponse) -> None:
        # --- Подготовка: пользователь с ролью кредита, два счёта и кредит ---

        repay_request = CreditRepayRequest(creditId=credit.creditId,
                                           accountId=credit_account.id,
                                           amount=credit.amount)

        # --- Действие: погашаем кредит, когда денег на счёте не хватает ---
        repay = api_manager.user_steps.repay_credit_invalid(credit_user, repay_request)

        # --- Проверка: ответ API ---
        assert 'Insufficient funds' in repay.text, (f'Ожидали текст "Insufficient funds", '
                                                    f'а получили {repay.text}')

        # --- Проверка: история кредитов ---
        credit_history = api_manager.user_steps.get_credit(credit_user)
        credits = find_credit_by_id(credit_history.credits, credit.creditId)
        assert len(credits) == 1, f'В истории ожидали 1 кредит, а нашли {len(credits)}'
        assert credits[0].balance == -credit.amount, (f'Долг в истории {credits[0].balance}, '
                                                      f'а ожидали {-credit.amount}')

    @pytest.mark.usefixtures('repaid_credit')
    def test_credit_repay_twice(self, api_manager: ApiManager, credit_user: CreateUserRequest,
                                credit_account: CreateAccountResponse, funded_credit: AccountCreditResponse,
                                db_session: Session) -> None:
        # --- Подготовка: пользователь с ролью кредита, счёт, деньги и кредит ---

        repay_request = CreditRepayRequest(creditId=funded_credit.creditId,
                                           accountId=credit_account.id,
                                           amount=funded_credit.amount)

        # --- Действие: погашаем кредит, затем повторяем то же погашение ---
        repay_response = api_manager.user_steps.credit_repay_conflict(credit_user, repay_request)

        # --- Проверка: ответ API ---
        assert 'already been repaid' in repay_response.text, (f'Ожидали текст "already been repaid", '
                                                              f'а получили {repay_response.text}')

        # --- Проверка: база данных ---
        account_from_db = AccountCrudDb.get_account_by_id(db_session, credit_account.id)
        assert account_from_db is not None, f'Счет  {credit_account.id} не найден в бд'
        expected_balance = funded_credit.balance - funded_credit.amount
        assert account_from_db.balance == expected_balance, (f'В БД по факту {account_from_db.balance}, '
                                                             f'а ожидали {expected_balance}, '
                                                             f'деньги списались второй раз')

        repayments_from_db = TransactionCrudDb.get_repayments(db_session, funded_credit.creditId)
        assert len(repayments_from_db) == 1, (f'В БД фактически найдено  {len(repayments_from_db)} погашения кредита, '
                                              f'ожидали 1 {repayments_from_db}, '
                                              f'повторное погашение не должно записываться')
