from typing import TypedDict, Annotated, Literal
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage
from pydantic import BaseModel,Field
from sqlalchemy.orm import Session


# 自定义状态
class MyAgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    question: str  # 原始问题
    rewritten_question: str  # 重写后的问题
    retrieved_docs: list[str]  # 检索到的文档
    scored_decision: Literal["YES", "NO"]  # 评分决策
    rewrite_count: int  # 重写次数（核心熔断）
    next: str
    # intent:Literal["YES", "NO"]
    db: Session
    history_messages: list[BaseMessage]
    session_id: str #会话id

# ========================================
# 模型类
class Grade(BaseModel):
    """相关性检查的二元评分"""
    binary_score: str = Field(description="相关性评分 'YES' 或 'NO'", default="NO")