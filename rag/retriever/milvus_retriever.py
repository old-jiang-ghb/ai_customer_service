from langchain_core.tools import create_retriever_tool
from numba.scripts.generate_lower_listing import description

from rag.vector_store.milvus_store import MilvusVectorStore
from core import settings
mvs = MilvusVectorStore()
# 创建连接
mvs.create_milvus(settings.FURNITURE_ASSISTANT_COLLECTION_NAME)
# milvus不支持mmr
mmr_retriever = mvs.milvus.as_retriever(
    search_type= "mmr",     # mmr多样性返回 默认是"similarity" 相似度，返回比较单一, "mmr", or
    search_kwargs={
        "k": 4,
        "fetch_k": 12, # 先从库里召回多少条数据
        "lambda_mult":0.6 # 多样性权重，0-1 ， 0则是完全相似，1则是完全多样，官方推荐使用0.6
    }
)

mmr_retriever_tool = create_retriever_tool(mmr_retriever, "mmr_retriever",
                                           description = ("用于回答用户关于家具的售前咨询，包括现货、尺寸定制、软硬、乳胶含量、"
                                            "异味、卷包发货、质保、安装、甲醛、拆洗、退换货、包邮、物流、"
                                            "适用人群（老人/儿童/孕妇/腰酸）、面料、功能、保养、售后等客服问题。"
                                            "仅在用户咨询家具相关问题时使用，闲聊或无关问题不调用。"))

# 表中含有稀疏向量和稠密向量，也可以使用重排名 （rrf：多路召回融合排序，另一个是加权评分：加权评分（WeightedRanker）weighted）
rrf_retriever = mvs.milvus.as_retriever(
    search_type= "similarity",
    search_kwargs={
        "k": 4,
        "score_threshold": 0.1,
        "ranker_type": "rrf",
        "ranker_params": {"k": 100},
        "filter": {"category": "content"}
    }
)
# 加权评分
weighted_retriever = mvs.milvus.as_retriever(
    search_type="similarity",
    search_kwargs={
        "k": 4,
        "score_threshold": 0.1,
        "ranker_type": "weighted",
        "ranker_params": {
            "weights": [0.7, 0.3]  # 向量70%(稠密向量)，关键词30%(稀疏向量)
        },
        "filter": {"category": "content"}
    }
)