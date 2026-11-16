import pytest
from sqlalchemy.orm import Session

from src.main.api.generator.model_generator import RandomModelGenerator
from src.main.api.models.account_credit_request import AccountCreditRequest
from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.credit_repay_request import CreditRepayRequest
from src.main.api.models.money_transfer_request import MoneyTransferRequest
from src.main.db.crud.account_crud import AccountCrudDb
from src.main.db.crud.credit_crud import CreditCrudDb
from src.main.db.crud.transaction_crud import TransactionCrudDb

MAX_DEPOSIT = 9000.0


@pytest.mark.apis
class TestCreditRepay:
    def test_credit_repay_valid(self, api_manager, create_user_request, db_session: Session):
        # --- Подготовка: пользователь с ролью кредита, счёт и кредит ---
        user = create_user_request(role='ROLE_CREDIT_SECRET')

        account = api_manager.user_steps.create_account(user)
        assert account.balance == 0, f'Начальный баланс счёта {account.balance}, а ожидали 0'

        credit_request = RandomModelGenerator.generate(AccountCreditRequest)
        credit_request.accountId = account.id
        credit = api_manager.user_steps.credit_user_valid(user, credit_request)
        assert credit.balance == account.balance + credit_request.amount, (f'Баланс кредита {credit.balance}, '
                                                                           f'а ожидали {account.balance + credit_request.amount}')

        repay_request = CreditRepayRequest(creditId=credit.creditId,
                                           accountId=account.id,
                                           amount=credit.amount)
        expected_balance = credit.balance - repay_request.amount
        expected_debt = -credit.amount + repay_request.amount

        # --- Действие: погашаем кредит полностью ---
        repay = api_manager.user_steps.repay_credit_valid(user, repay_request)

        # --- Проверка: ответ API ---
        assert repay.amountDeposited == repay_request.amount, (f'В ответе API зачислено {repay.amountDeposited}, '
                                                              f'а ожидали {repay_request.amount}')
        assert credit.creditId == repay.creditId, f'В ответе creditId {repay.creditId}, а ожидали {credit.creditId}'

        account_after = api_manager.user_steps.get_account(user, account.id)
        assert account_after.balance == expected_balance, (f'Баланс счёта {account_after.balance}, '
                                                          f'а ожидали {expected_balance}')

        # --- Проверка: история кредитов ---
        credit_history = api_manager.user_steps.get_credit(user)
        credits = [c for c in credit_history.credits if c.creditId == credit.creditId]
        assert len(credits) == 1, f'В истории ожидали 1 кредит, а нашли {len(credits)}'
        assert credits[0].balance == expected_debt, (f'Долг в истории {credits[0].balance}, '
                                                  f'а ожидали {expected_debt}')

        # --- Проверка: база данных ---
        credit_from_db = CreditCrudDb.get_credit_by_id(db_session, credit.creditId)
        assert credit_from_db is not None, f'Кредит {credit.creditId} не найден в БД'
        assert credit_from_db.balance == expected_debt, (f'В БД по факту {credit_from_db.balance}, '
                                                         f'а ожидали {expected_debt}')
        account_from_db = AccountCrudDb.get_account_by_id(db_session, account.id)
        assert account_from_db is not None, f'Счет  {account.id} не найден в бд'
        assert account_from_db.balance == expected_balance, (f'В БД по факту {account_from_db.balance}, '
                                                          f'а ожидали {expected_balance}')

        repayments_from_db = TransactionCrudDb.get_repayments(db_session, credit.creditId)
        assert len(repayments_from_db) == 1, (f'В БД фактически найдено  {len(repayments_from_db)} погашения кредита, '
                                              f'ожидали 1 {repayments_from_db}')




    @pytest.mark.parametrize(
        'offset, error_text', [
            (1.0, 'Repayment amount exceeds remaining debt'),
            (500.0, 'Repayment amount exceeds remaining debt'),
            (-1.0, 'The amount is not enough'),
            (-500.0, 'The amount is not enough'),
        ]
    )
    def test_credit_repay_invalid(self, api_manager, create_user_request, offset, error_text):
        # --- Подготовка: пользователь с ролью кредита, счёт, деньги и кредит ---
        user = create_user_request(role='ROLE_CREDIT_SECRET')

        account = api_manager.user_steps.create_account(user)
        assert account.balance == 0, f'Начальный баланс счёта {account.balance}, а ожидали 0'

        deposit_request = RandomModelGenerator.generate(AccountDepositRequest)
        deposit_request.accountId = account.id
        api_manager.user_steps.deposit_account(user, deposit_request)

        credit_request = RandomModelGenerator.generate(AccountCreditRequest)
        credit_request.accountId = account.id
        credit = api_manager.user_steps.credit_user_valid(user, credit_request)

        repay_request = CreditRepayRequest(creditId=credit.creditId,
                                           accountId=account.id,
                                           amount=credit.amount + offset)

        # --- Действие: погашаем кредит неполной или излишней суммой ---
        repay = api_manager.user_steps.repay_credit_invalid(user, repay_request)

        # --- Проверка: ответ API ---
        assert error_text in repay.text, f'Ожидали текст "{error_text}", а получили {repay.text}'

        account_after = api_manager.user_steps.get_account(user, account.id)
        assert account_after.balance == credit.balance, (f'Баланс счёта после отказа {account_after.balance}, '
                                                           f'а ожидали {credit.balance}')

        # --- Проверка: история кредитов ---
        credit_history = api_manager.user_steps.get_credit(user)
        credits = [c for c in credit_history.credits if c.creditId == credit.creditId]
        assert len(credits) == 1, f'В истории ожидали 1 кредит, а нашли {len(credits)}'
        assert credits[0].balance == -credit.amount, (f'Долг в истории {credits[0].balance}, '
                                                   f'а ожидали {-credit.amount}')

    def test_credit_repay_no_limit(self, api_manager, create_user_request):
        # --- Подготовка: пользователь с ролью кредита, два счёта и кредит ---
        user = create_user_request(role='ROLE_CREDIT_SECRET')

        account_one = api_manager.user_steps.create_account(user)
        account_two = api_manager.user_steps.create_account(user)

        credit_request = RandomModelGenerator.generate(AccountCreditRequest)
        credit_request.accountId = account_one.id
        credit = api_manager.user_steps.credit_user_valid(user, credit_request)

        transfer_request = MoneyTransferRequest(fromAccountId=account_one.id,
                                                toAccountId=account_two.id,
                                                amount=credit.amount / 2)
        api_manager.user_steps.money_transfer_valid(user, transfer_request)

        repay_request = CreditRepayRequest(creditId=credit.creditId,
                                           accountId=account_one.id,
                                           amount=credit.amount)

        # --- Действие: погашаем кредит, когда денег на счёте не хватает ---
        repay = api_manager.user_steps.repay_credit_invalid(user, repay_request)

        # --- Проверка: ответ API ---
        assert 'Insufficient funds' in repay.text, (f'Ожидали текст "Insufficient funds", '
                                                     f'а получили {repay.text}')

        account_after = api_manager.user_steps.get_account(user, account_one.id)
        assert account_after.balance == credit.balance / 2, (f'Баланс счёта {account_after.balance}, '
                                                            f'а ожидали {credit.balance / 2}')

        # --- Проверка: история кредитов ---
        credit_history = api_manager.user_steps.get_credit(user)
        credits = [c for c in credit_history.credits if c.creditId == credit.creditId]
        assert len(credits) == 1, f'В истории ожидали 1 кредит, а нашли {len(credits)}'
        assert credits[0].balance == -credit.amount, (f'Долг в истории {credits[0].balance}, '
                                                   f'а ожидали {-credit.amount}')

    def test_credit_repay_twice(self, api_manager, create_user_request, db_session):
        # --- Подготовка: пользователь с ролью кредита, счёт, деньги и кредит ---
        user = create_user_request(role='ROLE_CREDIT_SECRET')

        account = api_manager.user_steps.create_account(user)

        deposit_request = AccountDepositRequest(accountId=account.id, amount=MAX_DEPOSIT)
        api_manager.user_steps.deposit_account(user, deposit_request)
        api_manager.user_steps.deposit_account(user, deposit_request)

        credit_request = RandomModelGenerator.generate(AccountCreditRequest)
        credit_request.accountId = account.id
        credit = api_manager.user_steps.credit_user_valid(user, credit_request)

        repay_request = CreditRepayRequest(creditId=credit.creditId,
                                           accountId=account.id,
                                           amount=credit.amount)

        # --- Действие: погашаем кредит, затем повторяем то же погашение ---
        api_manager.user_steps.repay_credit_valid(user, repay_request)
        account_after_first = api_manager.user_steps.get_account(user, account.id)
        expected_balance = account_after_first.balance
        expected_debt = - credit.amount + repay_request.amount

        repay_response = api_manager.user_steps.credit_repay_conflict(user, repay_request)

        # --- Проверка: ответ API ---
        assert 'already been repaid' in repay_response.text, (f'Ожидали текст "already been repaid", '
                                                               f'а получили {repay_response.text}')

        account_after_second = api_manager.user_steps.get_account(user, account.id)
        assert account_after_second.balance == expected_balance, (f'Баланс счёта {account_after_second.balance}, '
                                                                 f'а ожидали {expected_balance}, '
                                                                 f'деньги списались второй раз')

        # --- Проверка: история кредитов ---
        credit_history = api_manager.user_steps.get_credit(user)
        credits = [c for c in credit_history.credits if c.creditId == credit.creditId]
        assert len(credits) == 1, f'В истории ожидали 1 кредит, а нашли {len(credits)}'
        assert credits[0].balance == expected_debt, (f'Долг в истории {credits[0].balance}, '
                                                  f'а ожидали {expected_debt}')

        # --- Проверка: база данных ---
        credit_from_db = CreditCrudDb.get_credit_by_id(db_session, credit.creditId)
        assert credit_from_db is not None, f'Кредит {credit.creditId} не найден в БД'
        assert credit_from_db.balance == expected_debt, (f'В БД по факту {credit_from_db.balance}, '
                                                         f'а ожидали {expected_debt} '
                                                         f'повторное погашение, не должно менять долг')
        account_from_db = AccountCrudDb.get_account_by_id(db_session, account.id)
        assert account_from_db is not None, f'Счет  {account.id} не найден в бд'
        assert account_from_db.balance == expected_balance, (f'В БД по факту {account_from_db.balance}, '
                                                             f'а ожидали {expected_balance}, '
                                                             f'деньги списались второй раз')

        repayments_from_db = TransactionCrudDb.get_repayments(db_session, credit.creditId)
        assert len(repayments_from_db) == 1, (f'В БД фактически найдено  {len(repayments_from_db)} погашения кредита, '
                                              f'ожидали 1 {repayments_from_db}, '
                                              f'повторное погашение не должно записываться')

