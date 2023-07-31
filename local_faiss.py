from configs.model_config import *
from chains.local_doc_qa import LocalDocQA
from utils import torch_gc
from vectorstores import MyFAISS

vs_path = "/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/faiss_vector_store_tmp"
query="昭衍新药"
local_doc_qa = LocalDocQA()
local_doc_qa.init_cfg(llm_model=None,
                          embedding_model=EMBEDDING_MODEL,
                          embedding_device=EMBEDDING_DEVICE,
                          top_k=VECTOR_SEARCH_TOP_K)
vector_store = MyFAISS.load_local(vs_path, local_doc_qa.embeddings)
vector_store.chunk_size = local_doc_qa.chunk_size
vector_store.chunk_conent = False
vector_store.score_threshold = 800
related_docs_with_score = vector_store.similarity_search(query)
print(related_docs_with_score)
docs = vector_store.list_docs()
print(len(docs))
print(docs[0])
torch_gc()