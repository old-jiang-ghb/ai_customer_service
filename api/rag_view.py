import asyncio
from fastapi import APIRouter,UploadFile, File, Depends, Request
import os
import uuid
import json
from fastapi.responses import StreamingResponse
from typing import Optional

from core.database import get_db
from utils.response_utils import ResponseUtils
from sqlalchemy.orm import Session
from core import __BASE_DIR, settings
from core.exception import BusinessException
from rag.service.rag_service import RagService
from cache.rate_limit import RateLimiter

router = APIRouter(prefix="/rag")
# 生成上传文件的根本路径
UPLOAD_MD_FILE_SAVE_DIR =  __BASE_DIR.__str__() +  r"\dataes\upload_files\md"
os.makedirs(UPLOAD_MD_FILE_SAVE_DIR, exist_ok=True)

@router.post("/upload-md")
async def upload_md(request: Request, file: UploadFile = File(...), session: Session = Depends(get_db)):
    """
    上传md文件到后端，后端进行异步解析
    1.先将文件保存在本地（备份）
    2.数据库存储一条记录，记录谁上传的，以及时间，真实文件名，后端生成的文件名（对应）.后续如果系统出现了问题，则可以订正数据
    3.异步处理上传文件
    """
    # 校验格式
    if not file.filename.endswith(".md"):
        raise BusinessException(code=400, msg="仅支持 .md 文件")
    # 生成本地保存路径（用uuid防止重名覆盖）
    unique_filename = f"{uuid.uuid4().hex[:8]}_{file.filename}"
    local_file_path = os.path.join(UPLOAD_MD_FILE_SAVE_DIR, unique_filename)

    # 1. 保存到本地
    with open(local_file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    user_id = request.state.user_id
    asyncio.create_task(asyncio.to_thread(RagService.process_and_save_to_milvus,
                                          session, local_file_path,user_id, file.filename, unique_filename))

    return ResponseUtils.success_rsp(msg="上传成功，正在后台导入向量数据库")

#用户向ai客服提问
@router.post("/chat/steam")
async def chat_steam(request: Request, question:str, session_id: Optional[int]):

    user_id = request.state.user_id
    # 限流,同一个用户id同一时间只能咨询25次
    if not RateLimiter.is_allowed(user_id, 25):
        raise BusinessException(msg="请求次数过多，请稍后重试")

    generator = RagService.chat_stream_generator(question, user_id, session_id)
    # 流式返回 + 统一 ResponseUtils 包装
    async def wrapped_generator():
        for ans in generator:
            res = ResponseUtils.success_rsp(ans)
            yield f"data: {json.dumps(res.__dict__, ensure_ascii=False)}\n\n"
    return StreamingResponse(
        wrapped_generator(),
        media_type="text/event-stream"
    )

# 获取rag相关配置接口
@router.get("/config", description="获取rag相关配置接口")
def get_rag_config():
    result = {
        'hot_problem': settings.HOT_PROBLEM
    }
    # 后续常用配置就往result里面append就可以了
    return ResponseUtils.success_rsp(data=result)
