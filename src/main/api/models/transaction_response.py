
from src.main.api.models.base_model import BaseModel


class TransactionResponse(BaseModel):
    transactionId: int
    type: str
    amount: float
    fromAccountId: int | None = None
    toAccountId: int | None = None
    createdAt: str
    creditId: int | None = None
