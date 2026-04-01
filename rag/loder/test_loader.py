
from pathlib import Path
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from core import __BASE_DIR
# 测试加载数据

def load_file(filename: str):
    str = __BASE_DIR.__str__() + r'\dataes\md' + '\\' + filename
    loader = UnstructuredMarkdownLoader(file_path=str, mode= 'elements',strategy="fast")
    docs = []
    for doc in loader.lazy_load():
        docs.append(doc)
    print(docs)

if __name__ == '__main__':
    load_file('ask.md')