from typing import Union

from constants.error_constants import ErrorConstants

# 业务异常
class BusinessException(Exception):
    code: int = 500
    msg: str = ErrorConstants.common_error

    def __init__(self, msg: Union[str, None], code: int=500):
        if msg:
            self.msg = msg
        if code:
            self.code = code