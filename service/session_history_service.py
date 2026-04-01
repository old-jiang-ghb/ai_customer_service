from sqlalchemy.orm import Session

from core.exception import BusinessException
from dao.session_dao import SessionDao
from dao.session_history_dao import SessionHistoryDao
# 会话记录service
class SessionHistoryService:

    @staticmethod
    def get_by_session_id(db: Session, session_id: int, user_id: int):
        sessions = SessionDao.get_session_by_user_id(db, user_id)
        if session_id not in [session.id for session in sessions]:
            raise BusinessException(msg="当前会话不属于当前登录用户，请重新登录")
        session_histories = SessionHistoryDao.get_by_session_id(db, session_id)
        return session_histories