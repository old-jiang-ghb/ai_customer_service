from pydantic import BaseModel,Field
from typing import Union
from schemas import BasePaging


class BaseSession(BaseModel):
    user_id: int = Field(description='用户id')
    session_name: Union[str, None] = Field(description='会话名称', default='')

class SessionCreateOrUpdate(BaseSession):
    is_del: int = Field(description="是否删除", default=0)

class SessionResponse(BaseSession):
    id: int = Field(description='会话id')
    # 让 Pydantic 兼容 ORM 对象
    class Config:
        from_attributes = True