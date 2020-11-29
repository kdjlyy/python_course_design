# -*- coding: utf-8 -*-
# 爬虫获取待推荐用户数据，获取豆瓣影评信息，最后追加放入json文件中
# created by 徐智沛 李晓宇 苏正棚 许都礼
# copyright USTC
# 11.29.2020

import json
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import urllib

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/74.0.3724.8 Safari/537.36',
    'Referer': 'https://movie.douban.com/subject/26100958/comments',
    'Connection': 'keep-alive'
}

# 判断用户是否在数据集中
# :param movie_data: 数据集的文件名
# :param user_id: 用户的豆瓣ID
def judge_user(movie_data, user_id):
    if user_id in movie_data:
        return True
    else:
        return False

# 添加用户到数据集中
# :param user_id: 用户的豆瓣ID
def add_user_info(user_id):
    file1 = open('user_data.json', 'r', encoding='utf-8')
    user_data = json.load(file1)
    file1.close()

    if judge_user(user_data, user_id):
        print("未添加 因为该用户已经在数据集中！")
        return

    length1 = len(user_data)

    file2 = open('movie_data.json', 'r', encoding='utf-8')
    movie_data = json.load(file2)
    file2.close()

    url = "https://movie.douban.com/people/" + user_id + "/"
    user_data.setdefault(user_id, {})
    user_data[user_id]['people_url'] = url

    movie_data.setdefault(user_id, {})
    movie_data[user_id]["people_url"] = url

    for i in range(0, 6):
        comment_url_suffix = ("collect?start=" + str(i * 15) + "&sort=time&rating=all"
                                                               "&filter=all&mode=grid")
        comment_url = movie_data[user_id]["people_url"] + comment_url_suffix
        try:
            req = urllib.request.Request(url=comment_url, headers=headers)
            comment_data = urllib.request.urlopen(req).read().decode('utf-8')
        except:
            print("从网站未找到该用户的信息！")
            return
        else:
            print("成功定位该用户影评信息！ 第", str(i+1), "页")
        bs = BeautifulSoup(comment_data, 'html.parser')
        infos = bs.find("div", {"class": "grid-view"}).findAll("div", {"class": "info"})
        for info in infos:
            movie_name = info.em.get_text()
            try:
                movie_rate = re.search("[0-9]", info.findAll("li")[2].span.attrs["class"][0]).group()
            except:
                continue
            try:
                movie_comment = info.find("span", {"class": "comment"}).get_text()
            except:
                movie_comment = ""
            movie_data[user_id].setdefault("movies", {})
            movie_data[user_id]["movies"].setdefault(movie_name, {})
            movie_data[user_id]["movies"][movie_name]["movie_rate"] = movie_rate
            movie_data[user_id]["movies"][movie_name]["movie_comment"] = movie_comment

    file1 = open('user_data.json', 'w', encoding='utf-8')
    json.dump(user_data, file1, ensure_ascii=False)
    file1.close()

    file2 = open('movie_data.json', 'w', encoding='utf-8')
    json.dump(movie_data, file2, ensure_ascii=False)
    file2.close()

    if len(user_data) - 1 == length1 and len(movie_data) - 1 == length1:
        print("成功加入数据集！")
    else:
        print("加入数据集失败！")
