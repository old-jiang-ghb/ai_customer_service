from langchain_core.runnables import RunnableConfig

from cache.chat_cache import ChatHistoryCache
from cache.hot_problem_cache import HotQACache
from core.exception import BusinessException
from dao.file_upload_record_dao import FileUploadRecordDao
from dao.session_dao import SessionDao
from models.file_upload_record import FileUploadRecord
from models.session import Session
from models.session_history import SessionHistory, USER_HISTORY_TYPE, AI_HISTORY_TYPE
from rag.loder.parser import MarkdownParser
from rag.vector_store.milvus_store import MilvusVectorStore
from core import settings
from core.database import get_db
from utils.logger_utils import log
from rag.graph.memory import CommonLongMemoryCheckPointSaver
from rag.graph.customer_service_graph import build_ai_customer_service_graph
from dao.session_history_dao import SessionHistoryDao

# 向量知识库service
class RagService:

    @staticmethod
    def process_and_save_to_milvus(db: Session, file_path: str, user_id: int, file_name: str, local_file_name: str):
        """
        :param db:
        :param file_path:文件路径
        :param user_id: 用户id
        :param file_name: 原文件名称
        :param local_file_name: 本地生成的文件名称
        :return:
        """
        # 1.将文件解析写入向量数据库
        mp = MarkdownParser()
        docs = mp.parse_markdown_to_document(file_path)
        # 获取向量数据库
        mvs = MilvusVectorStore()
        mvs.create_milvus(collection_name=settings.FURNITURE_ASSISTANT_COLLECTION_NAME)
        mvs.add_documents(docs)
        # 2.将文件数据写入数据库
        FileUploadRecordDao.create_file_upload_record(db,
                                                      FileUploadRecord(user_id=user_id,
                                                                       file_name=file_name,
                                                                       local_file_name=local_file_name,
                                                                       local_file_path=file_path, state=1))

    # 流式输出ai调用结果
    @staticmethod
    def chat_stream_generator(question: str, user_id: int, session_id: int):
        # 生成session -> 调用工作流 ->返回结果
        db = next(get_db())
        # 会话名称只截取前20位
        try:
            session_name = question if len(question) <= 20 else question[0:21]
            if session_id:
                session = SessionDao.get_session(db, session_id)
                if not session:
                    raise BusinessException("会话不存在")
            else:
                session = SessionDao.create_session(db, Session(user_id=user_id, session_name=session_name))
            # 命中缓存逻辑
            cached_data = HotQACache.get(question)
            current_session_id = session.id
            # 热问题直接回复，并且加入到聊天记录里面
            if cached_data:
                log.info(f"命中热问题缓存:{cached_data}")
                answer = cached_data["answer"]
                # 更新聊天历史
                ChatHistoryCache.add_message(current_session_id, USER_HISTORY_TYPE, question)
                ChatHistoryCache.add_message(current_session_id, AI_HISTORY_TYPE, answer)
                # 更新数据库聊天历史
                # 用户的问题
                SessionHistoryDao.create_session_history(db, SessionHistory(
                    session_id=current_session_id,
                    detail=question,
                    history_type=USER_HISTORY_TYPE
                ))
                # ai回复
                SessionHistoryDao.create_session_history(db, SessionHistory(
                    session_id=current_session_id,
                    detail=answer,
                    history_type=AI_HISTORY_TYPE
                ))
                yield answer
                db.commit()
                return

            # 长期记忆
            memory_saver = CommonLongMemoryCheckPointSaver(db)
            graph = build_ai_customer_service_graph().compile(checkpointer=memory_saver)
            inputs = {
                "question": question,
                "rewritten_question": "",
                "retrieved_docs": [],
                "scored_decision": "NO",
                "rewrite_count": 0,
                "messages": [],
                "next": "",
                "db": db,
                "session_id": current_session_id
            }

            config = RunnableConfig(configurable={
                "thread_id": current_session_id,
                "question": question
            })

            final_answer = ""
            for chunk in graph.stream(inputs, config):
                if "generate" in chunk:
                    answer = chunk["generate"]["messages"][-1].content
                    final_answer = answer
                    yield answer
                elif "fallback" in chunk:
                    answer = chunk["fallback"]["messages"][-1].content
                    final_answer = answer
                    yield answer
            if question in settings.HOT_PROBLEM:
                HotQACache.set(question, final_answer)
            db.commit()

        except Exception as e:
            log.error("流式输出业务异常，全部回滚，请即使查看问题原因", e)
            db.rollback()
            raise BusinessException("服务异常，请稍后再试")
        finally:
            db.close()
