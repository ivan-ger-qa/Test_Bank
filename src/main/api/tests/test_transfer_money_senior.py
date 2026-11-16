import pytest
from sqlalchemy.orm import Session

from src.main.api.generator.model_generator import RandomModelGenerator
from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.money_transfer_request import MoneyTransferRequest
from src.main.db.crud.account_crud import AccountCrudDb
from src.main.db.crud.transaction_crud import TransactionCrudDb

MAX_DEPOSIT = 9000.0  # максимальная сумма пополнения по требованиям проекта 9000


@pytest.mark.apis
class TestMoneyTransferSenior:
    def test_money_transfer(self, api_manager, create_user_request, db_session: Session):
        # --- Подготовка: пользователь, два счёта, деньги на счёте отправителя ---
        user = create_user_request()

        account_one = api_manager.user_steps.create_account(user)
        assert account_one.balance == 0, f'Начальный баланс счёта {account_one.balance}, а ожидали 0'

        account_two = api_manager.user_steps.create_account(user)
        assert account_two.balance == 0, f'Начальный баланс счёта {account_two.balance}, а ожидали 0'

        deposit_request = RandomModelGenerator.generate(AccountDepositRequest)
        deposit_request.accountId = account_one.id
        deposit = api_manager.user_steps.deposit_account(user, deposit_request)
        expected_deposit_balance = account_one.balance + deposit_request.amount
        assert deposit.balance == expected_deposit_balance, (f'В ответе API баланс {deposit.balance}, '
                                                             f'а ожидали {expected_deposit_balance}')

        transfer_request = MoneyTransferRequest(fromAccountId=account_one.id,
                                                toAccountId=account_two.id,
                                                amount=deposit.balance / 2)

        expected_sender_balance = deposit.balance - transfer_request.amount
        expected_receiver_balance = account_two.balance + transfer_request.amount

        # --- Действие: перевод ---
        transfer = api_manager.user_steps.money_transfer_valid(user, transfer_request)

        # --- Проверка: ответ API ---
        assert transfer.fromAccountIdBalance == expected_sender_balance, (f'В ответе API баланс отправителя '
                                                                          f'{transfer.fromAccountIdBalance}, '
                                                                          f'а ожидали {expected_sender_balance}')

        account_two_after = api_manager.user_steps.get_account(user, account_two.id)
        assert account_two_after.balance == expected_receiver_balance, (
            f'Баланс получателя {account_two_after.balance}, '
            f'а ожидали {expected_receiver_balance}')

        # --- Проверка: выписка по счёту ---
        account_one_after = api_manager.user_steps.get_account(user, account_one.id)
        transfers_out = [t for t in account_one_after.transactions if t.type == 'transfer_out']
        assert len(transfers_out) == 1, (f'Переводов out у отправителя {len(transfers_out)}, '
                                         f'а ожидали 1')
        assert transfers_out[0].amount == -transfer_request.amount, (f'Сумма перевода out у отправителя '
                                                                     f'{transfers_out[0].amount}, '
                                                                     f'а ожидали {-transfer_request.amount}')
        assert transfers_out[0].toAccountId == account_two.id, (f'Перевод ушёл на счёт {transfers_out[0].toAccountId}, '
                                                                f'а ожидали {account_two.id}')

        transfers_in = [d for d in account_two_after.transactions if d.type == 'transfer_in']
        assert len(transfers_in) == 1, (f'Переводов in у получателя {len(transfers_in)}, '
                                       f'а ожидали 1')
        assert transfers_in[0].amount == transfer_request.amount, (f'Сумма перевода in у получателя '
                                                                  f'{transfers_in[0].amount}, '
                                                                  f'а ожидали {transfer_request.amount}')
        assert transfers_in[0].fromAccountId == account_one.id, (f'Перевод пришел со счета {transfers_in[0].fromAccountId}, '
                                                              f'а ожидали {account_one.id}')

        # --- Проверка: база данных ---
        sender_from_db = AccountCrudDb.get_account_by_id(db_session, account_one.id)
        assert sender_from_db is not None, f'Счет {account_one.id} не найден в БД'

        receiver_from_db = AccountCrudDb.get_account_by_id(db_session, account_two.id)
        assert receiver_from_db is not None, f'Счет {account_two.id} не найден в БД'

        assert sender_from_db.balance == expected_sender_balance, (
            f'Баланс отправителя в БД {sender_from_db.balance}, ожидали {expected_sender_balance}'
        )
        assert receiver_from_db.balance == expected_receiver_balance, (
            f'Баланс получателя в БД {receiver_from_db.balance}, ожидали {expected_receiver_balance}'
        )

        transfer_from_db = TransactionCrudDb.get_transfer(db_session,
                                                          from_account_id=account_one.id,
                                                          to_account_id=account_two.id)
        assert transfer_from_db is not None, (
            f'Перевод со счёта {account_one.id} на счёт {account_two.id} не найден в БД'
        )
        assert transfer_from_db.amount == transfer_request.amount, (
            f'Сумма перевода в БД {transfer_from_db.amount}, ожидали {transfer_request.amount}'
        )

    @pytest.mark.parametrize('amount', [500.0, 501.0, 5000.0, 9999.0, 10000.0])
    def test_money_transfer_valid(self, api_manager, create_user_request, amount):
        # --- Подготовка: пользователь, два счёта, деньги на счёте отправителя ---
        user = create_user_request()

        account_one = api_manager.user_steps.create_account(user)
        assert account_one.balance == 0, f'Начальный баланс счёта {account_one.balance}, а ожидали 0'

        account_two = api_manager.user_steps.create_account(user)
        assert account_two.balance == 0, f'Начальный баланс счёта {account_two.balance}, а ожидали 0'

        deposit_request_first = AccountDepositRequest(accountId=account_one.id, amount=MAX_DEPOSIT)
        api_manager.user_steps.deposit_account(user, deposit_request_first)

        deposit_request_second = AccountDepositRequest(accountId=account_one.id, amount=MAX_DEPOSIT)
        deposit = api_manager.user_steps.deposit_account(user, deposit_request_second)

        transfer_request = MoneyTransferRequest(fromAccountId=account_one.id,
                                                toAccountId=account_two.id,
                                                amount=amount)

        expected_sender_balance = deposit.balance - transfer_request.amount
        expected_receiver_balance = account_two.balance + transfer_request.amount

        # --- Действие: перевод ---
        transfer = api_manager.user_steps.money_transfer_valid(user, transfer_request)

        # --- Проверка: ответ API ---
        assert transfer.fromAccountIdBalance == expected_sender_balance, (f'В ответе API баланс отправителя '
                                                                          f'{transfer.fromAccountIdBalance}, '
                                                                          f'а ожидали {expected_sender_balance}')

        account_two_after = api_manager.user_steps.get_account(user, account_two.id)
        assert account_two_after.balance == expected_receiver_balance, (
            f'Баланс получателя {account_two_after.balance}, '
            f'а ожидали {expected_receiver_balance}')

    def test_money_transfer_invalid_zero(self, api_manager, create_user_request):
        # --- Подготовка: пользователь, два счёта, деньги на счёте отправителя ---
        user = create_user_request()

        account_one = api_manager.user_steps.create_account(user)

        account_two = api_manager.user_steps.create_account(user)

        deposit_request = RandomModelGenerator.generate(AccountDepositRequest)
        deposit_request.accountId = account_one.id
        deposit = api_manager.user_steps.deposit_account(user, deposit_request)

        transfer_request = MoneyTransferRequest(fromAccountId=account_one.id,
                                                toAccountId=account_two.id,
                                                amount=0)

        # --- Действие: перевод нуля ---
        transfer = api_manager.user_steps.money_transfer_invalid_zero(user, transfer_request)

        # --- Проверка: ответ API ---
        assert 'Amount must be greater than 0' in transfer.text, (f'Ожидали текст "Amount must be greater than 0", '
                                                                  f'а получили {transfer.text}')

        account_one_after = api_manager.user_steps.get_account(user, account_one.id)
        assert account_one_after.balance == deposit.balance, (f'Баланс отправителя {account_one_after.balance}, '
                                                              f'а ожидали {deposit.balance}')

        account_two_after = api_manager.user_steps.get_account(user, account_two.id)
        assert account_two_after.balance == account_two.balance, (f'Баланс получателя {account_two_after.balance}, '
                                                                  f'а ожидали {account_two.balance}')

    @pytest.mark.parametrize('amount', [250.0, 499.0, 10001.0, 15000.0])
    def test_money_transfer_invalid(self, api_manager, create_user_request, amount, db_session):
        # --- Подготовка: пользователь, два счёта, деньги на счёте отправителя ---
        user = create_user_request()

        account_one = api_manager.user_steps.create_account(user)
        assert account_one.balance == 0, f'Начальный баланс счёта {account_one.balance}, а ожидали 0'

        account_two = api_manager.user_steps.create_account(user)
        assert account_two.balance == 0, f'Начальный баланс счёта {account_two.balance}, а ожидали 0'

        deposit_request_first = AccountDepositRequest(accountId=account_one.id, amount=MAX_DEPOSIT)
        api_manager.user_steps.deposit_account(user, deposit_request_first)

        deposit_request_second = AccountDepositRequest(accountId=account_one.id, amount=MAX_DEPOSIT)
        deposit_second = api_manager.user_steps.deposit_account(user, deposit_request_second)

        transfer_request = MoneyTransferRequest(fromAccountId=account_one.id,
                                                toAccountId=account_two.id,
                                                amount=amount)

        sender_balance_before_db = AccountCrudDb.get_account_by_id(db_session, account_one.id).balance
        receiver_balance_before_db = AccountCrudDb.get_account_by_id(db_session, account_two.id).balance

        # --- Действие: перевод суммой вне лимита ---
        transfer = api_manager.user_steps.money_transfer_invalid_zero(user, transfer_request)

        # --- Проверка: ответ API ---
        assert 'Amount must be between 500 and 10000' in transfer.text, (
            f'Ожидали текст "Amount must be between 500 and 10000", '
            f'а получили {transfer.text}')

        first_after = api_manager.user_steps.get_account(user, account_one.id)
        assert first_after.balance == deposit_second.balance, (f'Баланс отправителя {first_after.balance}, '
                                                               f'а ожидали {deposit_second.balance}')

        second_after = api_manager.user_steps.get_account(user, account_two.id)
        assert second_after.balance == account_two.balance, (f'Баланс получателя {second_after.balance}, '
                                                             f'а ожидали {account_two.balance}')

        # --- Проверка: база данных ---
        db_session.expunge_all()
        sender_from_db = AccountCrudDb.get_account_by_id(db_session, account_one.id)
        assert sender_from_db is not None, f'Счет отправителя {account_one.id} не найден'
        assert sender_balance_before_db == sender_from_db.balance, (f'Баланс отправителя в БД до перевода '
                                                                    f'{sender_balance_before_db}, а после '
                                                                    f'{sender_from_db.balance}')

        receiver_from_db = AccountCrudDb.get_account_by_id(db_session, account_two.id)
        assert receiver_from_db is not None, f'Счет получателя {account_two.id} не найден'
        assert receiver_from_db.balance == receiver_balance_before_db, (f'Баланс получателя в БД до перевода '
                                                                        f'{receiver_balance_before_db}, а после '
                                                                        f'{receiver_from_db.balance}')

        transfer_from_db = TransactionCrudDb.get_transfer(db_session, account_one.id, account_two.id)
        assert transfer_from_db is None, (f'Отклоненный перевод {transfer_request.amount} '
                                          f'со счета {account_one.id} на счет {account_two.id} '
                                          f'появился в БД')
