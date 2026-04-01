from sqlalchemy import String, Integer, BIGINT
from sqlalchemy.orm import Mapped,mapped_column
from core.database import DBModelBase


class User(DBModelBase):
    __tablename__ = 't_user'
    username : Mapped[str] = mapped_column(String(63), nullable=False, default='', comment="用户名称")
    real_name: Mapped[str] = mapped_column(String(63), default='ai小智', comment="用户真实名称")
    password: Mapped[str] = mapped_column(String(63), nullable=False, default='', comment="用户密码")
    last_login_ip: Mapped[str] = mapped_column(String(63), nullable=True, default='', comment="最后一次登录IP地址")
    desc: Mapped[str] = mapped_column(String(1024), nullable=True, comment="用户描述")
    tel: Mapped[str] = mapped_column(String(16), nullable=True, comment="联系电话")
    mail: Mapped[str] = mapped_column(String(64), nullable=True, comment="邮箱地址")
    user_type: Mapped[int] = mapped_column(Integer, default= 1, comment="用户类型：1.普通 2.管理员")
    is_del: Mapped[int] = mapped_column(Integer, default=0, comment="是否删除 1-是 0：否")
