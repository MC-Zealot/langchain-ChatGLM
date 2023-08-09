# import os
# # os.environ['NUMEXPR_MAX_THREADS'] = '12'

import nltk


from chains.local_doc_qa_index_name import LocalDocQA
import pandas as pd


from models.loader.args import parser
import models.shared as shared
from models.loader import LoaderCheckPoint


# Show reply with source text from input document
REPLY_WITH_SOURCE = True
import json
from datetime import datetime
import multiprocessing
from utils.utils import *
from configs.model_config import *
nltk.data.path = [NLTK_DATA_PATH] + nltk.data.path
from utils.utils import sort_sumbit_json


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
    def init_prompts(self, vs_path = None):
        local_doc_qa = LocalDocQA()
        local_doc_qa.init_cfg(llm_model=None,
                              embedding_model=EMBEDDING_MODEL,
                              embedding_device=EMBEDDING_DEVICE,
                              top_k=VECTOR_SEARCH_TOP_K)
        self.vs_path = vs_path
        self.local_doc_qa = local_doc_qa
        # self.stock_names = self.get_all_company_names()
        self.stock_names = local_doc_qa.company_names

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

    def get_year(self, query):
        which_year = "-1"
        if "2019" in query:
            which_year = "2019年"
        elif "2020" in query:
            which_year = "2020年"
        elif "2021" in query:
            which_year = "2021年"
        return which_year


    def get_all_company_names(self):
        stock_names = []
        with open("/home/zealot/yizhou/git/langchain-ChatGLM/all_company_short.txt", "r") as f:
            lines = f.readlines()
            for stock_mapping_one in lines:
                stock_name = stock_mapping_one.split("\t")[1]
                stock_names.append(stock_name)
            f.close()
        return stock_names

    def get_company(self, query):
        which_company = "-1"
        for stock_name in self.stock_names:
            full_name=stock_name.split('\t')[0]
            short_name=stock_name.split('\t')[1]
            if full_name in query or short_name in query:
                which_company = short_name
                break
        return which_company


    def single_run(self, filepath="/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/test_questions.json", type='specific', openmode='w'):
        with open(filepath, "r") as f1, open(output_path, openmode, encoding="utf8") as f2:
            lines = f1.readlines()
            index = 0
            for line in lines:
                try:
                    questions_dict = json.loads(line)
                    questions_content = questions_dict['question']
                    questions_id = questions_dict['id']
                    # logger.info(str(datetime.now()) + "\t" +str(index)+"\t"+ questions_content)
                    query = questions_content.replace('(','').replace(')','')
                    year = self.get_year(query)
                    company_name = self.get_company(query)
                    prompt=''
                    if company_name != '-1' and year != '-1':
                        # logger.info(year+"\t"+company_name)
                        index_name = company_name+year
                        # 判断vs_path对应的index_name是否存在，如果不存在，则换一个，
                        # 换哪个呢？换一个+1年的
                        year_int = int(year[0:4])
                        if not os.path.isfile(self.vs_path + "/"+index_name+".faiss"):
                            new_year = year_int + 1
                            index_name = company_name + str(new_year) +"年"
                            if new_year <=2021 and not os.path.isfile(self.vs_path + "/" + index_name + ".faiss"):
                                new_year = year_int + 2
                                index_name = company_name + str(new_year) + "年"
                        if not os.path.isfile(self.vs_path + "/" + index_name + ".faiss"):
                            if type =='generic':
                                vs_path_new='/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/faiss_vector_store_extract2'
                                index_name='index'
                                prompt = self.local_doc_qa.get_prompt_based_query(query=query, vs_path=vs_path_new, index_name=index_name, ori_query=query)
                        else:
                            if type =='specific':
                                filtered_query = replace_company_name_and_year_by_question(query, self.stock_names).replace("保留2位小数。", "").replace("保留两位小数。", "").replace("请保留两位小数。", "").replace("请以2位小数点形式回答。", "").replace("是多少元?", "").replace("是多少元？", "").replace("是多少?", "").replace("是多少?", "").replace("为多少?", "")
                                # filtered_query2 = replace_company_name_and_year_by_question(query, self.stock_names)
                                prompt = self.local_doc_qa.get_prompt_based_query(query=filtered_query, vs_path=self.vs_path, index_name=index_name, ori_query=query)
                    else:
                        if type == 'generic':
                            logger.error("找不到公司名称！！！！！！第{questions_id}题： {query}" + str(questions_id) + "\t" + str(query))
                            prompt=query
                    # print(prompt)
                    if len(prompt) == 0:
                        continue
                    questions_dict['prompt'] = str(prompt.replace('\n','。'))
                    tmp = json.dumps(questions_dict, ensure_ascii=False)
                    f2.write(str(tmp) + '\n')
                    # f2.write(str(prompt.replace('\n','')) + '\n')
                    if index % 500 == 0:
                        logger.error(str(datetime.now()) + "\t" + f"qestion {index} is prompted")
                    index+=1
                except Exception as e:
                    logger.error(e)
                    logger.error(f"{line} 未能成功加载")



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
    # vs_path = "/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/faiss_vector_store_extract_tmp" #向量库的路径
    vs_path = "/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/faiss_vector_store_index_name" #向量库的路径
    # input_filepath="/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/small_test/test_questions.json" #输入的比赛问题的路径
    input_filepath="/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/test_questions.json" #输入的比赛问题的路径
    output_path = "/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/small_test/20230809.json" #输出的prompt的路径
    # output_path = "/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/small_test/test_prompts_tmp.json" #输出的prompt的路径

    opp.init_prompts(vs_path)
    opp.single_run(filepath=input_filepath, type='specific',openmode='w')
    opp.single_run(filepath=input_filepath, type='generic',openmode='a')
    logger.info("output prompt done: ")
    sorted_output_path = sort_sumbit_json(output_path)
    logger.info(sorted_output_path)
    print(sorted_output_path)
    # exit(0)
    # with open(output_path, "w", encoding="utf8") as f2:
    #     for line in ret:
    #         f2.write(str(line) + '\n')
    #         logger.error(str(datetime.now()) + "\t" + f"qestion {index} is prompted")
    #
    #         index+=1
    #     f2.flush()
    #     f2.close()
