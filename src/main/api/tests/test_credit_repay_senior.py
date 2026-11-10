import pytest

from src.main.api.generator.model_generator import RandomModelGenerator
from src.main.api.models.account_credit_request import AccountCreditRequest
from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.credit_repay_request import CreditRepayRequest
from src.main.api.models.money_transfer_request import MoneyTransferRequest


@pytest.mark.apis
class TestCreditRepay:
    def test_credit_repay_valid(self, api_manager, create_user_request):
        user = create_user_request(role='ROLE_CREDIT_SECRET')

        account = api_manager.user_steps.create_account(user)
        assert account.balance == 0

        credit_request = RandomModelGenerator.generate(AccountCreditRequest)
        credit_request.accountId = account.id
        credit = api_manager.user_steps.credit_user_valid(user, credit_request)
        assert credit.balance == account.balance + credit_request.amount

        repay_request = CreditRepayRequest(creditId=credit.creditId, accountId=account.id, amount=credit.amount)
        repay = api_manager.user_steps.repay_credit_valid(user, repay_request)
        assert repay.amountDeposited == repay_request.amount
        assert credit.creditId == repay.creditId

    @pytest.mark.parametrize(
        'offset, error_text', [
            (1.0, 'Repayment amount exceeds remaining debt'),
            (500.0, 'Repayment amount exceeds remaining debt'),
            (-1.0, 'The amount is not enough'),
            (-500.0, 'The amount is not enough'),
        ]
    )
    def test_credit_repay_invalid(self, api_manager, create_user_request, offset, error_text):
        user = create_user_request(role='ROLE_CREDIT_SECRET')

        account = api_manager.user_steps.create_account(user)
        assert account.balance == 0

        deposit_request = RandomModelGenerator.generate(AccountDepositRequest)
        deposit_request.accountId = account.id
        api_manager.user_steps.deposit_account(user, deposit_request)

        credit_request = RandomModelGenerator.generate(AccountCreditRequest)
        credit_request.accountId = account.id
        credit = api_manager.user_steps.credit_user_valid(user, credit_request)

        repay_request = CreditRepayRequest(creditId=credit.creditId, accountId=account.id,
                                           amount=credit.amount + offset)
        repay = api_manager.user_steps.repay_credit_invalid(user, repay_request)
        assert error_text in repay.text

    def test_credit_repay_no_limit(self, api_manager, create_user_request):
        user = create_user_request(role='ROLE_CREDIT_SECRET')

        account_one = api_manager.user_steps.create_account(user)
        account_two = api_manager.user_steps.create_account(user)

        credit_request = RandomModelGenerator.generate(AccountCreditRequest)
        credit_request.accountId = account_one.id
        credit = api_manager.user_steps.credit_user_valid(user, credit_request)

        transfer_request = MoneyTransferRequest(fromAccountId=account_one.id, toAccountId=account_two.id,
                                                amount=credit.amount/2)
        api_manager.user_steps.money_transfer_valid(user, transfer_request)

        repay_request = CreditRepayRequest(creditId=credit.creditId, accountId=account_one.id, amount=credit.amount)
        repay = api_manager.user_steps.repay_credit_invalid(user, repay_request)
        assert 'Insufficient funds' in repay.text



