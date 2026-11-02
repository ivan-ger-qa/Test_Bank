from src.main.api.models.base_model import BaseModel


class AccountCreditRequest(BaseModel):
    accountId: int
    amount:float
    termMonths:int

