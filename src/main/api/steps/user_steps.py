from src.main.api.foundation.endpoint import Endpoint
from src.main.api.foundation.requesters.crud_requester import CrudRequester
from src.main.api.foundation.requesters.validate_crud_requester import ValidateCrudRequester
from src.main.api.models import create_user_request
from src.main.api.models.account_credit_request import AccountCreditRequest
from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.credit_repay_request import CreditRepayRequest
from src.main.api.models.money_transfer_request import MoneyTransferRequest
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.api.steps.base_steps import BaseSteps


class UserSteps(BaseSteps):
    def create_account(self,create_user_request: CreateUserRequest):
        account_response = ValidateCrudRequester(
            RequestSpecs.auth_headers(create_user_request.username,create_user_request.password),
            Endpoint.CREATE_USER_ACCOUNT,
            ResponseSpecs.request_create()
        ).post()

        return account_response


    def deposit_account(self,create_user_request: CreateUserRequest, account_deposit_request: AccountDepositRequest):
        deposit_response = ValidateCrudRequester(
            RequestSpecs.auth_headers(create_user_request.username,create_user_request.password),
            Endpoint.ACCOUNT_DEPOSIT,
            ResponseSpecs.request_ok()
        ).post(account_deposit_request)

        return deposit_response

    def deposit_account_invalid_unauth(self, account_deposit_request: AccountDepositRequest):
        deposit_response = CrudRequester(
            RequestSpecs.unauth_headers(),
            Endpoint.ACCOUNT_DEPOSIT,
            ResponseSpecs.request_not_authentication()
        ).post(account_deposit_request)

        return deposit_response

    def deposit_account_invalid_over_mone(self,create_user_request: CreateUserRequest, account_deposit_request: AccountDepositRequest):
        deposit_response = CrudRequester(
            RequestSpecs.auth_headers(create_user_request.username,create_user_request.password),
            Endpoint.ACCOUNT_DEPOSIT,
            ResponseSpecs.request_bad()
        ).post(account_deposit_request)
        return deposit_response

    def money_transfer_valid(self,create_user_request:CreateUserRequest, money_transfer_request: MoneyTransferRequest):
        transfer_response = ValidateCrudRequester(
            RequestSpecs.auth_headers(create_user_request.username,create_user_request.password),
            Endpoint.MONEY_TRANSFER,
            ResponseSpecs.request_ok()
        ).post(money_transfer_request)
        return transfer_response

    def money_transfer_invalid(self,create_user_request:CreateUserRequest, money_transfer_request: MoneyTransferRequest):
        transfer_response = CrudRequester(
            RequestSpecs.auth_headers(create_user_request.username,create_user_request.password),
            Endpoint.MONEY_TRANSFER,
            ResponseSpecs.request_no_limit()
        ).post(money_transfer_request)
        return transfer_response

    def money_transfer_invalid_zero(self, create_user_request:CreateUserRequest, money_transfer_request: MoneyTransferRequest):
        transfer_response = CrudRequester(
            RequestSpecs.auth_headers(create_user_request.username,create_user_request.password),
            Endpoint.MONEY_TRANSFER,
            ResponseSpecs.request_bad()
        ).post(money_transfer_request)
        return transfer_response

    def credit_user_valid(self,create_user_request:CreateUserRequest, account_credit_request: AccountCreditRequest ):
        credit_response = ValidateCrudRequester(
            RequestSpecs.auth_headers(create_user_request.username,create_user_request.password),
            Endpoint.USER_CREDIT,
            ResponseSpecs.request_create()
        ).post(account_credit_request)
        return credit_response

    def credit_user_invalid(self,create_user_request:CreateUserRequest, account_credit_request: AccountCreditRequest):
        credit_response = CrudRequester(
            RequestSpecs.auth_headers(create_user_request.username,create_user_request.password),
            Endpoint.USER_CREDIT,
            ResponseSpecs.request_forbidden()
        ).post(account_credit_request)
        return credit_response

    # Swagger обещает 422 "Credit amount cannot exceed 15000", банк отдаёт 400 "Amount must be between 5000 and 15000"
    def credit_user_out_of_limit(self, create_user_request:CreateUserRequest, account_credit_request: AccountCreditRequest):
        credit_response = CrudRequester(
            RequestSpecs.auth_headers(create_user_request.username,create_user_request.password),
            Endpoint.USER_CREDIT,
            ResponseSpecs.request_bad()
        ).post(account_credit_request)
        return credit_response

    def repay_credit_valid(self, create_user_request:CreateUserRequest, credit_repay_request: CreditRepayRequest):
        repay_response = ValidateCrudRequester(
            RequestSpecs.auth_headers(create_user_request.username,create_user_request.password),
            Endpoint.CREDIT_REPAY,
            ResponseSpecs.request_ok()
        ).post(credit_repay_request)
        return repay_response

    def repay_credit_invalid(self, create_user_request:CreateUserRequest, credit_repay_request: CreditRepayRequest):
        repay_response = CrudRequester(
            RequestSpecs.auth_headers(create_user_request.username,create_user_request.password),
            Endpoint.CREDIT_REPAY,
            ResponseSpecs.request_no_limit()
        ).post(credit_repay_request)
        return repay_response

