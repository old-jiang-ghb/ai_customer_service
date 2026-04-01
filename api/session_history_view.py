from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.requests import Request
from core.database import get_db
from service.session_history_service import SessionHistoryService
from schemas.session_history_schemas import SessionHistoryResponse
from utils.response_utils import ResponseUtils

# 创建分路由
router = APIRouter(prefix="/session/history")

@router.get("/{session_id}", description="根据session_id查历史聊天记录")
def get_by_session_id(session_id:int, request: Request, db: Session = Depends(get_db)):
    session_histories = SessionHistoryService.get_by_session_id(db, session_id, request.state.user_id)
    result_list = [SessionHistoryResponse.model_validate(session_history) for session_history in session_histories]
    return ResponseUtils.success_rsp(data=result_list)