from core.database import DBModelBase
from sqlalchemy import Integer, BIGINT, String
from sqlalchemy.orm import Mapped,mapped_column

class Session(DBModelBase):
    __tablename__ = 't_session'
    user_id: Mapped[int] = mapped_column(BIGINT, nullable=False, comment="用户id")
    session_name: Mapped[str] = mapped_column(String(63), default='', comment="会话名称")
    is_del: Mapped[int] = mapped_column(Integer, default=0, comment="是否删除 1-是 0：否")