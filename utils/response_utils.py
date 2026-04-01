from typing import Any, Optional
from fastapi import status
from pydantic import BaseModel


class ResponseUtils(BaseModel):
    code: int
    msg: str
    data: Optional[Any] = None
    success: bool
    headers: dict = dict()

    # 成功返回
    @classmethod
    def success_rsp(cls, data: Any = None, msg: str = ""):
        return cls(
            code=status.HTTP_200_OK,
            msg=msg,
            data=data,
            success=True
        )

    # 失败返回
    @classmethod
    def error(cls, msg: str = "error", code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        return cls(
            code=code,
            msg=msg,
            data=None,
            success=False
        )