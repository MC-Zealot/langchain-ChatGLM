# import os
# # os.environ['NUMEXPR_MAX_THREADS'] = '12'

from configs.model_config import *
from chains.local_doc_qa import LocalDocQA

import nltk
from models.loader.args import parser
import models.shared as shared
from models.loader import LoaderCheckPoint
nltk.data.path = [NLTK_DATA_PATH] + nltk.data.path

# Show reply with source text from input document
REPLY_WITH_SOURCE = True



'''
1.保存数据到向量库
2.读取向量库，并且开始回答问题
'''
def main():
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
    # vs_path = "/home/zealot/yizhou/git/ChatGLM2-6B_new/langchain/keda_FAISS_20230731_000944/vector_store"
    vs_path = "/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/faiss_vector_store_v1"
    # local_doc_qa.load_vector_store_by_vspath(vs_path)
    filePath = '/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/alltxt_p1'
    file_list=[]
    for i, j, k in os.walk(filePath):
        # print(i, j, k)
        index = 0
        while index < len(k):
            file_path=str(i)+"/"+k[index]
            # print(file_path)
            file_list.append(file_path)
            index+=1
    # print("file_list len: ", len(file_list))
    # exit(0)

    filepath = file_list
    # filepath错误的返回为None, 如果直接用原先的vs_path,_ = local_doc_qa.init_knowledge_vector_store(filepath)
    # 会直接导致TypeError: cannot unpack non-iterable NoneType object而使得程序直接退出
    # 因此需要先加一层判断，保证程序能继续运行
    temp, loaded_files = local_doc_qa.init_knowledge_vector_store(filepath, vs_path)
    if temp is not None:
        vs_path = temp
        # 如果loaded_files和len(filepath)不一致，则说明部分文件没有加载成功
        # 如果是路径错误，则应该支持重新加载
        if len(loaded_files) != len(filepath):
            reload_flag = eval(input("部分文件加载失败，若提示路径不存在，可重新加载，是否重新加载，输入True或False: "))
            print("len(loaded_files): ", len(loaded_files))
            print("len(filepath): ", len(filepath))
            if reload_flag:
                vs_path = None
                exit(0)

        print(f"the loaded vs_path is 加载的vs_path为: {vs_path}")
    else:
        print("load file failed, re-input your local knowledge file path 请重新输入本地知识文件路径")




    # while not vs_path:
    #     print("注意输入的路径是完整的文件路径，例如knowledge_base/`knowledge_base_id`/content/file.md，多个路径用英文逗号分割")
    #     filepath = input("Input your local knowledge file path 请输入本地知识文件路径：")
    #
    #     # 判断 filepath 是否为空，如果为空的话，重新让用户输入,防止用户误触回车
    #     if not filepath:
    #         continue
    #
    #     # 支持加载多个文件
    #     filepath = filepath.split(",")
    #     # filepath错误的返回为None, 如果直接用原先的vs_path,_ = local_doc_qa.init_knowledge_vector_store(filepath)
    #     # 会直接导致TypeError: cannot unpack non-iterable NoneType object而使得程序直接退出
    #     # 因此需要先加一层判断，保证程序能继续运行
    #     temp,loaded_files = local_doc_qa.init_knowledge_vector_store(filepath)
    #     if temp is not None:
    #         vs_path = temp
    #         # 如果loaded_files和len(filepath)不一致，则说明部分文件没有加载成功
    #         # 如果是路径错误，则应该支持重新加载
    #         if len(loaded_files) != len(filepath):
    #             reload_flag = eval(input("部分文件加载失败，若提示路径不存在，可重新加载，是否重新加载，输入True或False: "))
    #             if reload_flag:
    #                 vs_path = None
    #                 continue
    #
    #         print(f"the loaded vs_path is 加载的vs_path为: {vs_path}")
    #     else:
    #         print("load file failed, re-input your local knowledge file path 请重新输入本地知识文件路径")




    # history = []
    # while True:
    #     query = input("Input your question 请输入问题：")
    #     last_print_len = 0
    #     for resp, history in local_doc_qa.get_knowledge_based_answer(query=query,
    #                                                                  vs_path=vs_path,
    #                                                                  chat_history=history,
    #                                                                  streaming=STREAMING):
    #         if STREAMING:
    #             print(resp["result"][last_print_len:], end="", flush=True)
    #             last_print_len = len(resp["result"])
    #         else:
    #             print(resp["result"])
    #     if REPLY_WITH_SOURCE:
    #         source_text = [f"""出处 [{inum + 1}] {os.path.split(doc.metadata['source'])[-1]}：\n\n{doc.page_content}\n\n"""
    #                        # f"""相关度：{doc.metadata['score']}\n\n"""
    #                        for inum, doc in
    #                        enumerate(resp["source_documents"])]
    #         print("\n\n" + "\n\n".join(source_text))


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
