from sqlalchemy.orm import Session
from models.session import Session as st


class SessionDao:

    @staticmethod
    def get_session(db: Session, session_id) -> type[st] | None:
        return db.query(st).filter(st.id == session_id).filter(st.is_del == 0).first()

    @staticmethod
    def create_session(db: Session, session: st):
        db.add(session)
        db.flush()
        db.refresh(session)
        return session

    @staticmethod
    def get_session_by_user_id(db: Session, user_id: int) -> list[type[st]]:
        query = db.query(st).filter(st.is_del == 0).filter(st.user_id == user_id)
        return query.all()

    @staticmethod
    def get_session_paging(db: Session, pno: int, page_size: int = 10, user_id: int = None) -> list[type[st]]:
        offset = (pno - 1) * page_size
        query = db.query(st).filter(st.is_del == 0)
        if user_id is not None:
            query = query.filter(st.user_id == user_id)
        query = query.order_by(st.id.desc()).offset(offset).limit(page_size)
        return query.all()

    @staticmethod
    def get_session_count(db: Session , user_id: int = None):
        query = db.query(st).filter(st.is_del == 0)
        if user_id is not None:
            query = query.filter(st.user_id == user_id)
        return query.count()