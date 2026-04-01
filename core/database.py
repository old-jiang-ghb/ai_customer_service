from sqlalchemy import create_engine,DateTime, func
from sqlalchemy.orm import sessionmaker, DeclarativeBase, declared_attr ,Mapped ,mapped_column
from sqlalchemy import URL
from core import settings
from datetime import datetime

url = URL(
    drivername= settings.DATABASE.DRIVER,
    username= settings.DATABASE.USERNAME,
    password= settings.DATABASE.PASSWORD,
    host= settings.DATABASE.HOST,
    port= settings.DATABASE.PORT,
    database= settings.DATABASE.NAME,
    query= settings.DATABASE.get('QUERY', None),
)

engine = create_engine(
    url,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=10,
    max_overflow=20
)

# 2. 创建会话工厂（每次请求一个Session）
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 3. 模型基类（所有Model都继承它）
class DBModelBase(DeclarativeBase):
    """ 定义一系列的可以映射的公共属性，此类是所有数据库模型类的父类"""

    __table_args__ = {"mysql_engine": "InnoDB"}
    #  如果为true，则ORM将在插入或更新之后立即获取服务器生成的默认值的值
    __mapper_args__ = {"eager_defaults": True}

    # 所有的模型类，都有的属性和字段映射
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    create_time: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now(), comment='创建时间')
    update_time: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now(), onupdate=func.now(),
                                                  comment='记录的最后一次修改时间')

# 4. 依赖注入：获取数据库会话（FastAPI 标准）
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()