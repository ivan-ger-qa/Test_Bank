
from requests import Response

from src.main.api.foundation.http_requester import HttpRequester
from src.main.api.models.base_model import BaseModel


class CrudRequester(HttpRequester):
    def get(self, object_id: int | None=None) -> Response:
        return self._request('GET', path_suffix=object_id)

    def post(self, model: BaseModel | None = None) -> Response:
        return self._request('POST', model)

    def delete(self, user_id: int) -> Response:
        return self._request('DELETE', path_suffix=user_id)