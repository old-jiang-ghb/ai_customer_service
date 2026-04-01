from fastapi import APIRouter, Depends, HTTPException,Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from service.user_service import UserService
from schemas.user_schemas import UserResponse, UserCreateOrUpdate, UserLogin, UserBaseResponse
from utils.jwt_utils import create_token
from utils.password_hash_utils import verify_password
from utils.response_utils import ResponseUtils
from core.database import get_db
from starlette import status
from utils.logger_utils import log
from utils.user_utils import get_real_ip
# 创建分路由
router = APIRouter(prefix="/user")

@router.post('/register', description='创建用户', summary='用户注册')
def create(obj_in: UserCreateOrUpdate, request: Request, session: Session = Depends(get_db)):
    ip = get_real_ip(request)
    obj_in.last_login_ip = ip
    return ResponseUtils.success_rsp(data=UserBaseResponse.model_validate(UserService.create_user(session, obj_in)))


@router.get('/{pk}', description='根据主键查询用户信息')
def get(pk:int, session: Session = Depends(get_db)):
    return ResponseUtils.success_rsp(data=UserBaseResponse.model_validate(UserService.get_user(session, pk)))

@router.post('/login', description='用户登录', summary='用户登录')
def login(obj_in: UserLogin, session: Session = Depends(get_db)):
    # 实现用户登录，成功之后返回用户信息，包括token
    # 第一步：根据用户名去查询用户
    user, token = UserService.login(session, obj_in.username, obj_in.password)
    user.token = token
    result = UserResponse.model_validate(user)
    # 代码执行到此，则登录成功
    return ResponseUtils.success_rsp(data=result)

@router.post('/auth', description='接口文档中认证表单提交')
def auth(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_db)):
    """
    接口文档中，用于接受认证表单提交的视图函数
    :param form_data: 表单数据
    :param session:
    :return:
    """
    user = UserService.get_user_by_username(session, form_data.username)
    log.info(user)
    if not user:  # 用户不存在
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'用户名{form_data.username}，在数据库表中不存在!'
        )
    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'登录密码错误'
        )
    # 代码执行到此，则登录成功
    return {'access_token': create_token(str(user.id) + ':' + user.username),  # 创建token
        'token_type': 'bearer'}