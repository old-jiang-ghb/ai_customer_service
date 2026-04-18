from sqlalchemy.orm import Session

from core.exception import BusinessException
from dao.user_dao import UserDao
from schemas.user_schemas import UserCreateOrUpdate
from models.user import User
from utils.password_hash_utils import get_hashed_password, verify_password
from utils.jwt_utils import create_token
from utils.checker_utils import Checker
from cache.redis_cache import RedisCache

class UserService:
    @staticmethod
    def get_user(db: Session, user_id: int):
        return UserDao.get_user_by_id(db, user_id)

    @staticmethod
    def get_user_by_username(db: Session, username: str):
        Checker.is_null(username,'用户名不能为空')
        return UserDao.get_user_by_username(db, username)

    @staticmethod
    def create_user(db: Session, user_in: UserCreateOrUpdate):
        user = UserDao.get_user_by_username(db, user_in.username)
        if user : raise BusinessException(msg= "用户名已存在")
        # 密码加密
        hashed_pwd = get_hashed_password(user_in.password)
        user = User(
            username=user_in.username,
            password=hashed_pwd,
            mail =user_in.email,
            tel= user_in.tel,
            desc = user_in.desc,
            real_name = user_in.real_name,
            last_login_ip = user_in.last_login_ip,
            user_type= user_in.user_type
        )
        return UserDao.create_user(db, user)

    @staticmethod
    def login(session, username, password):
        Checker.is_null(username, '用户名不能为空')
        Checker.is_null(password, '密码不能为空')
        user = UserDao.get_user_by_username(session, username)
        if not user:  # 用户不存在
            raise BusinessException(msg=f'用户:{username}未注册')
        if not verify_password(password, user.password):
            raise BusinessException(msg=f'登录密码错误')
        token = create_token(str(user.id) + ':' + user.username)
        # 将用户信息保存到redis中
        RedisCache.set(token, str(user.id) + ':' + user.username)
        return user, token




