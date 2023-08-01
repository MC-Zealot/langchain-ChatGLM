from langchain.vectorstores import Milvus
from langchain.vectorstores.base import VectorStore
from langchain.vectorstores.faiss import dependable_faiss_import
from typing import Any, Callable, List, Dict
from langchain.docstore.base import Docstore
from langchain.docstore.document import Document
import numpy as np
import copy
import os
from configs.model_config import *


class MyMilvus(Milvus, VectorStore):
    def __init__(
            self,
            embedding_function: Callable,
            index: Any,
            docstore: Docstore,
            index_to_docstore_id: Dict[int, str],
            normalize_L2: bool = False,
    ):
        super().__init__(embedding_function=embedding_function,
                         index=index,
                         docstore=docstore,
                         index_to_docstore_id=index_to_docstore_id,
                         normalize_L2=normalize_L2)
        self.score_threshold=VECTOR_SEARCH_SCORE_THRESHOLD
        self.chunk_size = CHUNK_SIZE
        self.chunk_conent = False

    def delete_doc(self, source: str or List[str]):
        try:
            if isinstance(source, str):
                ids = [k for k, v in self.docstore._dict.items() if v.metadata["source"] == source]
                vs_path = os.path.join(os.path.split(os.path.split(source)[0])[0], "vector_store")
            else:
                ids = [k for k, v in self.docstore._dict.items() if v.metadata["source"] in source]
                vs_path = os.path.join(os.path.split(os.path.split(source[0])[0])[0], "vector_store")
            if len(ids) == 0:
                return f"docs delete fail"
            else:
                for id in ids:
                    index = list(self.index_to_docstore_id.keys())[list(self.index_to_docstore_id.values()).index(id)]
                    self.index_to_docstore_id.pop(index)
                    self.docstore._dict.pop(id)
                # TODO: 从 self.index 中删除对应id
                # self.index.reset()
                self.save_local(vs_path)
                return f"docs delete success"
        except Exception as e:
            print(e)
            return f"docs delete fail"

    def update_doc(self, source, new_docs):
        try:
            delete_len = self.delete_doc(source)
            ls = self.add_documents(new_docs)
            return f"docs update success"
        except Exception as e:
            print(e)
            return f"docs update fail"

    def list_docs(self):
        return list(set(v.metadata["source"] for v in self.docstore._dict.values()))
