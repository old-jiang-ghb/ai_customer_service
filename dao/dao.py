from sqlalchemy.orm import Session
# 基础的CRUD
class BaseCRUD:
    def __init__(self, model):
        self.model = model

    # 查询单条
    def get(self, db: Session, id: int):
        return db.query(self.model).filter(self.model.id == id).first()

    # 修改
    def update(self, db: Session, id: int, data: dict):
        obj = self.get(db, id)
        if not obj:
            return None
        for key, value in data.items():
            setattr(obj, key, value)
        db.commit()
        db.refresh(obj)
        return obj