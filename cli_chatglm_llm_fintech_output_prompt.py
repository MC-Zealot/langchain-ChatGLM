# import os
# # os.environ['NUMEXPR_MAX_THREADS'] = '12'

import nltk

from configs.model_config import *
nltk.data.path = [NLTK_DATA_PATH] + nltk.data.path
from chains.local_doc_qa import LocalDocQA
import pandas as pd


from models.loader.args import parser
import models.shared as shared
from models.loader import LoaderCheckPoint


# Show reply with source text from input document
REPLY_WITH_SOURCE = True
import json
from datetime import datetime
import multiprocessing


'''
1.保存数据到向量库
2.读取向量库，并且开始回答问题
'''
class OutPutPrompts:
    print("========================")
    logger.info("begins")
    logger.info("logger config is done")
    print("========================")
    # llm_model_ins = shared.loaderLLM()
    # llm_model_ins.history_len = LLM_HISTORY_LEN


    logger.info("local_doc_qa init is done")
    def init_prompts(self, vs_path = "/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/faiss_vector_store_extract2"):
        local_doc_qa = LocalDocQA()
        local_doc_qa.init_cfg(llm_model=None,
                              embedding_model=EMBEDDING_MODEL,
                              embedding_device=EMBEDDING_DEVICE,
                              top_k=VECTOR_SEARCH_TOP_K)
        self.vs_path = vs_path
        self.local_doc_qa = local_doc_qa

    def execute_task(self, line):
        try:
            questions_dict = json.loads(line)
            questions_content = questions_dict['question']
            logger.info(str(datetime.now()) + "\t" + questions_content)
            query = questions_content
            prompt = self.local_doc_qa.get_prompt_based_query(query=query, vs_path=self.vs_path)

            questions_dict['question'] = str(prompt)
            ret = json.dumps(questions_dict, ensure_ascii=False)
            return ret
        except Exception as e:
            logger.info(e)
            logger.info(f"{line} 未能成功加载")

    def multi_run(self, filepath="/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/test_questions.json.100"):
        manager = multiprocessing.Manager()
        with open(filepath, "r") as f1:
            lines = f1.readlines()
            task_list = manager.list(lines)  # 共享的任务列表
            # 创建进程池
            pool = multiprocessing.Pool(1)
            # 使用进程池中的进程来执行共享的任务列表，并获取返回值
            results = pool.map_async(self.execute_task, task_list)
            # 等待所有任务执行完成
            results.wait()
            # 获取每个任务的返回值
            output = results.get()
            # print(output) # 打印输出结果
            # 关闭进程池
            pool.close()
            pool.join()
            f1.close()
        return output

    def single_run(self, filepath="/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/test_questions.json"):
        with open(filepath, "r") as f1:
            lines = f1.readlines()
            res =[]
            index = 0
            for line in lines:
                try:
                    questions_dict = json.loads(line)
                    questions_content = questions_dict['question']
                    logger.info(str(datetime.now()) + "\t" +str(index)+"\t"+ questions_content)
                    query = questions_content
                    prompt = self.local_doc_qa.get_prompt_based_query(query=query, vs_path=self.vs_path)

                    questions_dict['prompt'] = str(prompt)
                    tmp = json.dumps(questions_dict, ensure_ascii=False)
                    res.append(tmp)
                    index+=1
                except Exception as e:
                    logger.error(e)
                    logger.error(f"{line} 未能成功加载")
        return res



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
    # torch.multiprocessing.set_start_method('spawn')
    args = None
    args = parser.parse_args()
    args_dict = vars(args)
    shared.loaderCheckPoint = LoaderCheckPoint(args_dict)
    opp = OutPutPrompts()
    vs_path = "/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/faiss_vector_store_extract2" #向量库的路径
    input_filepath="/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/test_questions.json" #输入的比赛问题的路径
    output_path = "/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/test_prompts2.json" #输出的prompt的路径

    opp.init_prompts(vs_path)
    ret = opp.single_run(input_filepath)
    index = 0
    # exit(0)
    with open(output_path, "w", encoding="utf8") as f2:
        for line in ret:
            f2.write(str(line) + '\n')
            logger.error(str(datetime.now()) + "\t" + f"qestion {index} is prompted")

            index+=1
        f2.flush()
        f2.close()