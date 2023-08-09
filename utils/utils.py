import os
import json

stock_names = []
with open("/home/zealot/yizhou/git/langchain-ChatGLM/data_extract/6.txt", "r") as f:
    lines = f.readlines()
    for stock_mapping_one in lines:
        stock_name = stock_mapping_one.split("\t")[1]
        stock_names.append(stock_name)
    f.close()


def replace_company_name_and_year_by_question(question, stock_names):
    question = question.replace("在2020年的", "")
    question = question.replace("在2021年的", "")
    question = question.replace("在2019年的", "")
    question = question.replace("2019年的", "")
    question = question.replace("2020年的", "")
    question = question.replace("2021年的", "")
    question = question.replace("在2020年", "")
    question = question.replace("在2021年", "")
    question = question.replace("在2019年", "")
    question = question.replace("2019年", "")
    question = question.replace("2020年", "")
    question = question.replace("2021年", "")
    question = question.replace("2019", "")
    question = question.replace("2020", "")
    question = question.replace("2021", "")
    for stock_name_one in stock_names:
        stock_name_one=stock_name_one.replace('\n','')
        full_name=stock_name_one.split('\t')[0]
        short_name=stock_name_one.split('\t')[1]

        if full_name in question:
            # print(question)
            question = question.replace("在" + full_name, "")
            question = question.replace("在" + full_name + "的", "")
            question = question.replace(full_name + "股份有限公司", "")
            question = question.replace(full_name + "集团股份有限公司", "")
            question = question.replace(full_name + "科技股份有限公司", "")
            question = question.replace(full_name + "有限公司", "")
            question = question.replace(full_name + "股份有限公司的", "")
            question = question.replace(full_name + "智能控制股份有限公司", "")
            question = question.replace(full_name + "的", "")
            question = question.replace(full_name, "")
        elif short_name in question:
            question = question.replace("在" + short_name, "")
            question = question.replace("在" + short_name + "的", "")
            question = question.replace(short_name + "股份有限公司", "")
            question = question.replace(short_name + "集团股份有限公司", "")
            question = question.replace(short_name + "科技股份有限公司", "")
            question = question.replace(short_name + "有限公司", "")
            question = question.replace(short_name + "股份有限公司的", "")
            question = question.replace(short_name + "智能控制股份有限公司", "")
            question = question.replace(short_name + "的", "")
            question = question.replace(short_name, "")
        # else:
        #     print("没有公司名称")


    return question

def preprocess_promot(prompt):
    start_index = prompt.find("问题是：")
    end_index = len(prompt)
    query = prompt[start_index: end_index]
    query_new = replace_company_name_and_year_by_question(query, stock_names)
    return prompt[0: start_index] + query_new

def all_companys_output(output_path):
    filePath = '/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/alltxt'
    company_names = []
    for i, j, k in os.walk(filePath):
        # print(i, j, k)
        index = 0
        while index < len(k):
            company_name = k[index]
            # print(file_path)
            company_names.append(company_name.split("__")[1] + "\t" + company_name.split("__")[3])
            print(company_name.split("__")[1] + "\t" + company_name.split("__")[3])
            index += 1
        break  # 非递归
    print(len(company_names))
    print(company_names[0:10])
    company_names = set(company_names)
    with open(output_path, "w", encoding="utf8") as f2:
        for name in company_names:
            f2.write(str(name) + '\n')


def testcase_replace_company_name_and_year_by_question():
    prompt = "已知信息：。。广东奥飞数据科技股份有限公司2020年年度报告全文。广东奥飞数据科技股份有限公司。2020年年度报告。2021年03月。1。。广东奥飞数据科技股份有限公司2020年年度报告全文。第一节重要提示、目录和释义。公司董事会、监事会及董事、监事、高级管理人员保证年度报告内容的真实、准确、完整，不存在虚假记载、误导性陈述或者重大遗漏，并承担个别和连带的法律责任。。公司负责人冯康、主管会计工作负责人龚云峰及会计机构负责人(会计主管人员)林卫云声明：保证本年度报告中财务报告的真实、准确、完整。。所有董事均已出席了审�。�办法的议案》、《关于提请公司股东大会授权董事会办理公司2020年员工持股计划相关事宜的议案》，并披露了《广东奥飞数据科技股份有限公司2020年员工持股计划（草案）》、《广东奥飞数据科技股份有限公司2020年员工持股计划（草案）摘要》、《广东奥飞数据科技股份有限公司2020年员工持股计划管理办法》。。4、公司于2021年2月5日披露了《关于公司2020年员工持股计划实施进展公告》（公告编号：2021-023），由于员工自筹资金尚未到账及窗口期原因，公司2020年员工持股计划尚未购买公司股票。。公司需。。深圳市洲明科技股份有限公司2019年年度报告全文。证券代码：300232证券简称：洲明科技公告编号：2020-177。深圳市洲明科技股份有限公司。2019年年度报告。（更新后）。2020年09月。1。。深圳市洲明科技股份有限公司2019年年度报告全文。致尊敬的投资者：。时光如白驹过隙，转眼2019年就在时间的长河中飘荡而去，2020年扑面而来。。反过头来看2019年的时光，我们用汗水浇灌出一片郁郁葱葱的树林，也培育了很多萌发的种子，使我们的树林能够蓬勃生长，未来成长为一片茂盛的森林。。一、难忘2019年。2019年，洲明秉承着对研发创新始终如一的� 。。根据上述已知信息，简洁和专业的来回答用户的问题。如果无法从中得到答案，请说 “根据已知信息无法回答该问题” 或 “没有提供足够的相关信息”，不允许在答案中添加编造成分，答案请使用中文。 问题是：广东奥飞数据科技股份有限公司2019年证券简称是什么?"
    start_index = prompt.find("问题是：")
    end_index = len(prompt)
    query = prompt[start_index: end_index]
    query_new = replace_company_name_and_year_by_question(query, stock_names)
    prompt_new = prompt[0: start_index] + query_new
    print(prompt_new)


def by_score(t):
    return t[0]
def sort_sumbit_json(input_path):
    pre_path=input_path.split('.')[0]
    out_put_path=pre_path+"_sort.json"

    with open(input_path, "r") as f1, open(out_put_path, 'w', encoding="utf8") as f2:
        input_lines = f1.readlines()
        ret_list = []
        for line in input_lines:
            questions_dict = json.loads(line)
            questions_id = int(questions_dict['id'])
            ret_list.append([questions_id, line])

        L2 = sorted(ret_list, key=by_score, reverse=False)
        for line in L2:
            f2.write(str(line[1]))
        # print(ret_list[-10:])
        # print(L2[-10:])
    return out_put_path

if __name__ == "__main__":
    all_companys_output("/all_company_short.txt")