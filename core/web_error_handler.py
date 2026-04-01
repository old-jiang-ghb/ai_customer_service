from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from core.exception import BusinessException
from utils.response_utils import ResponseUtils
from utils.logger_utils import log
import traceback

# ---------------------------
# HTTP 异常
# ---------------------------
async def http_exception_handler(request: Request, exc: HTTPException):
    log.warning(f"HTTP异常: {exc.status_code} | {exc.detail}")
    resp = ResponseUtils.error(code=exc.status_code, msg=exc.detail)
    return JSONResponse(content=resp.model_dump(), status_code=200)

# ---------------------------
# 业务异常
# ---------------------------
async def business_exception_handler(request: Request, exc: BusinessException):
    log.warning(f"业务异常: {exc.code} | {exc.msg}")
    resp = ResponseUtils.error(code=exc.code, msg=exc.msg)
    return JSONResponse(content=resp.model_dump(), status_code=200)

# ---------------------------
# 参数校验异常
# ---------------------------
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    log.warning(f"参数错误: {exc.errors()}")
    resp = ResponseUtils.error(code=400, msg="请求参数格式错误")
    return JSONResponse(content=resp.model_dump(), status_code=200)

# ---------------------------
# 全局兜底异常（系统/代码BUG）
# ---------------------------
async def global_exception_handler(request: Request, exc: Exception):
    log.error(f"系统异常:\n{traceback.format_exc()}")
    resp = ResponseUtils.error(code=500, msg="服务器内部异常")
    return JSONResponse(content=resp.model_dump(), status_code=200)

# ---------------------------
# 注册所有异常
# ---------------------------
def register_exceptions(app):
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(BusinessException, business_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)