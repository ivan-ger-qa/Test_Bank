import pytest

from src.main.api.generator.model_generator import RandomModelGenerator
from src.main.api.models.account_credit_request import AccountCreditRequest


@pytest.mark.apis
class TestCreditUser:
    def test_credit_user(self, api_manager, create_user_request):
        user = create_user_request(role='ROLE_CREDIT_SECRET')

        account = api_manager.user_steps.create_account(user)

        credit_request = RandomModelGenerator.generate(AccountCreditRequest)
        credit_request.accountId = account.id
        credit = api_manager.user_steps.credit_user_valid(user, credit_request)
        assert credit.balance == credit_request.amount

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
        user = create_user_request(role='ROLE_CREDIT_SECRET')

        account = api_manager.user_steps.create_account(user)
        assert account.balance == 0

        credit_request = AccountCreditRequest(accountId=account.id, amount=amount, termMonths=termMonths)
        credit = api_manager.user_steps.credit_user_valid(user, credit_request)
        assert credit.balance == credit_request.amount

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
        user = create_user_request(role='ROLE_CREDIT_SECRET')

        account = api_manager.user_steps.create_account(user)
        assert account.balance == 0

        credit_request = AccountCreditRequest(accountId=account.id, amount=amount, termMonths=termMonths)
        credit = api_manager.user_steps.credit_user_out_of_limit(user, credit_request)
        assert error_text in credit.text

    def test_credit_user_forbiden(self, api_manager, create_user_request):
        user = create_user_request()

        account = api_manager.user_steps.create_account(user)

        credit_request = AccountCreditRequest(accountId=account.id, amount=10000.0, termMonths=12)
        credit = api_manager.user_steps.credit_user_invalid(user, credit_request)
        assert 'ROLE_CREDIT access required' in credit.text
