from langchain_experimental.text_splitter import SemanticChunker

from langchain.text_splitter import RecursiveCharacterTextSplitter

from rag.embeddings.embedding import openai_embedding

# 本地语义分割，速度会快一些
recursive_character_text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,        # 每块大小（企业常用 500~1000）
    chunk_overlap=200,      # 重叠区（保证上下文不丢失）
    length_function=len,    # 按长度切
    separators=[
        "\n\n",    # 段落
        "\n",      # 换行
        "。",      # 中文句子
        "！",
        "？",
        " ",       # 空格
        ""         # 最后按字符切
    ]
)

# 高级语义分割，速度会慢一些
semantic_chunker = SemanticChunker(embeddings= openai_embedding)