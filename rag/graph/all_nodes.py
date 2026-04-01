from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from typing import Literal
from core import settings
from models.session_history import USER_HISTORY_TYPE, AI_HISTORY_TYPE
from rag.graph import MyAgentState
from rag.retriever.milvus_retriever import rrf_retriever
from rag.llm.all_llm import get_client
from rag.llm.all_llm import DEEPSEEK
from utils.logger_utils import log
from dao.session_history_dao import SessionHistoryDao
from cache.chat_cache import ChatHistoryCache
import json
deepseek_llm = get_client(DEEPSEEK)


# 1. 定义初始化节点（读取历史消息并注入）
# 1. 定义初始化节点（读取历史消息并注入）
def init_node(state):
    session_id = state["session_id"]
    db = state["db"]

    # 1. 先从缓存拿（拿到的是 字典列表）
    history_messages = ChatHistoryCache.get(session_id)

    if not history_messages:
        # 2. 缓存没有 → 查数据库
        data = SessionHistoryDao.get_by_session_id(db, session_id)
        history_messages = []

        if data:
            # 【关键】存成 字典，不要存 Message 对象！
            cache_save_list = []
            for history_message in data:
                if history_message.history_type == USER_HISTORY_TYPE:
                    history_messages.append(HumanMessage(content=str(history_message.detail)))
                    cache_save_list.append({"history_type": USER_HISTORY_TYPE, "detail": str(history_message.detail)})

                elif history_message.history_type == AI_HISTORY_TYPE:
                    history_messages.append(AIMessage(content=str(history_message.detail)))
                    cache_save_list.append({"history_type": AI_HISTORY_TYPE, "detail": str(history_message.detail)})

            # 3. 回写缓存（只写字典，不写对象！）
            ChatHistoryCache.set(session_id, cache_save_list)

    # 4. 如果缓存里有数据，需要把字典 → Message 对象
    else:
        temp = []
        for msg in history_messages:
            if msg["history_type"] == USER_HISTORY_TYPE:
                temp.append(HumanMessage(content=msg["detail"]))
            elif msg["history_type"] == AI_HISTORY_TYPE:
                temp.append(AIMessage(content=msg["detail"]))
        history_messages = temp

    return {
        "history_messages": history_messages,
    }


# 意图识别（问题是否与客服相关）
# def intent_recognize_node(state: MyAgentState):
#     question = state["question"]
#     prompt = f"""
#     你是家具售前客服意图分类器。
#     只输出 JSON，不要其他任何文字。
#     判断用户问题是否是【家具相关咨询】。
#
#     输出格式:
#     {{
#         "intent": "YES 或 NO"
#     }}
#
#     用户问题：{question}
#     """
#     rsp = deepseek_llm.invoke(prompt)
#     result = json.loads(rsp.content.strip())
#     return {"intent": result.get("intent", "NO")}


# 搜索向量知识库并且返回
def retrieve_node(state: MyAgentState):
    question = state["rewritten_question"] or state["question"]
    docs = rrf_retriever.invoke(input=question)
    return {"retrieved_docs":[doc.page_content for doc in docs]}


# 评分节点
def score_node(state: MyAgentState):
    print(f"score_node打印状态:{json.dumps({"messages": state}, ensure_ascii=False, default=str)}")
    question = state["rewritten_question"] or state["question"]
    # 拼接以换行符拼接所有文档
    context = '\n'.join(state["retrieved_docs"])
    prompt = f"""
    你是专业的文档相关性判定器。
    只输出 JSON，不要其他任何文字。
    规则：
    - 文档相关能准确回答问题 → YES
    - 文档无关、不足、无法回答 → NO
    输出格式:
    {{
        "decision": "YES 或 NO",
    }}

    问题：{question}
    知识库内容：{context}
    """
    res = deepseek_llm.invoke(prompt)
    res = json.loads(res.content.strip())
    return {"scored_decision": res.get("decision", "NO")}

# 重写节点
def rewrite_question(state: MyAgentState):
    print(f"rewrite_question打印状态:{json.dumps({"messages": state}, ensure_ascii=False, default=str)}")
    question = state["rewritten_question"] or state["question"]
    history_messages = state["history_messages"]
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你能够根据用户与客服聊天的上下文优化用户现在问的问题，让用户问题更清晰、更适合向量数据库检索且不改变原来的意思。"),
        *history_messages,
        ("user", "{question}")
    ])
    rewrite_rsp = deepseek_llm.invoke(prompt.format_messages(question= question))
    log.info(f"问题:{question}重写节点的结果:{rewrite_rsp}")
    # 返回重写数据,重写次数＋1
    return {
        "rewritten_question": rewrite_rsp.content,
        "rewrite_count" : state["rewrite_count"] + 1
    }

def generate(state: MyAgentState):
    # 生成最终答案
    question = state["rewritten_question"] or state["question"]
    context = "\n".join(state["retrieved_docs"])
    history_messages = state["history_messages"]
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个客服回复助手。请根据文档内容回答问题。注意涉及到内部价格计算不要透出给用户,给一个数字就行"
                   "如果不知道答案，请直接说明。回答保持简洁,需要有客服的亲和力.文档:{context}"),
        *history_messages,
        ("user", "{question}")
    ])
    rsp = deepseek_llm.invoke(prompt.format_messages(question=question, context=context))
    finish_reason = None
    if hasattr(rsp, "response_metadata"):
        finish_reason = rsp.response_metadata.get("Finish reason", "")
    if finish_reason is not None and finish_reason=='content_filter':
        log.warn(f"deepseek敏感词拦截，用户问题:{question}")
        return {"messages": [AIMessage(content= settings.CONTENT_FILTER_RESULT)]}
    return {"messages": [AIMessage(content=rsp.content)]}

# 兜底节点
def fallback_node(state: MyAgentState):
    return {
        "messages": [
            AIMessage(content="非常抱歉，"
                              "我无法为您的问题提供准确回复。您可以尝试更换问题或联系人工客服。")
        ]
    }

# 路由节点
def score_router(state: MyAgentState) -> Literal["generate", "rewrite", "fallback"]:
    # 企业级熔断：最多允许重写 由配置决定 次
    if state["rewrite_count"] >= settings.REWRITE_COUNT:
        log.warn(f"重写warn:重写两次没有成功获取结果,请检查原因.用户问题:{state["question"]}")
        # 这里能不能转到让ai自由发挥？如果知识库没有，是不是可以让ai输出委婉拒绝，比较让人舒心的回复
        return "fallback"

    if state["scored_decision"] == "YES":
        return "generate"
    else:
        return "rewrite"

# 是否进入工作流路由
# def intent_router(state: MyAgentState) -> Literal["retrieve", "fallback"]:
#     if state["intent"] == "YES":
#         return "retrieve"
#     else:
#         log.warn(f"进入工作流warn:用户问题没有进入工作流,请检查原因.用户问题:{state["question"]}")
#         return "fallback"