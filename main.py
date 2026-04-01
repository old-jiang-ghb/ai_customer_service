# 导入mysqldb
import pymysql
import os
pymysql.install_as_MySQLdb()
# huggingface镜像
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
from core.docs_oauth2 import MyOauth2PasswordBearer
from fastapi import FastAPI , Depends
from core import web_error_handler, middlewares,settings
from api import routers
import uvicorn

class Server:

    def __init__(self):
        # 创建自定义的OAuth2的实例
        my_oauth2 = MyOauth2PasswordBearer("/api/user/auth", "Bearer")

        # 添加全局的依赖: 让所有的接口，都拥有接口文档的认证
        self.app = FastAPI(dependencies=[Depends(my_oauth2)])

    # 初始化web服务全局所需配置
    def init_all_global(self):
        # 初始化全局异常处理
        web_error_handler.register_exceptions(self.app)
        # 初始化全局中间件
        middlewares.init_middleware(self.app)
        # 初始化主路由
        routers.init_main_routers(self.app)

    def run(self):
        self.init_all_global()
        uvicorn.run(app=self.app, host=settings.HOST, port=settings.PORT)

if __name__ == "__main__":
    Server().run()