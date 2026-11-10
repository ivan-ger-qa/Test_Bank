from typing import Protocol

from requests import Response

from src.main.api.models.base_model import BaseModel


class CrudEndpoint(Protocol):
    def post(self, model: BaseModel | None) -> BaseModel | Response: ...

    def get(self, object_id: int) -> BaseModel | Response: ...

    def delete(self, user_id: int) -> BaseModel | Response: ...
