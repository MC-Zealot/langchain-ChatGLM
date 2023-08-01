import json
import os



def alter(file_old, file_new):
    """
    将替换的字符串写到一个新的文件中，然后将原文件删除，新文件改为原来文件的名字
    :param file: 文件路径
    :param old_str: 需要替换的字符串
    :param new_str: 替换的字符串
    :return: None
    """
    with open(file_old, "r", encoding="utf-8") as f1,open("%s" % file_new, "w", encoding="utf-8") as f2:
        for line in f1:
            try:
                questions_dict = json.loads(line)
            except Exception:
                print("error json: "+line)
            if 'inside' not in questions_dict:
                continue

            questions_content = questions_dict['inside']
            print(type(questions_content))
            f2.write(questions_content)
        f1.close()
        f2.close()

input_path="/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/alltxt_tmp/"
output_path="/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/alltxt_tmp_extract/"
# file_path="2020-04-10__福建福日电子股份有限公司__600203__福日电子__2019年__年度报告.txt"
# file_path_new="2020-04-10__福建福日电子股份有限公司__600203__福日电子__2019年__年度报告.txt.tmp"



filePath = input_path
file_list=[]
for i, j, k in os.walk(filePath):
    # print(i, j, k)
    index = 0
    while index < len(k):
        file_path=str(i)+"/"+k[index]
        print(str(index)+"\t"+file_path)
        file_name=k[index]
        file_list.append(file_path)
        alter(file_path, output_path + file_name)
        index+=1