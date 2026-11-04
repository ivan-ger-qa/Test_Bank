from dataclasses import dataclass
from enum import Enum
from typing import Optional, Type

from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.account_deposit_response import AccountDepositResponse
from src.main.api.models.base_model import BaseModel
from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.create_user_response import CreateUserResponse


@dataclass
class EndpointConfiguration:
    url: str
    request_model:Optional[Type[BaseModel]] = None
    response_model:Optional[Type[BaseModel]] = None


class Endpoint(Enum):
    ADMIN_CREATE_USER = EndpointConfiguration(
        url='/admin/create',
        request_model=CreateUserRequest,
        response_model=CreateUserResponse
    )

    ADMIN_DELETE_USER = EndpointConfiguration(
        url='/admin/users'
    )

    CREATE_USER_ACCOUNT = EndpointConfiguration(
        url='/account/create',
        response_model=CreateAccountResponse
    )

    ACCOUNT_DEPOSIT = EndpointConfiguration(
        url='/account/deposit',
        request_model=AccountDepositRequest,
        response_model=AccountDepositResponse
    )


