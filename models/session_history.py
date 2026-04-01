from sqlalchemy.dialects.mysql import LONGTEXT

from core.database import DBModelBase
from sqlalchemy import Integer, BIGINT
from sqlalchemy.orm import Mapped,mapped_column

USER_HISTORY_TYPE = 1
AI_HISTORY_TYPE = 2

class SessionHistory(DBModelBase):
    __tablename__ = 't_session_history'
    session_id: Mapped[int] = mapped_column(BIGINT, nullable=False, comment="会话id")
    detail: Mapped[str] = mapped_column(LONGTEXT, nullable=True, comment="聊天详细")
    history_type: Mapped[int] = mapped_column(Integer, nullable=False, default= 1, comment="1-用户问题 2-ai客服回复")
    is_del: Mapped[int] = mapped_column(Integer, default=0, comment="是否删除 1-是 0：否")