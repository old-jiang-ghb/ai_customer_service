from fastapi import APIRouter,Depends,Request
from sqlalchemy.orm import Session

from core.database import get_db
from schemas.session_schemas import SessionResponse, SessionCreateOrUpdate
from schemas import BasePaging
from service.session_service import SessionService
from utils.response_utils import ResponseUtils
# 创建分路由
router = APIRouter(prefix="/session")


@router.post('/paging', description='分页获取会话', summary='分页获取会话')
def paging(param:BasePaging, request: Request, session: Session = Depends(get_db)):
    user_id = request.state.user_id
    sessions, total = SessionService.paging(session, param.pno, param.page_size, user_id)
    # 2. 【核心】批量转成 Pydantic 模型
    session_response_list = [
        SessionResponse.model_validate(session) for session in sessions
    ]
    return ResponseUtils.success_rsp(data={
        'list': session_response_list,
        'total': total,
        'page': param.pno,
        'page_size': param.page_size
    })

@router.put('', description='分页获取会话', summary='分页获取会话')
def create_session(session_in: SessionCreateOrUpdate,request: Request, db: Session = Depends(get_db)):
    # 截断
    session_in.session_name = session_in.session_name if len(session_in.session_name) <=20 else session_in.session_name[0:21]
    session_in.user_id = request.state.user_id
    session = SessionService.create_session(db, session_in)
    return ResponseUtils.success_rsp(data=SessionResponse.model_validate(session))