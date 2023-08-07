from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from vectorstores import MyFAISS
from langchain.document_loaders import UnstructuredFileLoader, TextLoader, CSVLoader, DirectoryLoader

from datetime import datetime
from textsplitter import ChineseTextSplitter, AliTextSplitter
from langchain.text_splitter import TokenTextSplitter
from typing import List
from utils import torch_gc
from tqdm import tqdm
from pypinyin import lazy_pinyin
from models.base import (BaseAnswer,
                         AnswerResult)
from models.loader.args import parser
from models.loader import LoaderCheckPoint
import models.shared as shared
from agent import bing_search
from langchain.docstore.document import Document
from functools import lru_cache
from textsplitter.zh_title_enhance import zh_title_enhance
from langchain.chains.base import Chain
import multiprocessing
from configs.model_config import *



# patch HuggingFaceEmbeddings to make it hashable
def _embeddings_hash(self):
    return hash(self.model_name)


HuggingFaceEmbeddings.__hash__ = _embeddings_hash


# will keep CACHED_VS_NUM of vector store caches
@lru_cache(CACHED_VS_NUM)
def load_vector_store(vs_path, embeddings):
    return MyFAISS.load_local(vs_path, embeddings)

@lru_cache(CACHED_VS_NUM)
def load_vector_store_by_index_name(vs_path, embeddings, index_name):
    return MyFAISS.load_local(vs_path, embeddings, index_name)

@lru_cache(CACHED_VS_NUM)
def load_vector_store_milvus(vs_path, embeddings):
    return MyFAISS.load_local(vs_path, embeddings)


def tree(filepath, ignore_dir_names=None, ignore_file_names=None):
    """返回两个列表，第一个列表为 filepath 下全部文件的完整路径, 第二个为对应的文件名"""
    if ignore_dir_names is None:
        ignore_dir_names = []
    if ignore_file_names is None:
        ignore_file_names = []
    ret_list = []
    if isinstance(filepath, str):
        if not os.path.exists(filepath):
            print("路径不存在")
            return None, None
        elif os.path.isfile(filepath) and os.path.basename(filepath) not in ignore_file_names:
            return [filepath], [os.path.basename(filepath)]
        elif os.path.isdir(filepath) and os.path.basename(filepath) not in ignore_dir_names:
            for file in os.listdir(filepath):
                fullfilepath = os.path.join(filepath, file)
                if os.path.isfile(fullfilepath) and os.path.basename(fullfilepath) not in ignore_file_names:
                    ret_list.append(fullfilepath)
                if os.path.isdir(fullfilepath) and os.path.basename(fullfilepath) not in ignore_dir_names:
                    ret_list.extend(tree(fullfilepath, ignore_dir_names, ignore_file_names)[0])
    return ret_list, [os.path.basename(p) for p in ret_list]


def load_file(filepath, sentence_size=SENTENCE_SIZE, using_zh_title_enhance=ZH_TITLE_ENHANCE):
    start_index=filepath.find('__') + 2
    end_index=len(filepath) - 10
    file_name=filepath[start_index:end_index]
    if filepath.lower().endswith(".md"):
        loader = UnstructuredFileLoader(filepath, mode="elements")
        docs = loader.load()
    elif filepath.lower().endswith(".txt"):
        # loader = TextLoader(filepath, autodetect_encoding=True)
        # textsplitter = ChineseTextSplitter(pdf=False, sentence_size=sentence_size)
        # docs = loader.load_and_split(textsplitter)
        loader = TextLoader(filepath)
        # 将数据转成 document 对象，每个文件会作为一个 document
        documents = loader.load()
        # text_splitter = CharacterTextSplitter(separator='\n', chunk_size=sentence_size, chunk_overlap=0)
        text_splitter = TokenTextSplitter(chunk_size=sentence_size, chunk_overlap=0)
        docs = text_splitter.split_documents(documents)
        # docs = text_splitter.split_documents_v2(documents, file_name)

    elif filepath.lower().endswith(".pdf"):
        # 暂且将paddle相关的loader改为动态加载，可以在不上传pdf/image知识文件的前提下使用protobuf=4.x
        from loader import UnstructuredPaddlePDFLoader
        loader = UnstructuredPaddlePDFLoader(filepath)
        textsplitter = ChineseTextSplitter(pdf=True, sentence_size=sentence_size)
        docs = loader.load_and_split(textsplitter)
    elif filepath.lower().endswith(".jpg") or filepath.lower().endswith(".png"):
        # 暂且将paddle相关的loader改为动态加载，可以在不上传pdf/image知识文件的前提下使用protobuf=4.x
        from loader import UnstructuredPaddleImageLoader
        loader = UnstructuredPaddleImageLoader(filepath, mode="elements")
        textsplitter = ChineseTextSplitter(pdf=False, sentence_size=sentence_size)
        docs = loader.load_and_split(text_splitter=textsplitter)
    elif filepath.lower().endswith(".csv"):
        loader = CSVLoader(filepath)
        docs = loader.load()
    else:
        loader = UnstructuredFileLoader(filepath, mode="elements")
        textsplitter = ChineseTextSplitter(pdf=False, sentence_size=sentence_size)
        docs = loader.load_and_split(text_splitter=textsplitter)
    if using_zh_title_enhance:
        docs = zh_title_enhance(docs)
    # write_check_file(filepath, docs)
    return docs


