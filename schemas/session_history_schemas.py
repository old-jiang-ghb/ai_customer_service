from typing import Union

from pydantic import Field, BaseModel


class BaseSessionHistory(BaseModel):
    session_id: int = Field(description='会话id')
    detail: Union[str, None] = Field(description='聊天详细', default='')
    history_type: int = Field(description='记录类型 1-用户问题 2-ai客服回复', default=1)

class SessionHistoryResponse(BaseSessionHistory):
    id: int = Field(description='会话id')
    # 让 Pydantic 兼容 ORM 对象
    class Config:
        from_attributes = True