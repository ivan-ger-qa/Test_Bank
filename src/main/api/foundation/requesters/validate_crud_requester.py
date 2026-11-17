from collections.abc import Callable

import allure
from requests import Response

from src.main.api.foundation.endpoint import Endpoint
from src.main.api.foundation.http_requester import HttpRequester
from src.main.api.foundation.requesters.crud_requester import CrudRequester
from src.main.api.models.base_model import BaseModel


class ValidateCrudRequester(HttpRequester):
    def __init__(self, request_spec: dict[str, str], endpoint: Endpoint,
                 response_spec: Callable[Response, None]) -> None:
        super().__init__(request_spec, endpoint, response_spec)
        self.crud_requester = CrudRequester(
            request_spec=request_spec,
            endpoint=endpoint,
            response_spec=response_spec
        )

    def post(self, model: BaseModel | None = None) -> BaseModel:
        response = self.crud_requester.post(model)
        with allure.step(f'ValidateModelResponse: {self.endpoint.value.response_model.__name__}'):
            return self.endpoint.value.response_model.model_validate(response.json())

    def get(self, object_id: int | None = None) -> BaseModel:
        response = self.crud_requester.get(object_id)
        with allure.step(f'ValidateModelResponse: {self.endpoint.value.response_model.__name__}'):
            return self.endpoint.value.response_model.model_validate(response.json())
