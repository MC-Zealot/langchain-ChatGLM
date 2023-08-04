

stock_names = []
with open("../data_extract/6.txt", "r") as f:
    lines = f.readlines()
    for stock_mapping_one in lines:
        stock_name = stock_mapping_one.split("\t")[1]
        stock_names.append(stock_name)
    f.close()


def replace_company_name_and_year_by_question(question, stock_names):
    for stock_name_one in stock_names:
        stock_name_one=stock_name_one.replace('\n','')
        if stock_name_one in question:
            # print(question)
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
            question = question.replace("在" + stock_name_one, "")
            question = question.replace("在" + stock_name_one + "的", "")
            question = question.replace(stock_name_one + "股份有限公司", "")
            question = question.replace(stock_name_one + "集团股份有限公司", "")
            question = question.replace(stock_name_one + "科技股份有限公司", "")
            question = question.replace(stock_name_one + "有限公司", "")
            question = question.replace(stock_name_one + "股份有限公司的", "")
            question = question.replace(stock_name_one + "智能控制股份有限公司", "")
            question = question.replace(stock_name_one + "的", "")
            question = question.replace(stock_name_one, "")

    return question
