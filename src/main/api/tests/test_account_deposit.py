import pytest
import requests


class TestAccountDeposit:
    def test_account_deposit_valid(self):
        create_admit_response = requests.post(
            url= 'http://localhost:4111/api/auth/token/login',
            json = {
                'username': 'admin',
                'password': '123456'
            },
            headers = {
                'content-type': 'application/json',
                'accept': 'application/json'
            }
        )
        token = create_admit_response.json().get('token')
        assert create_admit_response.status_code == 200

        create_user_response = requests.post(
            url= 'http://localhost:4111/api/admin/create',
            json = {
                'username': 'ivangg23',
                'password': 'Pas!sw0rd',
                'role': 'ROLE_USER'
            },
            headers = {
                'content-type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )
        assert create_user_response.status_code == 200

        auth_user_response = requests.post(
            url= 'http://localhost:4111/api/auth/token/login',
            json = {
                'username': 'ivangg23',
                'password': 'Pas!sw0rd'
            },
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
        create_admit_response = requests.post(
            url='http://localhost:4111/api/auth/token/login',
            json={
                'username': 'admin',
                'password': '123456'
            },
            headers={
                'content-type': 'application/json',
                'accept': 'application/json'
            }
        )
        token = create_admit_response.json().get('token')
        assert create_admit_response.status_code == 200

        create_user_response = requests.post(
            url='http://localhost:4111/api/admin/create',
            json={
                'username': 'ivangg21',
                'password': 'Pas!sw0rd',
                'role': 'ROLE_USER'
            },
            headers={
                'content-type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )
        assert create_user_response.status_code == 200

        auth_user_response = requests.post(
            url='http://localhost:4111/api/auth/token/login',
            json={
                'username': 'ivangg21',
                'password': 'Pas!sw0rd'
            },
            headers={
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

