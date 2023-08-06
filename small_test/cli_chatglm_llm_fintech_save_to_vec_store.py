# import os
# # os.environ['NUMEXPR_MAX_THREADS'] = '12'
import nltk
from configs.model_config import *
from chains.local_doc_qa_index_name import LocalDocQA
# import nltk
from models.loader.args import parser
import models.shared as shared
from models.loader import LoaderCheckPoint
nltk.data.path = [NLTK_DATA_PATH] + nltk.data.path
# Show reply with source text from input document
REPLY_WITH_SOURCE = True
from datetime import datetime





'''
1.保存数据到向量库
2.读取向量库，并且开始回答问题
'''
def start():
    print("========================")
    logger.info("begins")
    logger.info("logger config is done")
    print("========================")
    # llm_model_ins = shared.loaderLLM()
    # llm_model_ins.history_len = LLM_HISTORY_LEN
    local_doc_qa = LocalDocQA()
    local_doc_qa.init_cfg(llm_model=None,
                          embedding_model=EMBEDDING_MODEL,
                          embedding_device=EMBEDDING_DEVICE,
                          top_k=VECTOR_SEARCH_TOP_K)
    # vs_path = "~/yizhou/git/ChatGLM2-6B_new/langchain/keda_FAISS_20230731_000944/vector_store"
    a = datetime.now()

    vs_path = "/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/faiss_vector_store_index_name"
    # local_doc_qa.load_vector_store_by_vspath(vs_path)
    filePath = '/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/alltxt_extract_filtered_3000'
    file_list=[]
    for i, j, k in os.walk(filePath):
        # print(i, j, k)
        index = 0
        while index < len(k):
            file_path=str(i)+"/"+k[index]
            # print(file_path)
            file_list.append(file_path)
            index+=1
        break #非递归
    # print("file_list len: ", len(file_list))
    # exit(0)

    filepath = file_list
    # filepath错误的返回为None, 如果直接用原先的vs_path,_ = local_doc_qa.init_knowledge_vector_store(filepath)
    # 会直接导致TypeError: cannot unpack non-iterable NoneType object而使得程序直接退出
    # 因此需要先加一层判断，保证程序能继续运行
    local_doc_qa.init_knowledge_vector_store(filepath, vs_path)

    print(f"the loaded vs_path is 加载的vs_path为: {vs_path}")
    b = datetime.now()
    print("加载文件个数: "+str(len(file_list))+", 到数据库总耗时"+str((b-a).seconds))




if __name__ == "__main__":
    logger.info("begins1")
    args = None
    args = parser.parse_args()
    args_dict = vars(args)
    logger.info("begins2")
    shared.loaderCheckPoint = LoaderCheckPoint(args_dict)
    logger.info("begins3")
    start()
