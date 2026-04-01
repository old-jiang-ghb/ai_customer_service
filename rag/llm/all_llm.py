from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from sympy.strategies.core import switch

from core import settings
# 大模型相关常量
# deepseek非思考模型
DEEPSEEK_CHAT: str = "deepseek-chat"
# deepseek思考模型
DEEPSEEK_REASONER: str='deepseek-reasoner'
# ============================== 模型名称 ===========================
DEEPSEEK = 'deepseek'
OPEN_AI = 'openai'
ZHIPU_AI= 'zhipu'
# 所有的大模型client
# openai的，温度为0.1，不需要大模型过多想象填补，给一个正确答案就行
# llm = ChatOpenAI(
#     temperature=0.1,
#     model='gpt-4o-mini',
#     api_key=SecretStr(settings.OPENAI_API_KEY))

# deepseek
# llm = ChatOpenAI(
#     model=DEEPSEEK_CHAT,
#     api_key=SecretStr(settings.DEEPSEEK_API_KEY),
#     temperature=0.1,
#     base_url='https://api.deepseek.com')

def get_client(model_name: str = DEEPSEEK) -> ChatOpenAI:
    llm:ChatOpenAI | None = None
    if model_name == DEEPSEEK:
        llm = ChatOpenAI(
            model=DEEPSEEK_CHAT,
            api_key=SecretStr(settings.DEEPSEEK_API_KEY),
            temperature=0.1,
            base_url='https://api.deepseek.com')
    elif model_name == OPEN_AI:
        llm = ChatOpenAI(
            temperature=0.1,
            model='gpt-4o-mini',
            api_key=SecretStr(settings.OPENAI_API_KEY))
    return llm