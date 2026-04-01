from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from core import settings
import os

# 1. 设置 OpenAI Key
os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
# 如果你用中转/代理，就加这个
# os.environ["OPENAI_BASE_URL"] = ""

openai_embedding = OpenAIEmbeddings(
    model= settings.OPENAI_TEXT_EMBEDDING_MODEL
)

# model_name = "BAAI/bge-small-zh-v1.5"
# model_name = 'C:\Users\Administrator\.cache\huggingface\hub\models--BAAI--bge-small-zh-v1.5\snapshots\7999e1d3359715c523056ef9478215996d62a620'
# 本地模型位置
model_name = r"E:\big_model\bge-large-zh-v1.5"
model_kwargs = {"device": "cpu"}
encode_kwargs = {"normalize_embeddings": True}
# 嵌入模型
bge_embedding = HuggingFaceEmbeddings(
    model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
)