from sqlalchemy import BIGINT, String, Integer

from core.database import DBModelBase
from sqlalchemy.orm import  Mapped, mapped_column

class FileUploadRecord(DBModelBase):
    __tablename__ = "t_file_upload_record"
    user_id: Mapped[int] = mapped_column(BIGINT, nullable=False, comment="用户id")
    file_name: Mapped[str] = mapped_column(String(128), comment="原始文件名称")
    local_file_name: Mapped[str] = mapped_column(String(128), comment="本地文件名称")
    local_file_path: Mapped[str] = mapped_column(String(128), comment="本地文件路径")
    is_del: Mapped[int] = mapped_column(Integer, default=0, comment="是否删除 1-是 0：否")
    state: Mapped[int] = mapped_column(Integer, default=2, comment="文件状态 1-已加载 2-加载失败")