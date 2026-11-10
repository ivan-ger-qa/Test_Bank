from typing import Annotated

from src.main.api.generator.creation_rule import CreationRule
from src.main.api.models.base_model import BaseModel


class CreditRepayRequest(BaseModel):
    creditId: int
    accountId: int
    amount:float