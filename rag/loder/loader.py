from langchain_community.document_loaders import UnstructuredMarkdownLoader
from typing import List
from langchain_core.documents import Document

# 加载markdown文档
def load_markdown_file(file_path: str) -> List[Document]:
    loader = UnstructuredMarkdownLoader(file_path=file_path, mode='elements', strategy="fast")
    docs = []
    for doc in loader.lazy_load():
        docs.append(doc)
    return docs