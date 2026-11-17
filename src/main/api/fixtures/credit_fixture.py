import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.configs.constants import MAX_DEPOSIT
from src.main.api.generator.model_generator import RandomModelGenerator
from src.main.api.models.account_credit_request import AccountCreditRequest
from src.main.api.models.account_credit_response import AccountCreditResponse
from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.credit_repay_request import CreditRepayRequest
from src.main.api.models.credit_repay_response import CreditRepayResponse
from src.main.api.models.money_transfer_request import MoneyTransferRequest
from src.main.api.models.money_transfer_response import MoneyTransferResponse


# Выдаёт кредит на пустой счёт
@pytest.fixture
def credit(api_manager: ApiManager, credit_user: CreateUserRequest,
           credit_account: CreateAccountResponse) -> AccountCreditResponse:
    credit_request = RandomModelGenerator.generate(AccountCreditRequest)
    credit_request.accountId = credit_account.id
    credit = api_manager.user_steps.credit_user_valid(credit_user, credit_request)
    return credit


# Два пополнения, затем кредит
@pytest.fixture
def funded_credit(api_manager: ApiManager, credit_user: CreateUserRequest,
                  credit_account: CreateAccountResponse) -> AccountCreditResponse:
    deposit_request = AccountDepositRequest(accountId=credit_account.id, amount=MAX_DEPOSIT)
    api_manager.user_steps.deposit_account(credit_user, deposit_request)
    api_manager.user_steps.deposit_account(credit_user, deposit_request)

    credit_request = RandomModelGenerator.generate(AccountCreditRequest)
    credit_request.accountId = credit_account.id
    credit = api_manager.user_steps.credit_user_valid(credit_user, credit_request)
    return credit


# Половину кредита переводит на второй счёт
@pytest.fixture
def spent_credit(api_manager: ApiManager, credit_user: CreateUserRequest,
                 credit: AccountCreditResponse, credit_account: CreateAccountResponse,
                 second_credit_account: CreateAccountResponse) -> MoneyTransferResponse:
    transfer_request = MoneyTransferRequest(fromAccountId=credit_account.id, toAccountId=second_credit_account.id,
                                            amount=credit.amount / 2)
    transfer = api_manager.user_steps.money_transfer_valid(credit_user, transfer_request)
    return transfer


# Полностью погашает кредит больше суммы долга
@pytest.fixture
def repaid_credit(api_manager: ApiManager, credit_user: CreateUserRequest,
                  credit_account: CreateAccountResponse,
                  funded_credit: AccountCreditResponse) -> CreditRepayResponse:
    repay_request = CreditRepayRequest(creditId=funded_credit.creditId, accountId=credit_account.id,
                                       amount=funded_credit.amount)
    return api_manager.user_steps.repay_credit_valid(credit_user, repay_request)
