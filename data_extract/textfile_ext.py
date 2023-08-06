import json
import os


content_count={}


def cal_content_count_by_file(file_old):
    """
    将替换的字符串写到一个新的文件中，然后将原文件删除，新文件改为原来文件的名字
    :param file: 文件路径
    :param old_str: 需要替换的字符串
    :param new_str: 替换的字符串
    :return: None
    """
    with (open(file_old, "r", encoding="utf-8") as f1):
        tmp_content=''
        for line in f1:
            try:
                questions_dict = json.loads(line)
            except Exception:
                print("error json: "+line)
            if 'inside' not in questions_dict:
                continue

            questions_content = questions_dict['inside']
            if len(questions_content) == 0:
                continue
            tmp_content += (questions_content +'\n')
            if questions_content[-1] =='。':
                if tmp_content in content_count:
                    content_count[tmp_content] += 1
                else:
                    content_count[tmp_content] = 1
                tmp_content=''

        f1.close()


def cal_content_count(input_path, top_k):
    a=os.walk(input_path)
    file_list = []
    for i, j, k in os.walk(input_path):
        # print(i, j, k)
        index = 0
        while index < len(k):
            file_path = str(i) + "/" + k[index]
            # print(str(index) + "\t" + file_path)
            # file_name = k[index]
            file_list.append(file_path)
            cal_content_count_by_file(file_path)
            index += 1

    sorted_content_count = sorted(content_count.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    index = 0
    for val in sorted_content_count:
        if index == top_k:
            break
        print(str(index) + '\t' + str(val))
        index += 1

if __name__ == '__main__':
    input_path="/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/alltxt/"
    output_path="/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/alltxt_extract_filtered/"
    top_k = 1000
    cal_content_count(input_path, top_k)