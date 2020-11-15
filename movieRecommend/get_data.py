# -*- coding: utf-8 -*-

"""
爬取豆瓣某影视的评分前100个用户，将他们的影评信息抓取下来作为movie.json
为了保证数据的可靠性，选择豆瓣电影top250 No.1的【肖申克的救赎】，热门影评的前100人作为数据：
https://movie.douban.com/subject/1292052/comments?start=0&limit=20&sort=new_score&status=P&percent_type=
"""

from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import json
import urllib
import time
import requests

people_names = []  # 爬取的用户id
people_urls = []   # 用户主页的url

# 创建一个正则表达式匹配对象
r = re.compile(r'e/(.+)/')
# 浏览器的模拟
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/74.0.3724.8 Safari/537.36',
    # 'Referer': 'https://movie.douban.com/subject/26100958/comments',
    'Referer': 'https://movie.douban.com/subject/1292052/comments',
    # 'Referer': 'https://movie.douban.com/subject/35069506/comments',
    'Connection': 'keep-alive'
}

print("爬取用户中 ...")
user_num = 1    # 10*20*90 = 18000条信息
for i in range(0, user_num):
    # url = ("https://movie.douban.com/subject/1292052/comments?"
    #        "start=" + str(i * 20) + "&limit=20&sort=new_score&status=P&percent_type=")
    url = ("https://movie.douban.com/subject/1292052/comments?start="+str(i * 20)+"&limit=20&status=P&sort=new_score")
    req = urllib.request.Request(url=url, headers=headers)
    data = urllib.request.urlopen(req).read().decode('utf-8')
    # data = requests.get(url,headers=headers)
    bs = BeautifulSoup(data, 'html.parser')
    comments = bs.findAll("div", {"class": "comment"})

    # 将用户主页存储在people_url中
    for comment in comments:
        people_url = comment.findAll("a")[1].attrs["href"].replace("www", "movie")
        name = re.findall(r, people_url)[0]
        people_names.append(name)
        people_urls.append(people_url)
print("爬取用户完成")

# 将用户名和用户主页的url组合成一个字典，如：
# {
#     'whiterhinoceros': {'people_url': 'https://movie.douban.com/people/whiterhinoceros/'},
#     'kingfish': {'people_url': 'https://movie.douban.com/people/kingfish/'}
# }
final_data = {}
for i in range(0, len(people_names)):
    final_data.setdefault(people_names[i], {})
    final_data[people_names[i]]["people_url"] = people_urls[i]
print(final_data)

# 保存用户信息
user_info_file = open('user_data.json', 'w', encoding='utf-8')
json.dump(final_data, user_info_file, ensure_ascii=False)
user_info_file.close()

print("爬取用户影评中...")
user_count = 1
for people_name in final_data:
    print("正在爬取第" + str(user_count) + "位用户" + people_name + "的影评信息")
    user_count += 1
    # 爬取该用户前90条影评,忽略没有进行评分的电影
    for i in range(0, 6):
        # 获取影评后缀
        comment_url_suffix = ("collect?start=" + str(i * 15) + "&sort=time&rating=all"
                                                               "&filter=all&mode=grid")
        comment_url = final_data[people_name]["people_url"] + comment_url_suffix
        # 生成该用户看过的电影记录的url,如：
        # https://movie.douban.com/people/whiterhinoceros/collect?start=0&sort=time&rating=all&filter=all&mode=grid

        req = urllib.request.Request(url=comment_url, headers=headers)
        comment_data = urllib.request.urlopen(req).read().decode('utf-8')
        bs = BeautifulSoup(comment_data, 'html.parser')
        infos = bs.find("div", {"class": "grid-view"}).findAll("div", {"class": "info"})
        # info_bs = bs.find("div", {"class": "grid-view"})
        # if info_bs == "":
        #     continue
        # else:
        #     infos = info_bs.findAll("div", {"class": "info"})

        for info in infos:
            movie_name = info.em.get_text()  # 从em标签提取
            try:
                movie_rate = re.search("[0-9]", info.findAll("li")[2].span.attrs["class"][0]).group()
            except:
                continue
            try:
                movie_comment = info.find("span", {"class": "comment"}).get_text()
            except:
                movie_comment = ""
            final_data[people_name].setdefault("movies", {})
            final_data[people_name]["movies"].setdefault(movie_name, {})
            final_data[people_name]["movies"][movie_name]["movie_rate"] = movie_rate
            final_data[people_name]["movies"][movie_name]["movie_comment"] = movie_comment
print("爬取用户影评完成")

# 保存用户名、主页url和该用户前90部的电影影评信息
file = open('movie_data.json', 'w', encoding='utf-8')
json.dump(final_data, file, ensure_ascii=False)
file.close()

# 读取数据
# file = open('movie_data.json', 'r', encoding='utf-8')
# s = json.load(file)
# file.close()

