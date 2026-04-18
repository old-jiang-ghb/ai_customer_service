import re
import traceback
from datetime import datetime
from typing import Callable
from fastapi import FastAPI
from fastapi.requests import Request
from jose import jwt, ExpiredSignatureError
from starlette import status
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
import uuid
from utils.response_utils import ResponseUtils
from core import settings
from utils.logger_utils import log
from utils.user_utils import get_real_ip
from cache.rate_limit import RateLimiter
from cache.redis_cache import RedisCache
from utils.context_utils import trace_id_ctx

async def add_trace_id(request: Request, call_next: Callable) -> JSONResponse:
    # 1. 生成 trace_id
    trace_id = str(uuid.uuid4())

    # 2. 存入上下文（全局任何地方都能取！）
    trace_id_ctx.set(trace_id)

    # 3. 执行请求
    response = await call_next(request)

    # 4. 响应头带回
    response.headers["X-Trace-ID"] = trace_id
    return response

async def verify_token(request: Request, call_next: Callable) -> JSONResponse:
    # OAuth2的规范，如果认证失败，请求头中返回“WWW-Authenticate”
    auth_error = JSONResponse(content=ResponseUtils(code=status.HTTP_401_UNAUTHORIZED, msg="'非法的指令牌Token，请重新登录！", headers={"WWW-Authenticate": "JWT"},
                                                    success=True).model_dump(), status_code=200)
    limit_error = JSONResponse(content=ResponseUtils(code=status.HTTP_429_TOO_MANY_REQUESTS, msg="请求频率过高，请稍后重试", success=False).model_dump()
                               , status_code=status.HTTP_429_TOO_MANY_REQUESTS)
    # token校验的中间件

    # 是不是所有api接口都需要token验证？ 有很多是不需要的
    # 不需要的可以把它们保存到一个白名单里面。

    # 得到请求路径
    path: str = request.get('path')
    # 从白名单中匹配请求路径
    for request_path in settings.WHITE_LIST:
        if re.match(request_path, path):
            return await call_next(request)  # 继续往下执行
    else:  # 请求路径不是白名单里面的
        # 从请求的header中读取token
        # curl -X GET "http://localhost:8000/api/test" -H "Authorization: Bearer {token}"
        authorization: str = request.headers.get('Authorization')
        if not authorization:
            return auth_error
        token: str = authorization.split(' ')[1]
        try:
            # 校验token
            res_dict = RedisCache.get(token)
            # 如果没有查到则返回错误
            if not res_dict:
                return auth_error
            sub = res_dict.get('sub').split(':')
            user_id = sub[0]
            username = sub[1]
            # 限流ip，防止攻击 1分钟100次
            if not RateLimiter.is_allowed(get_real_ip(request), 100):
                return limit_error
            request.state.user_id = user_id
            request.state.username = username  # 把用户名绑定到request对象中
            return await call_next(request)
        except ExpiredSignatureError as e:
            log.error('\n' + traceback.format_exc())
            return auth_error
        except Exception as e:
            log.error(e)
            log.error('\n' + traceback.format_exc())
            return JSONResponse(content=ResponseUtils.error().model_dump(), status_code=200)

# 初始化跨域
def init_cors(app: FastAPI) -> None:
    """
    在app中注册cors的中间件，cors的中间件名字是：CORSMiddleware
    :param app:
    :return:
    """
    app.add_middleware(CORSMiddleware,
                       allow_origins=settings.ORIGINS,  # 前端服务器的源
                       allow_credentials=True,  # 指示跨域请求支持 cookies
                       allow_methods=["*"],  # 允许所有标准方法
                       allow_headers=["*"],
                       )

def init_middleware(app: FastAPI) -> None:

    # 在app中注册中间件。 才能生效
    # 增加trace_id
    app.middleware("http")(add_trace_id)
    # 校验token
    app.middleware('http')(verify_token)
    # 跨域
    init_cors(app)
