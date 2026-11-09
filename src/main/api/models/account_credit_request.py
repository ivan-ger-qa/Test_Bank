from typing import Annotated

from src.main.api.generator.creation_rule import CreationRule
from src.main.api.models.base_model import BaseModel


class AccountCreditRequest(BaseModel):
    accountId: int
    amount:Annotated[float, CreationRule(regex=r'^([5-9][0-9]{3}|1[0-4][0-9]{3})$')]
    termMonths:Annotated[int, CreationRule(regex=r'^[1-5][0-9]$')]   #В требованиях нет срока кредита, нашел в свагере от 1 до 60

