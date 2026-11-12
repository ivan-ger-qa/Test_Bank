import allure

from src.main.api.foundation.endpoint import Endpoint
from src.main.api.foundation.requesters.crud_requester import CrudRequester
from src.main.api.foundation.requesters.validate_crud_requester import (
    ValidateCrudRequester,
)
from src.main.api.models.account_credit_request import AccountCreditRequest
from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.credit_repay_request import CreditRepayRequest
from src.main.api.models.money_transfer_request import MoneyTransferRequest
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.api.steps.base_steps import BaseSteps


class UserSteps(BaseSteps):
    # ------------------------------------------------------------- АККАУНТЫ --
    @allure.step('Создаём счёт — 201')
    def create_account(self, create_user_request: CreateUserRequest):
        account_response = ValidateCrudRequester(
            RequestSpecs.auth_headers(create_user_request.username, create_user_request.password),
            Endpoint.CREATE_USER_ACCOUNT,
            ResponseSpecs.request_create()
        ).post()
        return account_response

    @allure.step('Читаем счёт — 200')
    def get_account(self, create_user_request: CreateUserRequest, account_id: int):
        account_response = ValidateCrudRequester(
            RequestSpecs.auth_headers(create_user_request.username, create_user_request.password),
            Endpoint.ACCOUNT_TRANSACTIONS,
            ResponseSpecs.request_ok()
        ).get(account_id)
        return account_response

    # ----------------------------------------------------------- ПОПОЛНЕНИЕ --
    @allure.step('Пополняем счёт — 200')
    def deposit_account(self, create_user_request: CreateUserRequest, account_deposit_request: AccountDepositRequest):
        deposit_response = ValidateCrudRequester(
            RequestSpecs.auth_headers(create_user_request.username, create_user_request.password),
            Endpoint.ACCOUNT_DEPOSIT,
            ResponseSpecs.request_ok()
        ).post(account_deposit_request)
        return deposit_response

    @allure.step('Негатив: пополнение без токена — 401')
    def deposit_account_invalid_unauth(self, account_deposit_request: AccountDepositRequest):
        deposit_response = CrudRequester(
            RequestSpecs.unauth_headers(),
            Endpoint.ACCOUNT_DEPOSIT,
            ResponseSpecs.request_not_authentication()
        ).post(account_deposit_request)
        return deposit_response

    @allure.step('Негатив: сумма вне лимита 1000–9000 — 400')
    def deposit_account_invalid_over_money(self, create_user_request: CreateUserRequest,
                                           account_deposit_request: AccountDepositRequest):
        deposit_response = CrudRequester(
            RequestSpecs.auth_headers(create_user_request.username, create_user_request.password),
            Endpoint.ACCOUNT_DEPOSIT,
            ResponseSpecs.request_bad()
        ).post(account_deposit_request)
        return deposit_response

    # -------------------------------------------------------------- ПЕРЕВОД --
    @allure.step('Переводим между своими счетами — 200')
    def money_transfer_valid(self, create_user_request: CreateUserRequest,
                             money_transfer_request: MoneyTransferRequest):
        transfer_response = ValidateCrudRequester(
            RequestSpecs.auth_headers(create_user_request.username, create_user_request.password),
            Endpoint.MONEY_TRANSFER,
            ResponseSpecs.request_ok()
        ).post(money_transfer_request)
        return transfer_response

    @allure.step('Негатив: перевод больше баланса — 422')
    def money_transfer_invalid(self, create_user_request: CreateUserRequest,
                               money_transfer_request: MoneyTransferRequest):
        transfer_response = CrudRequester(
            RequestSpecs.auth_headers(create_user_request.username, create_user_request.password),
            Endpoint.MONEY_TRANSFER,
            ResponseSpecs.request_no_limit()
        ).post(money_transfer_request)
        return transfer_response

    @allure.step('Негатив: перевод нуля — 400')
    def money_transfer_invalid_zero(self, create_user_request: CreateUserRequest,
                                    money_transfer_request: MoneyTransferRequest):
        transfer_response = CrudRequester(
            RequestSpecs.auth_headers(create_user_request.username, create_user_request.password),
            Endpoint.MONEY_TRANSFER,
            ResponseSpecs.request_bad()
        ).post(money_transfer_request)
        return transfer_response

    # --------------------------------------------------------------- КРЕДИТ --
    @allure.step('Берём кредит — 201')
    def credit_user_valid(self, create_user_request: CreateUserRequest, account_credit_request: AccountCreditRequest):
        credit_response = ValidateCrudRequester(
            RequestSpecs.auth_headers(create_user_request.username, create_user_request.password),
            Endpoint.USER_CREDIT,
            ResponseSpecs.request_create()
        ).post(account_credit_request)
        return credit_response

    @allure.step('Читаем историю кредитов — 200')
    def get_credit(self, create_user_request: CreateUserRequest):
        credit_response = ValidateCrudRequester(
            RequestSpecs.auth_headers(create_user_request.username, create_user_request.password),
            Endpoint.CREDIT_HISTORY,
            ResponseSpecs.request_ok()
        ).get()
        return credit_response

    @allure.step('Негатив: кредит без роли ROLE_CREDIT_SECRET — 403')
    def credit_user_invalid(self, create_user_request: CreateUserRequest, account_credit_request: AccountCreditRequest):
        credit_response = CrudRequester(
            RequestSpecs.auth_headers(create_user_request.username, create_user_request.password),
            Endpoint.USER_CREDIT,
            ResponseSpecs.request_forbidden()
        ).post(account_credit_request)
        return credit_response

    @allure.step(
        'Негатив: сумма кредита вне лимита 5000–15000 — 400')
    # Swagger обещает 422 "Credit amount cannot exceed 15000", банк отдаёт 400 "Amount must be between 5000 and 15000"
    def credit_user_out_of_limit(self, create_user_request: CreateUserRequest,
                                 account_credit_request: AccountCreditRequest):
        credit_response = CrudRequester(
            RequestSpecs.auth_headers(create_user_request.username, create_user_request.password),
            Endpoint.USER_CREDIT,
            ResponseSpecs.request_bad()
        ).post(account_credit_request)
        return credit_response

    # ------------------------------------------------------------ ПОГАШЕНИЕ --
    @allure.step('Погашаем кредит — 200')
    def repay_credit_valid(self, create_user_request: CreateUserRequest, credit_repay_request: CreditRepayRequest):
        repay_response = ValidateCrudRequester(
            RequestSpecs.auth_headers(create_user_request.username, create_user_request.password),
            Endpoint.CREDIT_REPAY,
            ResponseSpecs.request_ok()
        ).post(credit_repay_request)
        return repay_response

    @allure.step('Негатив: сумма погашения не равна долгу — 422')
    def repay_credit_invalid(self, create_user_request: CreateUserRequest, credit_repay_request: CreditRepayRequest):
        repay_response = CrudRequester(
            RequestSpecs.auth_headers(create_user_request.username, create_user_request.password),
            Endpoint.CREDIT_REPAY,
            ResponseSpecs.request_no_limit()
        ).post(credit_repay_request)
        return repay_response

    @allure.step('Негатив: повторное погашение — 409')
    def credit_repay_conflict(self, create_user_request: CreateUserRequest,
                              credit_repay_request: CreditRepayRequest):
        transfer_response = CrudRequester(
            RequestSpecs.auth_headers(create_user_request.username, create_user_request.password),
            Endpoint.CREDIT_REPAY,
            ResponseSpecs.request_conflict()
        ).post(credit_repay_request)
        return transfer_response
