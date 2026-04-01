from pydantic import BaseModel, field_validator, Field
from typing import Union


# ==================== 前端传过来的创建用户参数（入参） ====================
class BaseUser(BaseModel):
    username: str = Field(description='用户名称')
    real_name: Union[str, None] = Field(description='用户真实名称', default='ai小智')
    last_login_ip: Union[str, None] = Field(description='最后一次登录IP地址', default='')
    desc: Union[str, None] = Field(description='用户描述', default=None)
    tel: Union[str, None] = Field(description='联系电话', default=None)
    email: Union[str, None] = Field(description='用户邮箱', default=None)

class UserCreateOrUpdate(BaseUser):
    password: str = Field(description='密码')
    user_type: int = Field(description='用户类型', default=1)
    # 可以加校验（可选）
    @field_validator("username")
    def username_is_null(cls, v):
        if v is None:
            raise ValueError("用户名不能为空")
        return v

    @field_validator("password")
    def password(cls, v):
        if v is None:
            raise ValueError("密码不能为空")
        return v
class UserLogin(BaseModel):
    """用户登录接受数据的模型类型"""
    username: str = Field(description='用户名')
    password: str = Field(description='密码')

# ==================== 前端返回的用户信息（出参） ====================
class UserBaseResponse(BaseUser):
    id: int = Field(description='用户id')
    # 让 Pydantic 兼容 ORM 对象
    class Config:
        from_attributes = True
class UserResponse(BaseUser):
    id: int = Field(description='用户id')
    token: str
    # 让 Pydantic 兼容 ORM 对象
    class Config:
        from_attributes = True

