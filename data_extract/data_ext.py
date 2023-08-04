import json

test_questions = open("/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/test_questions.jsonl").readlines()
question_2020 = []
DATE_STR='2019'
for test_question in test_questions:
    question = json.loads(test_question)["question"]
    if DATE_STR in question:
        question_2020.append(question)

stock_names = []

with open("6.txt", "r") as f:
    lines = f.readlines()
    for stock_mapping_one in lines:
        stock_name = stock_mapping_one.split("\t")[1]
        stock_names.append(stock_name)
    f.close()

quetion_cls = {}
company_names=set()
# def is_hit(question_2020, stock_names):
#     flag = False
#     for stock_name_one in stock_names:
#         if stock_name_one in question_2020:
#             flag = True
#     return flag
#
#
# for question in test_questions:
#     flag = is_hit(question, stock_names)
#     if not flag:
#         print(question)
#
# exit(0)
questions_not_hit=[]
for question_2020_one in question_2020:
    is_hit_flag=False
    for stock_name_one in stock_names:
        if stock_name_one in question_2020_one:
            is_hit_flag=True
            # print(question_2020_one)
            question_2020_one = question_2020_one.replace("在"+DATE_STR+"年的", "<year>")
            question_2020_one = question_2020_one.replace("2020年的", "<year>")

            question_2020_one = question_2020_one.replace("在"+DATE_STR+"年", "<year>")
            question_2020_one = question_2020_one.replace(DATE_STR+"年", "<year>")
            question_2020_one = question_2020_one.replace(DATE_STR, "<year>")
            question_2020_one = question_2020_one.replace("在" + stock_name_one, "<company>")
            question_2020_one = question_2020_one.replace("在" + stock_name_one + "的", "<company>")
            question_2020_one = question_2020_one.replace(stock_name_one + "股份有限公司", "<company>")
            question_2020_one = question_2020_one.replace(stock_name_one + "集团股份有限公司", "<company>")
            question_2020_one = question_2020_one.replace(stock_name_one + "科技股份有限公司", "<company>")
            question_2020_one = question_2020_one.replace(stock_name_one + "有限公司", "<company>")
            question_2020_one = question_2020_one.replace(stock_name_one + "股份有限公司的", "<company>")
            question_2020_one = question_2020_one.replace(stock_name_one + "智能控制股份有限公司", "<company>")
            question_2020_one = question_2020_one.replace(stock_name_one + "的", "<company>")
            question_2020_one = question_2020_one.replace(stock_name_one, "<company>")
            question_2020_one = question_2020_one.replace("保留2位小数。", "<ask>")
            question_2020_one = question_2020_one.replace("保留两位小数。", "<ask>")
            question_2020_one = question_2020_one.replace("请保留两位小数。", "<ask>")
            question_2020_one = question_2020_one.replace("请以2位小数点形式回答。", "<ask>")
            question_2020_one = question_2020_one.replace("是多少元?", "<money>")
            question_2020_one = question_2020_one.replace("是多少元？", "<money>")
            question_2020_one = question_2020_one.replace("是多少?", "<how>")
            question_2020_one = question_2020_one.replace("是多少?", "<how>")
            question_2020_one = question_2020_one.replace("为多少?", "<how>")
            question_2020_one = question_2020_one.replace("<company><year>", "<year><company>")

            # print(question_2020_one)
            if question_2020_one in quetion_cls:
                quetion_cls[question_2020_one] = quetion_cls[question_2020_one] + 1
            else:
                quetion_cls[question_2020_one] = 1
    if is_hit_flag == False:
        questions_not_hit.append(question_2020_one)

a = sorted(quetion_cls.items(), key=lambda x: x[1], reverse=True)
# print(a)
index = 0
for  val in a:
    if index == 50:
        break
    print(val)
    index+=1

print("==================================================================")
for q in questions_not_hit:
    print(q)
print(len(questions_not_hit))