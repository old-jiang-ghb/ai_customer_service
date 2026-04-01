from fastapi import FastAPI, APIRouter
from api.user_view import router as user_router
from api.session_view import router as session_router
from api.rag_view import router as rag_router
from api.session_history_view import router as session_history_router


def main_router()-> APIRouter :
    main_router_1 = APIRouter()
    main_router_1.include_router(user_router, tags=["用户管理"])
    main_router_1.include_router(session_router, tags=["会话管理"])
    main_router_1.include_router(rag_router, tags=["rag管理"])
    main_router_1.include_router(session_history_router, tags=["会话历史管理"])
    return  main_router_1


def init_main_routers(app: FastAPI):
    app.include_router(main_router(), prefix="/api")