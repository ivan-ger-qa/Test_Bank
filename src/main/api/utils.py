from src.main.api.models.credit_response import CreditResponse
from src.main.api.models.transaction_response import TransactionResponse


def find_transaction_by_type(transactions: list[TransactionResponse],
                             transaction_type: str) -> list[TransactionResponse]:
    return [t for t in transactions if t.type == transaction_type]


def find_credit_by_id(credits: list[CreditResponse],
                      credit_id: int) -> list[CreditResponse]:
    return [c for c in credits if c.creditId == credit_id]
