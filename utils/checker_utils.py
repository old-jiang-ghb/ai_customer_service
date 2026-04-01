from typing import Any
from constants.error_constants import ErrorConstants
from core.exception import BusinessException


#校验器
class Checker:
    @staticmethod
    def is_null(obj: Any, err_msg: str = ErrorConstants.common_error):
        if obj is None:
            raise BusinessException(err_msg)

    @staticmethod
    def is_true(obj: bool, err_msg: str = ErrorConstants.common_error):
        if obj:
            raise BusinessException(err_msg)