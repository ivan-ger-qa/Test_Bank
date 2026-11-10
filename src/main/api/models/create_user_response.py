from src.main.api.models.base_model import BaseModel


class CreateUserResponse(BaseModel):
    # В Swagger поле называется accountId, а API на самом деле возвращает id —
    # расхождение документации и реального ответа. Модель сделана по факту.
    id: int
    username: str
    password: str
    role: str
