from sqlalchemy.orm import Session
from models.session import Session as st
from dao.session_dao import SessionDao
from schemas.session_schemas import SessionCreateOrUpdate


class SessionService:
    @staticmethod
    def paging(db: Session, pno: int, page_size: int, user_id: int = None):
        sessions = SessionDao.get_session_paging(db, pno, page_size, user_id)
        count = SessionDao.get_session_count(db, user_id)
        return sessions, count

    @staticmethod
    def create_session(db: Session, session_in: SessionCreateOrUpdate):
        session = st(user_id=session_in.user_id, session_name=session_in.session_name)
        SessionDao.create_session(db, session)
        db.commit()
        return session