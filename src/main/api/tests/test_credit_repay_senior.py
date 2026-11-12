import pytest

from src.main.api.generator.model_generator import RandomModelGenerator
from src.main.api.models.account_credit_request import AccountCreditRequest
from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.credit_repay_request import CreditRepayRequest
from src.main.api.models.money_transfer_request import MoneyTransferRequest

MAX_DEPOSIT = 9000.0


@pytest.mark.apis
class TestCreditRepay:
    def test_credit_repay_valid(self, api_manager, create_user_request):
        # --- Подготовка: пользователь с ролью кредита, счёт и кредит ---
        user = create_user_request(role='ROLE_CREDIT_SECRET')

        account = api_manager.user_steps.create_account(user)
        assert account.balance == 0

        credit_request = RandomModelGenerator.generate(AccountCreditRequest)
        credit_request.accountId = account.id
        credit = api_manager.user_steps.credit_user_valid(user, credit_request)
        assert credit.balance == account.balance + credit_request.amount

        repay_request = CreditRepayRequest(creditId=credit.creditId,
                                           accountId=account.id,
                                           amount=credit.amount)

        # --- Действие: погашаем кредит полностью ---
        repay = api_manager.user_steps.repay_credit_valid(user, repay_request)

        # --- Проверка: ответ API ---
        assert repay.amountDeposited == repay_request.amount
        assert credit.creditId == repay.creditId

        account_after = api_manager.user_steps.get_account(user, account.id)
        assert account_after.balance == credit.balance - repay_request.amount

        # --- Проверка: история кредитов ---
        credit_history = api_manager.user_steps.get_credit(user)
        credits = [c for c in credit_history.credits if c.creditId == credit.creditId]
        assert len(credits) == 1
        assert credits[0].balance == -credit.amount + repay_request.amount

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
        assert account.balance == 0

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
        assert error_text in repay.text

        account_after = api_manager.user_steps.get_account(user, account.id)
        assert account_after.balance == credit.balance

        # --- Проверка: история кредитов ---
        credit_history = api_manager.user_steps.get_credit(user)
        credits = [c for c in credit_history.credits if c.creditId == credit.creditId]
        assert len(credits) == 1
        assert credits[0].balance == -credit.amount

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
        assert 'Insufficient funds' in repay.text

        account_after = api_manager.user_steps.get_account(user, account_one.id)
        assert account_after.balance == credit.balance / 2

        # --- Проверка: история кредитов ---
        credit_history = api_manager.user_steps.get_credit(user)
        credits = [c for c in credit_history.credits if c.creditId == credit.creditId]
        assert len(credits) == 1
        assert credits[0].balance == -credit.amount

    def test_credit_repay_twice(self, api_manager, create_user_request):
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

        repay_responce = api_manager.user_steps.credit_repay_conflict(user, repay_request)

        # --- Проверка: ответ API ---
        assert 'already been repaid' in repay_responce.text

        account_after_second = api_manager.user_steps.get_account(user, account.id)
        assert account_after_second.balance == account_after_first.balance

        # --- Проверка: история кредитов ---
        credit_history = api_manager.user_steps.get_credit(user)
        credits = [c for c in credit_history.credits if c.creditId == credit.creditId]
        assert len(credits) == 1
        assert credits[0].balance == -credit.amount + repay_request.amount
