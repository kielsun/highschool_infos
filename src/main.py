# -- coding:UTF-8 --
from pandas import json_normalize
import requests
import os
try:
    os.makedirs('../date/专业信息')
except Exception:
    pass
try:
    os.makedirs('../date/学校信息')
except Exception:
    pass

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'utf-8',
    'Connection': 'keep-alive',
    'Origin': 'https://www.gaokao.cn',
    'Referer': 'https://www.gaokao.cn/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    'sec-ch-ua':
    '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

# 请求头部以及请求载荷


# 分数线与专业线
def get_schoolInfos(school_id):
    school_infos = {}
    school_infos["学校id"] = school_id
    url = f'https://static-data.gaokao.cn/www/2.0/school/{school_id}/info.json'
    response = requests.get(url, headers=headers)
    infos = response.json().get("data")
    school_infos["院校名称"] = infos.get("name")
    school_infos["院校性质"] = infos.get('school_type_name') + "|" + infos.get(
        'school_nature_name')
    school_infos["院校地址"] = infos.get('address')
    return school_infos


def get_Mark_infos(url, headers) -> list:
    response = requests.get(url, headers)
    if response.status_code == 200:
        return response.json()['data']['item']
    else:
        return []


def special_mark(
    school_id=2906,
    province=13,
    year=2021,
):
    spe_url1 = f"https://static-data.gaokao.cn/www/2.0/schoolspecialindex/{year}/{school_id}/{province}/2074/10/1.json"
    spe_url2 = f"https://static-data.gaokao.cn/www/2.0/schoolspecialindex/{year}/{school_id}/{province}/2074/10/2.json"
    items = get_Mark_infos(spe_url1, headers) + get_Mark_infos(
        spe_url2, headers)
    info_list = []

    for m in items:
        if m is None:
            continue
        news_school = {}
        news_school["专业代号"] = m['special_id']
        news_school["专业名称"] = m["spname"]
        news_school["最低分"] = m["min"]
        news_school["最低排名"] = m['min_section']
        info_list.append(news_school)
    return info_list


def get_MatchSchool(my_mark=336, target_province=13) -> list:
    school_list = []
    signsafe = dict({
        1: "590f0a9dc95d556c0e6c2f528d101426",
        2: "a9f0a2ecfc71e434a87bdee054dae0e3"
    })
    for page in range(1, 3):

        json_data = {
            'admissions': '',
            'again': '70003,70005',
            'central': '',
            'department': '',
            'dual_class': '',
            'f211': '',
            'f985': '',
            'is_dual_class': '',
            'local_batch_id': '',
            'local_province_id': '13',
            'page': page,
            'preferred': 70004,
            'province_id': target_province,
            'recom': 0,
            'request_type': 1,
            'score': f'{my_mark}',
            'section_level': '',
            'signsafe': signsafe[page],
            'size': 20,
            'top_id':
            '[770,603,2843,1249,2622,1398,417,668,270,135,597,108,596,624,2902,85,335,689,1815,88,90]',
            'total': 143777,
            'uri': 'apidata/api/gkv4/recomScore/gufen_b_special',
            'xktype': 1,
            'zslx': 0,
        }
        url = f'https://api.eol.cn/web/api/?admissions=&again=70003,70005&central=&department=&dual_class=&f211=&f985=&is_doublehigh=&is_dual_class=&local_batch_id=&local_province_id=13&page={page}&preferred=70004&province_id={target_province}&recom=0&request_type=1&score={my_mark}&section_level=&size=20&top_id=\\[770,603,2843,1249,2622,1398,417,668,270,135,597,108,596,624,2902,85,335,689,1815,88,90\\]&total=143777&uri=apidata/api/gkv4/recomScore/gufen_b_special&xktype=1&zslx=0&signsafe={signsafe[page]}'

        open_url = requests.post(url=url, headers=headers, json=json_data)

        if open_url.status_code == 200:
            match_lists = open_url.json()['data']['item']
            for each in match_lists:
                # print(each["school_id"])
                school_list.append(each["school_id"])
        else:
            print("get_error")
            continue

    return school_list


def save_josn(result, path):
    json_normalize(result).to_excel(path)


def main(year, my_mark, target_province):

    school_lists = get_MatchSchool(my_mark, target_province)
    print(school_lists)
    school_infos = []
    for id in school_lists:
        info = get_schoolInfos(id)
        school_infos.append(info)
    save_josn(school_infos, "../date/学校信息/school_infos.xlsx")
    for each in school_infos:
        id = each["学校id"]
        id_s = str(id)
        na = each["院校名称"]
        marks = special_mark(id, province=13, year=year)
        print(id)
        save_josn(marks, f"../date/专业信息/{year}_{na}_{id_s}_专业信息.xlsx")


if __name__ == "__main__":
    main(year=2021, my_mark=336, target_province=11)
