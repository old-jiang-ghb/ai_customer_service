import re
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request
from typing import Optional
from core import settings

class MyOauth2PasswordBearer(OAuth2PasswordBearer) :
    def __init__(self, tokenUrl: str , schema: str):
        super().__init__(
            tokenUrl=tokenUrl,
            scheme_name= schema,
            auto_error= True
        )

    async def __call__(self, request: Request) -> Optional[str]:
        """
                解析请求头中的token。 在接口文档中传递token的格式是固定的： Authorization： JWT token值
                :param request:
                :return:
                """
        path: str = request.get('path')
        # 根据白名单来过滤
        for request_path in settings.WHITE_LIST:
            if re.match(request_path, path):
                return ''
        else:  # 请求路径不是白名单里面的，则鉴权
            return super().__call__(request)