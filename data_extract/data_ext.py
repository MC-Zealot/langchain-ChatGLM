import json

test_questions = open("/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/test_questions.jsonl").readlines()
question_2020 = []
for test_question in test_questions:
    question = json.loads(test_question)["question"]
    if "2020" in question:
        question_2020.append(question)

stock_names = []

with open("mapping.txt", "r") as f:
    lines = f.readlines()
    for stock_mapping_one in lines:
        stock_name = stock_mapping_one.split("\t")[1]
        stock_names.append(stock_name)
    f.close()

quetion_cls = {}
for question_2020_one in question_2020:
    for stock_name_one in stock_names:
        # if len(stock_name_one) != 4:
        #     continue
        if stock_name_one in question_2020_one:
            # print(question_2020_one)
            question_2020_one = question_2020_one.replace("在2020年的", "<year>")
            question_2020_one = question_2020_one.replace("2020年的", "<year>")

            question_2020_one = question_2020_one.replace("在2020年", "<year>")
            question_2020_one = question_2020_one.replace("2020年", "<year>")
            question_2020_one = question_2020_one.replace("2020", "<year>")
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
            question_2020_one = question_2020_one.replace("请以2位小数点形式回答。", "<ask>")
            question_2020_one = question_2020_one.replace("是多少元?", "<money>")
            question_2020_one = question_2020_one.replace("是多少元？", "<money>")
            question_2020_one = question_2020_one.replace("是多少?", "<how>")
            question_2020_one = question_2020_one.replace("是多少?", "<how>")
            question_2020_one = question_2020_one.replace("<company><year>", "<year><company>")

            # print(question_2020_one)
            if question_2020_one in quetion_cls:
                quetion_cls[question_2020_one] = quetion_cls[question_2020_one] + 1
            else:
                quetion_cls[question_2020_one] = 1

a = sorted(quetion_cls.items(), key=lambda x: x[1], reverse=True)
# print(a)
index = 0
for  val in a:
    if index == 50:
        break
    print(val)
    index+=1