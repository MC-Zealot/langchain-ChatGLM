import json


def by_score(t):
    return t[0]

with open("/home/zealot/Downloads/submit_example_20230808_output.json", "r") as f1, \
        open('/home/zealot/Downloads/submit_example_20230808_output_sort.json', 'w', encoding="utf8") as f2:
    lines = f1.readlines()
    ret_list=[]
    for line in lines:
        questions_dict = json.loads(line)
        questions_id = int(questions_dict['id'])
        ret_list.append([questions_id, line])

    L2 = sorted(ret_list, key=by_score, reverse=False)
    for line in L2:
        f2.write(str(line[1]))
    # print(ret_list[-10:])
    # print(L2[-10:])