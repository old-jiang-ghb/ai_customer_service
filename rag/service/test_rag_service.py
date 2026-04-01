# 导入mysqldb
import os
import pymysql
pymysql.install_as_MySQLdb()
# huggingface镜像
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
from rag.service.rag_service import RagService
from core.database import get_db
if __name__ == '__main__':
    db = get_db()
    RagService.process_and_save_to_milvus(db, r"E:\python-workspace\ai_customer_service\dataes\md\ask.md",
                                          1, "ask.md", "ask.md")