# import os
# # os.environ['NUMEXPR_MAX_THREADS'] = '12'
import nltk
from configs.model_config import *
from chains.local_doc_qa import LocalDocQA
import pandas as pd

from models.loader.args import parser
import models.shared as shared
from models.loader import LoaderCheckPoint
nltk.data.path = [NLTK_DATA_PATH] + nltk.data.path

# Show reply with source text from input document
REPLY_WITH_SOURCE = True
import json
from datetime import datetime
from utils.utils import *


'''
1.保存数据到向量库
2.读取向量库，并且开始回答问题
'''
def main():
    print("========================")
    logger.error("begins")
    logger.error("logger config is done")
    print("========================")
    llm_model_ins, llm = shared.loaderLLM_and_chain()
    llm_model_ins.history_len = LLM_HISTORY_LEN
    local_doc_qa = LocalDocQA()
    local_doc_qa.init_cfg(llm_model=llm_model_ins,
                          embedding_model=EMBEDDING_MODEL,
                          embedding_device=EMBEDDING_DEVICE,
                          top_k=VECTOR_SEARCH_TOP_K)
    # vs_path = "~/yizhou/git/ChatGLM2-6B_new/langchain/keda_FAISS_20230731_000944/vector_store"
    vs_path = "~/yizhou/git/chatglm_llm_fintech_raw_dataset/faiss_vector_store_extract"
    # vs_path = "/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/faiss_vector_store_v1"
    logger.error("local_doc_qa init is done")

    history = []
        # ret=[]
    index = 0
    with open("/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/test_prompts_v2.json", "r") as f1, \
        open('/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/submit_example_20230804_v2.json', 'w', encoding="utf8") as f2:
        lines = f1.readlines()
        for line in lines:
            questions_dict = json.loads(line)
            questions_content = questions_dict['prompt']
            questions_id = questions_dict['id']

            query = questions_content
            last_print_len = 0
            res=''
            for resp, history in local_doc_qa.get_answer_by_prompt(query=query,chat_history=history,streaming=STREAMING):
                # print(resp["result"][last_print_len:], end="", flush=True)
                res += resp["result"][last_print_len:]

                last_print_len = len(resp["result"])
                if last_print_len>3500:
                    break;

            print("res: ",res)
            questions_dict['answer']=str(res)
            del questions_dict['prompt']
            ret = json.dumps(questions_dict, ensure_ascii=False)
            f2.write(str(ret) + '\n')
            # ret.append(questions_dict)
            logger.error(str(datetime.now()) + "\t" + f"qestion {questions_id} is answered")
            f2.flush()
            index+=1
        f1.close()
        f2.close()


    # with open('~/yizhou/git/chatglm_llm_fintech_raw_dataset/submit_example.json.test', 'w', encoding="utf8") as f:
    #     for line in ret:
    #         ret = json.dumps(line, ensure_ascii=False)
    #         f.write(str(ret)+'\n')

if __name__ == "__main__":
#     # 通过cli.py调用cli_demo时需要在cli.py里初始化模型，否则会报错：
    # langchain-ChatGLM: error: unrecognized arguments: start cli
    # 为此需要先将
    # args = None
    # args = parser.parse_args()
    # args_dict = vars(args)
    # shared.loaderCheckPoint = LoaderCheckPoint(args_dict)
    # 语句从main函数里取出放到函数外部
    # 然后在cli.py里初始化
    args = None
    args = parser.parse_args()
    args_dict = vars(args)
    shared.loaderCheckPoint = LoaderCheckPoint(args_dict)
    main()
