import random

import pytest
import requests


def generate_username():
    return f'ivangg{random.randint(1, 99999)}'


@pytest.mark.api
class TestUserCredit:
    def test_user_credit_valid(self):
        username = generate_username()

        auth_admin_request = requests.post(
            url='http://localhost:4111/api/auth/token/login',
            json={
                'username': 'admin',
                'password': '123456'
            },
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )
        assert auth_admin_request.status_code == 200
        token = auth_admin_request.json().get('token')

        create_account_user_response = requests.post(
            url='http://localhost:4111/api/admin/create',
            json={
                'username': username,
                'password': 'Pas!sw0rd',
                'role': 'ROLE_CREDIT_SECRET'
            },
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )
        assert create_account_user_response.status_code == 200

        auth_user_response = requests.post(
            url='http://localhost:4111/api/auth/token/login',
            json={
                'username': username,
                'password': 'Pas!sw0rd'
            },
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )

        assert auth_user_response.status_code == 200
        token = auth_user_response.json().get('token')

        create_banc_account_user_response = requests.post(
            url='http://localhost:4111/api/account/create',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )
        # print(create_banc_account_user_response.json())
        assert create_banc_account_user_response.status_code == 201
        id_account = create_banc_account_user_response.json().get('id')

        create_credit_user_response = requests.post(
            url='http://localhost:4111/api/credit/request',
            json={
                'accountId': id_account,
                'amount': 5000.0,
                'termMonths': 12
            },
            headers={
                'Content-Type': 'application/json',
                'accept': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )
        assert create_credit_user_response.status_code == 201
        assert create_credit_user_response.json().get('balance') == 5000.0

    def test_user_credit_invalid(self):
        username = generate_username()
        auth_admin_response = requests.post(
            url='http://localhost:4111/api/auth/token/login',
            json={
                'username': "admin",
                'password': "123456"
            },
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )
        assert auth_admin_response.status_code == 200
        token = auth_admin_response.json().get('token')

        create_account_user_response = requests.post(
            url='http://localhost:4111/api/admin/create',
            json={
                'username': username,
                'password': "Pas!sw0rd",
                'role': 'ROLE_USER'
            },
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )
        assert create_account_user_response.status_code == 200

        auth_user_response = requests.post(
            url='http://localhost:4111/api/auth/token/login',
            json={
                'username': username,
                'password': "Pas!sw0rd"
            },
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )
        assert auth_user_response.status_code == 200
        token = auth_user_response.json().get('token')


        create_banc_account_user_response = requests.post(
            url='http://localhost:4111/api/account/create',
           headers={
               'Content-Type': 'application/json',
               'Authorization': f'Bearer {token}'
            }
        )
        assert create_banc_account_user_response.status_code == 201
        id_account = create_banc_account_user_response.json().get('id')

        create_credit_user_response = requests.post(
            url='http://localhost:4111/api/credit/request',
            json={
                'accountId': id_account,
                'amount': 5000.0,
                'termMonths': 12
            },
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'authorization': f'Bearer {token}'
            }
        )

        assert create_credit_user_response.status_code == 403