def write_check_file(filepath, docs):
    folder_path = os.path.join(os.path.dirname(filepath), "tmp_files")
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    fp = os.path.join(folder_path, 'load_file.txt')
    with open(fp, 'a+', encoding='utf-8') as fout:
        fout.write("filepath=%s,len=%s" % (filepath, len(docs)))
        fout.write('\n')
        for i in docs:
            fout.write(str(i))
            fout.write('\n')
        fout.close()


def generate_prompt(related_docs: List[str],
                    query: str,
                    prompt_template: str = PROMPT_TEMPLATE, ) -> str:
    context = "\n".join([doc.page_content for doc in related_docs])
    prompt = prompt_template.replace("{question}", query).replace("{context}", context)
    return prompt

def generate_prompt_v2(related_docs: List[str],
                    query: str,
                    prompt_template: str = PROMPT_TEMPLATE_V2, ) -> str:
    context = "\n".join([doc.page_content for doc in related_docs])
    prompt = prompt_template.replace("{question}", query).replace("{context}", context)
    return prompt


def search_result2docs(search_results):
    docs = []
    for result in search_results:
        doc = Document(page_content=result["snippet"] if "snippet" in result.keys() else "",
                       metadata={"source": result["link"] if "link" in result.keys() else "",
                                 "filename": result["title"] if "title" in result.keys() else ""})
        docs.append(doc)
    return docs


