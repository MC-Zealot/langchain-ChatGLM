# import pandas as pd

# questions_df = pd.read_json('/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/submit_example.json')
# print(questions_df[0])
import json

with open("/home/zealot/yizhou/git/chatglm_llm_fintech_raw_dataset/test_questions.json", "r") as f:
    lines = f.readlines()
    for line in lines:
        user_dict = json.loads(line)
        print(user_dict)