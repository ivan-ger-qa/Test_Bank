import requests

from src.main.api.configs.config import Config
from src.main.api.models.login_user_request import LoginUserRequest
from src.main.api.models.login_user_response import LoginUserResponse


class RequestSpecs:

    @staticmethod
    def base_headers() -> dict[str, str]:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    @staticmethod
    def auth_headers(username: str, password: str) -> dict[str, str]:
        request = LoginUserRequest(username=username, password=password)
        response = requests.post(
            url=f'{Config.fetch('backendUrl')}/auth/token/login',
            headers=RequestSpecs.base_headers(),
            json=request.model_dump()
        )
        if response.status_code == 200:
            response_data = LoginUserResponse(**response.json())
            token = response_data.token
            headers = RequestSpecs.base_headers()
            headers["Authorization"] = f"Bearer {token}"

            return headers
        raise Exception('Failed to login')

    @staticmethod
    def unauth_headers() -> dict[str, str]:
        return RequestSpecs.base_headers()
