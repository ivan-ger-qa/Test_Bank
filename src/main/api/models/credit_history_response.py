
from src.main.api.models.base_model import BaseModel
from src.main.api.models.credit_response import CreditResponse


class CreditHistoryResponse(BaseModel):
    userId: int
    credits: list[CreditResponse]