class LocalDocQA:
    llm_model_chain: Chain = None
    embeddings: object = None
    top_k: int = VECTOR_SEARCH_TOP_K
    chunk_size: int = CHUNK_SIZE
    chunk_conent: bool = False
    score_threshold: int = VECTOR_SEARCH_SCORE_THRESHOLD

    def init_cfg(self,
                 embedding_model: str = EMBEDDING_MODEL,
                 embedding_device=EMBEDDING_DEVICE,
                 llm_model: Chain = None,
                 top_k=VECTOR_SEARCH_TOP_K,
                 ):
        self.llm_model_chain = llm_model
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model_dict[embedding_model], model_kwargs={'device': embedding_device})
        self.top_k = top_k
        self.company_names = self.init_company_names()

    def init_company_names(self):
        ret_names=[]
        company_file="/home/zealot/yizhou/git/langchain-ChatGLM/all_company_short.txt"
        with open(company_file, "r", encoding="utf-8") as f1:
            for line in f1:
                ret_names.append(line.replace('\n',''))
        return ret_names

    def init_knowledge_vector_store(self, filepath: str or List[str], vs_path: str or os.PathLike = None, sentence_size=SENTENCE_SIZE):
        failed_files = []
        file=''
        if isinstance(filepath, str):
            if not os.path.exists(filepath):
                print("路径不存在")
                return None
            elif os.path.isfile(filepath):
                file = os.path.split(filepath)[-1]
                try:
                    docs = load_file(filepath, sentence_size)
                    logger.error(f"{file} 已成功加载")
                    # loaded_files.append(filepath)
                except Exception as e:
                    logger.error(e)
                    logger.error(f"{file} 未能成功加载")
                    return None
            elif os.path.isdir(filepath):
                docs = []
                for fullfilepath, file in tqdm(zip(*tree(filepath, ignore_dir_names=['tmp_files'])), desc="加载文件"):
                    try:
                        docs += load_file(fullfilepath, sentence_size)
                        # loaded_files.append(fullfilepath)
                    except Exception as e:
                        logger.error(e)
                        failed_files.append(file)

                if len(failed_files) > 0:
                    logger.error("以下文件未能成功加载：")
                    for file in failed_files:
                        logger.error(f"{file}\n")

        else:
            docs = []
            # self.multi_run(filepath, vs_path)
            for file_path in filepath:
                if "太保" in file_path:
                    print(file_path)
                self.execute_task(file_path, vs_path)


    def save_vector_store(self, vs_path, file, docs):
        if vs_path and os.path.isdir(vs_path) and "index.faiss" in os.listdir(vs_path):
            vector_store = load_vector_store(vs_path, self.embeddings)
            vector_store.add_documents(docs)
            torch_gc()
        else:
            if not vs_path:
                vs_path = os.path.join(KB_ROOT_PATH,
                                       f"""{"".join(lazy_pinyin(os.path.splitext(file)[0]))}_FAISS_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}""",
                                       "vector_store")

            # 分批处理文本，应对大文本一次性处理导致进程终止的问题
            # logger.error("docs len: " + str(len(docs)))
            file_company_name=file.split("__")[1]
            for name in self.company_names:
                full_name = name.split('\t')[0]
                short_name = name.split('\t')[1]
                if full_name in file_company_name or short_name in file_company_name:
                    file_company_name = short_name
                    break
            index_name=file_company_name + file.split("__")[4]
            vector_store = MyFAISS.from_documents(docs, self.embeddings)
            vector_store.save_local(vs_path, index_name)

        return vector_store

    def one_knowledge_add(self, vs_path, one_title, one_conent, one_content_segmentation, sentence_size):
        try:
            if not vs_path or not one_title or not one_conent:
                logger.error("知识库添加错误，请确认知识库名字、标题、内容是否正确！")
                return None, [one_title]
            docs = [Document(page_content=one_conent + "\n", metadata={"source": one_title})]
            if not one_content_segmentation:
                text_splitter = ChineseTextSplitter(pdf=False, sentence_size=sentence_size)
                docs = text_splitter.split_documents(docs)
            if os.path.isdir(vs_path) and os.path.isfile(vs_path + "/index.faiss"):
                vector_store = load_vector_store(vs_path, self.embeddings)
                vector_store.add_documents(docs)
            else:
                vector_store = MyFAISS.from_documents(docs, self.embeddings)  ##docs 为Document列表
            torch_gc()
            vector_store.save_local(vs_path)
            return vs_path, [one_title]
        except Exception as e:
            logger.error(e)
            return None, [one_title]

    def get_knowledge_based_answer(self, query, vs_path, chat_history=[], streaming: bool = STREAMING):
        vector_store = load_vector_store(vs_path, self.embeddings)
        vector_store.chunk_size = self.chunk_size
        vector_store.chunk_conent = self.chunk_conent
        vector_store.score_threshold = self.score_threshold
        related_docs_with_score = vector_store.similarity_search_with_score(query, k=self.top_k)
        torch_gc()
        if len(related_docs_with_score) > 0:
            prompt = generate_prompt(related_docs_with_score, query)
        else:
            prompt = query

        answer_result_stream_result = self.llm_model_chain(
            {"prompt": prompt, "history": chat_history, "streaming": streaming})

        for answer_result in answer_result_stream_result['answer_result_stream']:
            resp = answer_result.llm_output["answer"]
            history = answer_result.history
            history[-1][0] = query
            response = {"query": query,
                        "result": resp,
                        "source_documents": related_docs_with_score}
            yield response, history

    def get_knowledge_based_answer_v2(self, query, vs_path, chat_history=[], streaming: bool = STREAMING):
        vector_store = load_vector_store(vs_path, self.embeddings)
        vector_store.chunk_size = self.chunk_size
        vector_store.chunk_conent = self.chunk_conent
        vector_store.score_threshold = self.score_threshold
        related_docs_with_score = vector_store.similarity_search_with_score(query, k=self.top_k)
        torch_gc()
        if len(related_docs_with_score) > 0:
            prompt = generate_prompt(related_docs_with_score, query)
        else:
            prompt = query

        answer_result_stream_result = self.llm_model_chain({"prompt": prompt, "history": chat_history, "streaming": streaming})

        for answer_result in answer_result_stream_result['answer_result_stream']:
            resp = answer_result.llm_output["answer"]
            # history = answer_result.history
            # history[-1][0] = query
            response = {"query": '',
                        "result": resp,
                        "source_documents": ''}
            yield response

    def get_answer_by_prompt(self, query, chat_history=[], streaming: bool = STREAMING):
        answer_result_stream_result = self.llm_model_chain({"prompt": query, "history": chat_history, "streaming": streaming})

        for answer_result in answer_result_stream_result['answer_result_stream']:
            resp = answer_result.llm_output["answer"]

            history = answer_result.history
            history[-1][0] = query
            response = {"query": '',
                        "result": resp,
                        "source_documents": ''}
            yield response, history

    def get_prompt_based_query(self, query, vs_path, index_name):

        vector_store = load_vector_store_by_index_name(vs_path, self.embeddings, index_name)
        vector_store.chunk_size = self.chunk_size
        vector_store.chunk_conent = self.chunk_conent
        vector_store.score_threshold = self.score_threshold
        related_docs_with_score = vector_store.similarity_search_with_score(query, k=self.top_k)
        torch_gc()
        if len(related_docs_with_score) > 0:
            prompt = generate_prompt_v2(related_docs_with_score, query)
        else:
            prompt = query

        return prompt

    # query      查询内容
    # vs_path    知识库路径
    # chunk_conent   是否启用上下文关联
    # score_threshold    搜索匹配score阈值
    # vector_search_top_k   搜索知识库内容条数，默认搜索5条结果
    # chunk_sizes    匹配单段内容的连接上下文长度
    def get_knowledge_based_conent_test(self, query, vs_path, chunk_conent,
                                        score_threshold=VECTOR_SEARCH_SCORE_THRESHOLD,
                                        vector_search_top_k=VECTOR_SEARCH_TOP_K, chunk_size=CHUNK_SIZE):
        vector_store = load_vector_store(vs_path, self.embeddings)
        # FAISS.similarity_search_with_score_by_vector = similarity_search_with_score_by_vector
        vector_store.chunk_conent = chunk_conent
        vector_store.score_threshold = score_threshold
        vector_store.chunk_size = chunk_size
        related_docs_with_score = vector_store.similarity_search_with_score(query, k=vector_search_top_k)
        if not related_docs_with_score:
            response = {"query": query,
                        "source_documents": []}
            return response, ""
        torch_gc()
        prompt = "\n".join([doc.page_content for doc in related_docs_with_score])
        response = {"query": query,
                    "source_documents": related_docs_with_score}
        return response, prompt

    def get_search_result_based_answer(self, query, chat_history=[], streaming: bool = STREAMING):
        results = bing_search(query)
        result_docs = search_result2docs(results)
        prompt = generate_prompt(result_docs, query)

        answer_result_stream_result = self.llm_model_chain(
            {"prompt": prompt, "history": chat_history, "streaming": streaming})

        for answer_result in answer_result_stream_result['answer_result_stream']:
            resp = answer_result.llm_output["answer"]
            history = answer_result.history
            history[-1][0] = query
            response = {"query": query,
                        "result": resp,
                        "source_documents": result_docs}
            yield response, history

    def delete_file_from_vector_store(self,
                                      filepath: str or List[str],
                                      vs_path):
        vector_store = load_vector_store(vs_path, self.embeddings)
        status = vector_store.delete_doc(filepath)
        return status

    def update_file_from_vector_store(self,
                                      filepath: str or List[str],
                                      vs_path,
                                      docs: List[Document], ):
        vector_store = load_vector_store(vs_path, self.embeddings)
        status = vector_store.update_doc(filepath, docs)
        return status

    def list_file_from_vector_store(self,
                                    vs_path,
                                    fullpath=False):
        vector_store = load_vector_store(vs_path, self.embeddings)
        docs = vector_store.list_docs()
        if fullpath:
            return docs
        else:
            return [os.path.split(doc)[-1] for doc in docs]

    def load_vector_store_by_vspath(self,
                                    vs_path):
        vector_store = load_vector_store(vs_path, self.embeddings)
        return vector_store

    def get_knowledge_based_answer_test(self, query, vs_path, chat_history=[], streaming: bool = STREAMING):
        vector_store = load_vector_store(vs_path, self.embeddings)
        vector_store.chunk_size = self.chunk_size
        vector_store.chunk_conent = self.chunk_conent
        vector_store.score_threshold = self.score_threshold
        related_docs_with_score = vector_store.similarity_search_with_score(query, k=self.top_k)
        torch_gc()

    def execute_task(self, file, vs_path):
        # vs_path = "/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/faiss_vector_store_extract_tmp"


        file_company_name = file.split("__")[1]
        for name in self.company_names:
            full_name = name.split('\t')[0]
            short_name = name.split('\t')[1]
            if full_name in file_company_name or short_name in file_company_name:
                file_company_name = short_name
                break
        index_name = file_company_name + file.split("__")[4]
        filepath=vs_path+'/'+index_name+'.faiss'
        if os.path.isfile(filepath):
            logger.error("faiss库以存在！"+str(filepath))
            return
        try:
            docs = load_file(file)
            # print(f"{file} 已成功加载123....")
            # logger.error(f"{file} 已成功加载1233")
            if len(docs) > 0:
                logger.error(str(datetime.now()) + "\t" + "文件加载完毕，正在生成向量库")

                self.save_vector_store(vs_path, file, docs)
                # vector_store.save_local(vs_path)
            return True
        except Exception as e:
            logger.error(e)
            logger.error(f"{file} 未能成功加载")

    def multi_run(self, filepath, vs_path):
        manager = multiprocessing.Manager()
        task_list = manager.list(filepath)  # 共享的任务列表
        # 创建进程池
        pool = multiprocessing.Pool(1)
        # 使用进程池中的进程来执行共享的任务列表，并获取返回值
        pool.map_async(self.execute_task, task_list)
        # 等待所有任务执行完成
        # results.wait()
        # 获取每个任务的返回值
        # output = results.get()
        # print(output) # 打印输出结果
        # 关闭进程池
        pool.close()
        pool.join()
        # return output


