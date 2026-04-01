from fastapi import Request
from sqlalchemy.orm import Session

from service.user_service import UserService
# 获取用户信息的工具
def get_current_user(request: Request, db: Session):
    user_id = request.state.user_id
    user = UserService.get_user(db, user_id)
    return user

def get_real_ip(request: Request) -> str:
    """
    企业级获取真实客户端IP
    支持：本地运行、Nginx、Docker、K8s、阿里云、腾讯云、云函数
    """
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        ip_list = [ip.strip() for ip in forwarded_for.split(",") if ip.strip()]
        if ip_list:
            return ip_list[0]

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    return request.client.host if request.client else "unknown"