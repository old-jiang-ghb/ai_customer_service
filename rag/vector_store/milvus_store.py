
from langchain_core.documents import Document
from langchain_milvus import Milvus, BM25BuiltInFunction
from pymilvus import MilvusClient, Function
from typing import List

from utils.decorators import retry
from core import settings
from rag.embeddings.embedding import bge_embedding
from pymilvus.client.types import DataType, FunctionType
from utils.logger_utils import log


# milvus向量数据库相关操作
class MilvusVectorStore:

    def __init__(self):
        self.milvus : Milvus=None

    # 使用pymilvus创建家具助手知识库集合 ， 因为langchain-milvus不支持自定义schema
    def create_collection(self, collection_name: str = settings.FURNITURE_ASSISTANT_COLLECTION_NAME):
        milvus_client = MilvusClient(settings.MILVUS_URI)
        schema = milvus_client.create_schema()
        schema.add_field(field_name='id', datatype=DataType.INT64, is_primary=True, auto_id=True)
        # 最长设置4000，因为3000会进行语义切割
        schema.add_field(field_name='text', datatype=DataType.VARCHAR, max_length=4000,
                         enable_analyzer=True, # 开启文本分词才支持关键词搜索/全文检索/BM25
                         analyzer_params={"tokenizer": "standard", "filter": ["cnalphanumonly"]}) # 分词器还可以选择jieba
        schema.add_field(field_name='category', datatype=DataType.VARCHAR, max_length=1000)
        schema.add_field(field_name='source', datatype=DataType.VARCHAR, max_length=1000)
        schema.add_field(field_name='filename', datatype=DataType.VARCHAR, max_length=1000)
        schema.add_field(field_name='filetype', datatype=DataType.VARCHAR, max_length=1000)
        schema.add_field(field_name='title', datatype=DataType.VARCHAR, max_length=1000)
        # 使用稀疏，稠密双向量检索
        schema.add_field(field_name='sparse', datatype=DataType.SPARSE_FLOAT_VECTOR)
        schema.add_field(field_name='dense', datatype=DataType.FLOAT_VECTOR, dim=1024)

        bm25_function = Function(
            name="text_bm25_emb",
            input_field_names=["text"],
            output_field_names=["sparse"],
            function_type=FunctionType.BM25,
        )
        schema.add_function(bm25_function)
        index_params = milvus_client.prepare_index_params()

        index_params.add_index(
            field_name="sparse",
            index_name="sparse_inverted_index",
            index_type="SPARSE_INVERTED_INDEX", #稀疏向量固定索引类型
            metric_type="BM25",                 #计算相关性的算法
            params={
                "inverted_index_algo": "DAAT_MAXSCORE", # 查询算法，官方推荐
                "bm25_k1": 1.2,  # 控制：关键词出现次数对结果的影响,默认就是1.2
                "bm25_b": 0.75   # 控制：文本长度对相关性的影响
            },
        )
        index_params.add_index(
            field_name="dense",
            index_name="dense_inverted_index",
            index_type="HNSW",     # 稠密向量一般都用这个索引 (基于图实现的)
            metric_type="IP",       # 可以选择 IP（内积适合已经做了归一化的），COSINE（余弦相似度，适合没做归一化的），L2（欧式距离，适合坐标，位置，数值预测）
            params={"M": 16, "efConstruction": 64}  # M :邻接节点数(M越大精度越高、内存越大), efConstruction: 搜索范围(越大建索引越慢、精度越高)，按需对这两个参数进行调优
        )

        if collection_name in milvus_client.list_collections():
            # 先释放， 再删除索引，再删除collection
            index_params.add_index(
                field_name="sparse",
                index_name="sparse_inverted_index",
                index_type="SPARSE_INVERTED_INDEX",
                metric_type="BM25",
                params={
                    "inverted_index_algo": "DAAT_MAXSCORE",
                    "bm25_k1": 1.2,
                    "bm25_b": 0.75
                },
            )
            milvus_client.release_collection(collection_name=collection_name)
            milvus_client.drop_index(collection_name=collection_name, index_name='sparse_inverted_index')
            milvus_client.drop_index(collection_name=collection_name, index_name='dense_inverted_index')
            milvus_client.drop_collection(collection_name=collection_name)

        milvus_client.create_collection(
            collection_name=collection_name,
            schema=schema,
            index_params=index_params
        )

    def create_milvus(self, collection_name:str):
        self.milvus = Milvus(
            collection_name=collection_name,
            collection_description= "家具客服助手向量知识库",
            embedding_function=bge_embedding,  # 生成稠密向量(dense vector)的模型
            builtin_function= BM25BuiltInFunction(), #BM25稀疏向量函数
            vector_field=["dense", "sparse"],
            auto_id=True,
            consistency_level= "Strong",    # 数据一致性强 ， 可以选择用 Session，不保证强一致，但是当前对话会有返回
            connection_args = {
                "uri": settings.MILVUS_URI,
                "timeout": 60,  # 超时时间
                "pool_size": 5,  # 连接池
            }
        )

    # 新增文档
    @retry(delay=2)
    def add_documents(self, docs: List[Document]):
        self.milvus.add_documents(docs)
        log.info(f"文档新增完成,长度为:{len(docs)}")

if __name__ == '__main__':
    ms = MilvusVectorStore()
    ms.create_collection()