from sqlalchemy.orm import Session
from models.file_upload_record import FileUploadRecord
from utils.decorators import retry

class FileUploadRecordDao:
    @staticmethod
    @retry(delay=2, max_retries=3)
    def create_file_upload_record(db: Session, file_upload_record: FileUploadRecord):
        db.add(file_upload_record)
        db.commit()
        db.refresh(file_upload_record)
        return file_upload_record