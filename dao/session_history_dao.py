from sqlalchemy.orm import Session
from utils.decorators import retry
from models.session_history import SessionHistory

class SessionHistoryDao:

    @staticmethod
    def get_by_session_id(db: Session, session_id: int) -> list[type[SessionHistory]]:
        return db.query(SessionHistory).filter(SessionHistory.session_id == session_id).order_by(SessionHistory.id).all()

    # @staticmethod
    # def get_by_session_id_type(db: Session, session_id: int, history_type: int =1) -> list[type[SessionHistory]]:
    #     return db.query(SessionHistory).filter(SessionHistory.session_id == session_id).filter(SessionHistory.history_type == history_type).all()

    @staticmethod
    @retry(2,1)
    def create_session_history(db: Session, obj: SessionHistory):
        db.add(obj)
        db.flush()
        db.refresh(obj)
        return obj

    @staticmethod
    def get_sessions_history_paging(db: Session, pno: int, page_size: int = 10, user_id: int = None) -> list[type[SessionHistory]]:
        offset = (pno - 1) * page_size
        query = db.query(SessionHistory).offset(offset).limit(page_size)
        if user_id is not None:
            query = query.filter_by(user_id=user_id)
        return query.all()