from http import HTTPStatus

import requests

from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.request.requester import Requester


class CreateAccountRequester(Requester):
    def post(self, model=None):
        url = f'{self.base_url}/account/create'
        response = requests.post(
            url=url,
            headers=self.headers,
        )
        self.response_spec(response)
        if response.status_code == HTTPStatus.CREATED:
            return CreateAccountResponse(**response.json())
        raise response
