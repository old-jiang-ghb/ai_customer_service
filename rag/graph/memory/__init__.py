from collections.abc import AsyncIterator, Iterator, Sequence
from typing import Any

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import BaseCheckpointSaver, CheckpointTuple, Checkpoint,CheckpointMetadata,ChannelVersions
from sqlalchemy.orm import Session
from cache.chat_cache import ChatHistoryCache
from dao.session_history_dao import SessionHistoryDao
from models.session_history import SessionHistory, USER_HISTORY_TYPE, AI_HISTORY_TYPE


# 自定义通用长期记忆 Checkpoint ， 对接mysql数据库
class CommonLongMemoryCheckPointSaver(BaseCheckpointSaver):
    def __init__(self, db: Session):
        super().__init__()
        # 缓存记忆
        self.cache = {}
        self.db = db

    def get_tuple(self, config: RunnableConfig) -> CheckpointTuple | None:
        return None

    def put(
            self,
            config: RunnableConfig,
            checkpoint: Checkpoint,
            metadata: CheckpointMetadata,
            new_versions: ChannelVersions,
    ) -> RunnableConfig:
        channel_values = checkpoint.get("channel_values", {})
        if "__start__" in channel_values:
            # 这是框架初始节点 → 跳过
            return config
        session_id = config["configurable"]["thread_id"]
        question = config["configurable"]["question"]
        messages = channel_values.get("messages", [])
        # 更新缓存，因为这里的checkpoint里面的messages已经更新了
        self.cache[session_id] = CheckpointTuple(config, checkpoint, metadata)

        if not messages:
            return config

        writes = metadata.get("writes", {})
        if "generate" in writes or "fallback" in writes:
            # 入库逻辑
            try:
                # 用户的问题
                SessionHistoryDao.create_session_history(self.db, SessionHistory(
                    session_id=session_id,
                    detail=question,
                    history_type=USER_HISTORY_TYPE
                ))
                # 将messages返过来进行读取，
                for msg in reversed(messages):
                    # ai给的最终回复
                    if msg.type == "ai":
                        SessionHistoryDao.create_session_history(self.db, SessionHistory(
                            session_id=session_id,
                            detail=msg.content,
                            history_type=AI_HISTORY_TYPE
                        ))
                        # 回写缓存
                        ChatHistoryCache.add_message(session_id, USER_HISTORY_TYPE, question)
                        ChatHistoryCache.add_message(session_id, AI_HISTORY_TYPE, msg.content)
                        break

            except Exception as e:
                print(f"用户聊天记录保存失败，session_id:{session_id},已回滚", e)
                raise e
        return config

    def put_writes(
            self,
            config: RunnableConfig,
            writes: Sequence[tuple[str, Any]],
            task_id: str,
            task_path: str = "",
    ) -> None:
        pass

    def list(
            self,
            config: RunnableConfig | None,
            *,
            filter: dict[str, Any] | None = None,
            before: RunnableConfig | None = None,
            limit: int | None = None,
    ) -> Iterator[CheckpointTuple]:
        return iter([])

    def delete_thread(
            self,
            thread_id: str,
    ) -> None:
        pass

    async def aget_tuple(self, config: RunnableConfig) -> CheckpointTuple | None:
        pass

    async def alist(
            self,
            config: RunnableConfig | None,
            *,
            filter: dict[str, Any] | None = None,
            before: RunnableConfig | None = None,
            limit: int | None = None,
    ) -> AsyncIterator[CheckpointTuple]:
        pass

    async def aput(
            self,
            config: RunnableConfig,
            checkpoint: Checkpoint,
            metadata: CheckpointMetadata,
            new_versions: ChannelVersions,
    ) -> RunnableConfig:
        pass

    async def aput_writes(
            self,
            config: RunnableConfig,
            writes: Sequence[tuple[str, Any]],
            task_id: str,
            task_path: str = "",
    ) -> None:
        pass

    async def adelete_thread(
            self,
            thread_id: str,
    ) -> None:
        pass