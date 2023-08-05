import json
file_old="/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/submit_example_20230805.json"
file_new="/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/submit_example_20230805_new.json"

with open(file_old, "r", encoding="utf-8") as f1, open("%s" % file_new, "w", encoding="utf-8") as f2:
    for line in f1:
        try:
            questions_dict = json.loads(line)
        except Exception:
            print("error json: " + line)

        answer_content = questions_dict['answer']
        if "为" in answer_content and "元" in answer_content:

            # print(answer_content.replace(',',''))
            questions_dict['answer'] = answer_content.replace(',','')
        ret = json.dumps(questions_dict, ensure_ascii=False) + '\n'
        f2.write(ret)
    f1.close()
    f2.close()