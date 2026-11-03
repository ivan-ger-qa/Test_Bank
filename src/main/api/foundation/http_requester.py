from typing import Callable

from requests import Response

from src.main.api.configs.config import Config
from src.main.api.foundation.endpoint import Endpoint


class HttpRequester:
    def __init__(self, request_spec: dict[str, str], endpoint: Endpoint, response_spec: Callable[[Response], None]):
        self.request_spec = request_spec
        self.endpoint = endpoint
        self.response_spec = response_spec

    def request(self, endpoint, model=None):
        url = f'{Config.fetch('backendUrl')}{endpoint.value.url}'
        body = None if endpoint.value.request_model is None else model.model_dump()
        ...
