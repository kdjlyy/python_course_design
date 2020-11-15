# -*- coding: utf-8 -*-
"""
爬虫获取待推荐用户数据（默认自己）
获取本人豆瓣影评信息，通过此信息分析个人喜好,寻找与我品味相似的用户
最后将本人的喜好也放入json文件中
"""

import json
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import urllib


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/74.0.3724.8 Safari/537.36',
    'Referer': 'https://movie.douban.com/subject/26100958/comments',
    'Connection': 'keep-alive'}
file = open('movie_data.json', 'r', encoding='utf-8')
movie_data = json.load(file)
file.close()

# 这里填你的豆瓣上面的id
# 在movie_data里加入自己的id和url
people_name = "180311913"
url = "https://movie.douban.com/people/"+people_name+"/"
movie_data.setdefault(people_name, {})
movie_data[people_name]["people_url"] = url
print(movie_data)

# 在原本的url中加入自己的id（即待推荐用户的id）和url，并爬取前90条数据，追加到movie_data.json中
for i in range(0, 6):
    comment_url_suffix = ("collect?start="+str(i*15)+"&sort=time&rating=all"
                          "&filter=all&mode=grid")
    comment_url = movie_data[people_name]["people_url"]+comment_url_suffix
    req = urllib.request.Request(url=comment_url, headers=headers)
    comment_data = urllib.request.urlopen(req).read().decode('utf-8')
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
        movie_data[people_name].setdefault("movies", {})
        movie_data[people_name]["movies"].setdefault(movie_name, {})
        movie_data[people_name]["movies"][movie_name]["movie_rate"] = movie_rate
        movie_data[people_name]["movies"][movie_name]["movie_comment"] = movie_comment


file = open('movie_data.json', 'w', encoding='utf-8')
json.dump(movie_data, file, ensure_ascii=False)
file.close()
