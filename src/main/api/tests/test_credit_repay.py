import requests
import pytest
import random


def generate_username():
    return f'ivan{random.randint(0, 9999999)}'


class TestCreditRepay:
    def test_credit_repay_valid(self):
        username = generate_username()

        auth_admin_response = requests.post(
            url='http://localhost:4111/api/auth/token/login',
            json={
                'username':  'admin',
                'password': '123456'
            },
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )
        assert auth_admin_response.status_code == 200
        admin_token = auth_admin_response.json().get('token')

        create_user_response = requests.post(
            url= 'http://localhost:4111/api/admin/create',
            json={
                'username': username,
                'password': 'Pas!sw0rd',
                'role': 'ROLE_CREDIT_SECRET'
            },
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {admin_token}'
            }
        )
        assert create_user_response.status_code == 200

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
        user_token = auth_user_response.json().get('token')

        create_user_acount_response = requests.post(
            url='http://localhost:4111/api/account/create',
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {user_token}'
            }
        )
        assert create_user_acount_response.status_code == 201
        id_user = create_user_acount_response.json().get('id')

        create_user_credit_response = requests.post(
            url= 'http://localhost:4111/api/credit/request',
            json={
                'accountId': id_user,
                'amount': 10000,
                'termMonths': 12
            },
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {user_token}'
            }
        )
        assert create_user_credit_response.status_code == 201
        id_credit = create_user_credit_response.json().get('creditId')


        create_creit_repay_response = requests.post(
            url= 'http://localhost:4111/api/credit/repay',
            json={
                'creditId': id_credit,
                'accountId': id_user,
                'amount': 10000
            },
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {user_token}'
            }
        )
        assert create_creit_repay_response.status_code == 200

    def test_credit_repay_invalid(self):
        username = generate_username()

        auth_admin_response = requests.post(
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
        assert auth_admin_response.status_code == 200
        admin_token = auth_admin_response.json().get('token')

        create_user_response = requests.post(
            url='http://localhost:4111/api/admin/create',
            json={
                'username': username,
                'password': 'Pas!sw0rd',
                'role': 'ROLE_CREDIT_SECRET'
            },
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {admin_token}'
            }
        )
        assert create_user_response.status_code == 200

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
        user_token = auth_user_response.json().get('token')

        create_user_acount_response = requests.post(
            url='http://localhost:4111/api/account/create',
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {user_token}'
            }
        )
        assert create_user_acount_response.status_code == 201
        id_user = create_user_acount_response.json().get('id')

        create_user_credit_response = requests.post(
            url='http://localhost:4111/api/credit/request',
            json={
                'accountId': id_user,
                'amount': 10000,
                'termMonths': 12
            },
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {user_token}'
            }
        )
        assert create_user_credit_response.status_code == 201
        id_credit = create_user_credit_response.json().get('creditId')

        create_creit_repay_response = requests.post(
            url='http://localhost:4111/api/credit/repay',
            json={
                'creditId': id_credit,
                'accountId': id_user,
                'amount': 12000
            },
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {user_token}'
            }
        )
        assert create_creit_repay_response.status_code == 422
