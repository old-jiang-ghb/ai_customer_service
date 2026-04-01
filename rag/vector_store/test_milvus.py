import json
from rag.retriever.milvus_retriever import rrf_retriever
if __name__ == '__main__':
    docs = rrf_retriever.invoke(input="这款床垫有现货吗?")
    print(docs)
    print(json.dumps(f"{'messages': {docs}}"))
    # 连接 Milvus
    # connections.connect(uri="http://localhost:19530")
    #
    # # 获取集合
    # collection = Collection("t_furniture_assistant")
    #
    # # =====================
    # # 遍历 fields
    # # =====================
    # for field in collection.schema.fields:
    #     print(f"字段名: {field.name}")
    #     print(f"开启分词: {getattr(field, 'enable_analyzer', '无此属性')}")
    #     print(f"分词配置: {getattr(field, 'analyzer_params', '无此属性')}")
    #     print("-" * 50)