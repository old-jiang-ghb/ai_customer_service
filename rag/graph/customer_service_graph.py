from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END

from rag.graph import MyAgentState
from rag.graph.all_nodes import (score_router, fallback_node,generate,rewrite_question,score_node
,retrieve_node,init_node)
import uuid


# 咨询客服工作流
def build_ai_customer_service_graph() -> StateGraph:
    # 定义一个新的工作流图
    workflow = StateGraph(MyAgentState)

    # 增加节点
    workflow.add_node("init", init_node)
    workflow.add_node("score", score_node)
    workflow.add_node("fallback", fallback_node)
    workflow.add_node("generate", generate)
    workflow.add_node("rewrite", rewrite_question)
    workflow.add_node("retrieve", retrieve_node)
    # 首个节点先检测问题是否为家具相关的客服问题
    workflow.set_entry_point("init")
    workflow.add_edge("init", "retrieve")
    workflow.add_edge("retrieve", "score")
    # 增加评分完成后的条件路由
    workflow.add_conditional_edges(
        "score",
        score_router,
        {
            "generate": "generate",
            "rewrite": "rewrite",
            "fallback": "fallback"
        }
    )
    workflow.add_edge("rewrite", "retrieve")
    workflow.add_edge("generate", END)
    workflow.add_edge("fallback", END)
    return workflow

if __name__ == "__main__":
    graph = build_ai_customer_service_graph()

    inputs = {
        "question": "这款床垫现在有现货吗？",
        "rewritten_question": "",
        "retrieved_docs": [],
        "scored_decision": "NO",
        "rewrite_count": 0,  # 初始次数 0
        "messages": []
    }

    config = RunnableConfig(configurable={
        "thread_id": str(uuid.uuid4())
    })
    result = graph.invoke(inputs, config)
    print(result["messages"][-1].content)