if __name__ == "__main__":
    # 初始化消息
    args = None
    args = parser.parse_args(args=['--model-dir', '/media/checkpoint/', '--model', 'chatglm-6b', '--no-remote-model'])

    args_dict = vars(args)
    shared.loaderCheckPoint = LoaderCheckPoint(args_dict)
    llm_model_ins = shared.loaderLLM()

    local_doc_qa = LocalDocQA()
    local_doc_qa.init_cfg(llm_model=llm_model_ins)
    query = "本项目使用的embedding模型是什么，消耗多少显存"
    vs_path = "/media/gpt4-pdf-chatbot-langchain/dev-langchain-ChatGLM/vector_store/test"
    last_print_len = 0
    # for resp, history in local_doc_qa.get_knowledge_based_answer(query=query,
    #                                                              vs_path=vs_path,
    #                                                              chat_history=[],
    #                                                              streaming=True):
    for resp, history in local_doc_qa.get_search_result_based_answer(query=query,
                                                                     chat_history=[],
                                                                     streaming=True):
        print(resp["result"][last_print_len:], end="", flush=True)
        last_print_len = len(resp["result"])
    source_text = [f"""出处 [{inum + 1}] {doc.metadata['source'] if doc.metadata['source'].startswith("http")
    else os.path.split(doc.metadata['source'])[-1]}：\n\n{doc.page_content}\n\n"""
                   # f"""相关度：{doc.metadata['score']}\n\n"""
                   for inum, doc in
                   enumerate(resp["source_documents"])]
    logger.error("\n\n" + "\n\n".join(source_text))
    pass
