import pytest
import requests
import random

from src.main.api.models.create_user_response import CreateUserResponse
from src.main.api.models.login_user_request import LoginUserRequest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.login_user_response import LoginUserResponse

def generate_name():
    return f'ivangg{random.randint(1, 909999)}'


class TestAccountDeposit:
    def test_account_deposit_valid(self):
        username = generate_name()

        login_user_request = LoginUserRequest(username='admin', password='123456')

        create_admit_response = requests.post(
            url= 'http://localhost:4111/api/auth/token/login',
            json = login_user_request.model_dump(),
            headers = {
                'content-type': 'application/json',
                'accept': 'application/json'
            }
        )
        token = create_admit_response.json().get('token')
        assert create_admit_response.status_code == 200
        login_user_response = LoginUserResponse(**create_admit_response.json())
        assert login_user_request.username == login_user_response.user.username
        assert login_user_response.user.role == 'ROLE_ADMIN'


        create_user_request = CreateUserRequest(username=username, password='Pas!sw0rd',role='ROLE_USER')

        response = requests.post(
            url= 'http://localhost:4111/api/admin/create',
            json = create_user_request.model_dump(),
            headers = {
                'content-type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )
        assert response.status_code == 200
        create_user_response = CreateUserResponse(**response.json())
        assert create_user_request.username == create_user_response.username
        assert create_user_request.role == create_user_response.role


        login_user_request = LoginUserRequest(username=username, password='Pas!sw0rd')
        auth_user_response = requests.post(
            url= 'http://localhost:4111/api/auth/token/login',
            json = login_user_request.model_dump(),
            headers = {
                'content-type': 'application/json',
                'accept': 'application/json'
            }
        )
        assert auth_user_response.status_code == 200
        token = auth_user_response.json().get('token')

        create_account_user_response = requests.post(
            url= 'http://localhost:4111/api/account/create',
            headers = {
                'content-type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )

        id_account = create_account_user_response.json().get('id')

        assert create_account_user_response.status_code == 201
        assert create_account_user_response.json().get('balance') == 0

        user_account_deposit_response = requests.post(
            url= 'http://localhost:4111/api/account/deposit',
            json = {
                'accountId': id_account,
                'amount': 1000.0
            },
            headers = {
                'content-type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )
        assert user_account_deposit_response.status_code == 200
        assert user_account_deposit_response.json().get('balance') == 1000



    def test_account_deposit_invalid(self):
        username = generate_name()

        login_user_request = LoginUserRequest(username='admin', password='123456')

        create_admit_response = requests.post(
            url= 'http://localhost:4111/api/auth/token/login',
            json = login_user_request.model_dump(),
            headers = {
                'content-type': 'application/json',
                'accept': 'application/json'
            }
        )
        token = create_admit_response.json().get('token')
        assert create_admit_response.status_code == 200

        create_user_request = CreateUserRequest(username=username, password='Pas!sw0rd',role='ROLE_USER')

        response = requests.post(
            url= 'http://localhost:4111/api/admin/create',
            json = create_user_request.model_dump(),
            headers = {
                'content-type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )
        assert response.status_code == 200
        create_user_response = CreateUserResponse(**response.json())
        assert create_user_request.username == create_user_response.username
        assert create_user_request.role == create_user_response.role


        login_user_request = LoginUserRequest(username=username, password='Pas!sw0rd')
        auth_user_response = requests.post(
            url= 'http://localhost:4111/api/auth/token/login',
            json = login_user_request.model_dump(),
            headers = {
                'content-type': 'application/json',
                'accept': 'application/json'
            }
        )
        assert auth_user_response.status_code == 200
        token = auth_user_response.json().get('token')

        create_account_user_response = requests.post(
            url='http://localhost:4111/api/account/create',
            headers={
                'content-type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )

        id_account = create_account_user_response.json().get('id')

        assert create_account_user_response.status_code == 201
        assert create_account_user_response.json().get('balance') == 0

        user_account_deposit_response = requests.post(
            url='http://localhost:4111/api/account/deposit',
            json={
                'accountId': id_account,
                'amount': 10000.0
            },
            headers={
                'content-type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )
        assert user_account_deposit_response.status_code == 400

