from typing import Any

from src.main.api.specs.request_specs import RequestSpecs


class BaseSteps:
    def __init__(self, created_obj: list[Any]):
        self.created_obj= created_obj
        self.admin_headers = RequestSpecs.auth_headers('admin', '123456')