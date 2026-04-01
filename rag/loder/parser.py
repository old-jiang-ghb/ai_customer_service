from typing import List
from langchain_core.documents import Document
from rag.loder.splitter import recursive_character_text_splitter
from rag.loder.loader import load_markdown_file
from utils.logger_utils import log

class MarkdownParser:
    def __init__(self):
        self.text_splitter = recursive_character_text_splitter

    def parse_markdown_to_document(self, file_path: str) -> List[Document]:
        log.info(f"开始解析md文件: {file_path}")
        # 加载文件并解析
        docs = load_markdown_file(file_path)
        log.info(f"加载文件原始长度为: {len(docs)}")
        # 合并数据(标题)
        merge_docs = self.merge_title_content(docs)
        log.info(f"合并后文件长度为: {len(merge_docs)}")
        # 语义切割数据
        docs = self.text_chunker(merge_docs)
        log.info(f"语义切割后文件长度为: {len(merge_docs)}")
        return docs

    def merge_title_content(self, datas: List[Document]) -> List[Document]:
        merged_data = []
        parent_dict = {}  # 是一个字典，保存所有的父document， key为当前父document的ID
        for document in datas:
            metadata = document.metadata
            # if 'languages' in metadata:
            #     metadata.pop('languages')

            parent_id = metadata.get('parent_id', None)
            category = metadata.get('category', None)
            element_id = metadata.get('element_id', None)

            # 是否为：内容document
            if category == 'NarrativeText' and parent_id is None:
                merged_data.append(document)
            # 如果是标题
            elif category == 'Title':
                document.metadata['title'] = document.page_content
                if parent_id in parent_dict:
                    document.page_content = parent_dict[parent_id].page_content + ' -> ' + document.page_content
                parent_dict[element_id] = document
            # 不是标题，且有父id
            elif parent_id:
                parent_dict[parent_id].page_content = parent_dict[parent_id].page_content + ' ' + document.page_content
                parent_dict[parent_id].metadata['category'] = 'content'

        # 处理字典
        if parent_dict is not None:
            merged_data.extend(parent_dict.values())

        return merged_data

    def text_chunker(self, datas: List[Document]) -> List[Document]:
        new_docs = []
        for d in datas:
            if len(d.page_content) > 3000:
                new_docs.extend(self.text_splitter.split_documents([d]))
                continue
            new_docs.append(d)
        return new_docs