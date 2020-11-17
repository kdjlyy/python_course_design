# -*- coding: utf-8 -*-
"""
爬取豆瓣某影视的评分前100个用户，将他们的影评信息抓取下来作为movie.json
为了保证数据的可靠性，选择豆瓣电影top250 No.1的【肖申克的救赎】，热门影评的前100人作为数据：
https://movie.douban.com/subject/1292052/comments?start=0&limit=20&sort=new_score&status=P&percent_type=
"""

from bs4 import BeautifulSoup
import re
import json
import time
import requests

people_names = []  # 爬取的用户id
people_urls = []   # 用户主页的url

# 创建一个正则表达式匹配对象
r = re.compile(r'e/(.+)/')

user_count = 1

# 浏览器的模拟
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/74.0.3724.8 Safari/537.36',
    'Referer': 'https://movie.douban.com/subject/1292052/comments',
    'Connection': 'close'  # 'keep-alive'
}

# 代理网站生成的API链接，调用HTTP GET请求即可返回所需的IP结果
def get_proxy():
    print("开始调用get_proxy() ...")
    time.sleep(1)
    douban = "https://movie.douban.com/"
    targetUrl = "http://route.xiongmaodaili.com/xiongmao-web/api/glip?secret=e17d54febcb4e3cd3621687bd4c7a110&orderNo=GL20201117105022cS9fHwXQ&count=1&isTxt=1&proxyType=1"
    # targetUrl = "http://route.xiongmaodaili.com/xiongmao-web/api/glip?secret=e17d54febcb4e3cd3621687bd4c7a110&orderNo=GL20201115202957E65iVlUh&count=1&isTxt=1&proxyType=1"
    try:
        r = requests.get(targetUrl, timeout=9)
    except:
        print("get_proxy() Error!!! request.get()")
        return get_proxy()

    print("r.status_code", r.status_code)
    if r.status_code != 200:
        print("get_proxy() Error!!!  status_code!=200 another try ...")
        return get_proxy()
    ip = r.text[:-2]
    proxy = {
        'http': 'http://' + ip,
        'https': 'https://' + ip
    }
    try:
        res = requests.get(douban, proxies=proxy, headers=headers, timeout=9)
    except:
        print("requests.exceptions.ProxyError!")
        time.sleep(1)
        return get_proxy()
    else:
        if res.status_code == 200:
            print("get ip succcess:", ip)
            return proxy
        else:
            print("status_code="+str(res.status_code)+" another try ...")
            time.sleep(1)
            return get_proxy()

def get_User_Name_And_Url(i):
    url = ("https://movie.douban.com/subject/1292052/comments?start=" + str(i*20) + "&limit=20&status=P&sort=new_score")
    print("正在爬取第" + str(i + 1) + "页的用户名 ...")
    # req = urllib.request.Request(url=url, headers=headers)
    # data = urllib.request.urlopen(req).read().decode('utf-8')
    my_proxies = get_proxy()
    data = requests.get(url, headers=headers, proxies=my_proxies).text

    bs = BeautifulSoup(data, 'html.parser')
    comments = bs.findAll("div", {"class": "comment"})

    print("len(comments):" + str(len(comments)))
    return comments


print("爬取用户中 ...")
page_num = 10    # 10*20*90 = 18000条信息
for i in range(0, page_num):
    comments = get_User_Name_And_Url(i)
    while len(comments) == 0:
        comments = get_User_Name_And_Url(i)
    # 将用户主页存储在people_url中
    for comment in comments:
        people_url = comment.findAll("a")[1].attrs["href"].replace("www", "movie")
        name = re.findall(r, people_url)[0]
        print(name, people_url)  #
        people_names.append(name)
        people_urls.append(people_url)
print("爬取用户完成: ", str(len(people_names)))


final_data = {}
'''
将用户名和用户主页的url组合成一个字典，如：
{ 'whiterhinoceros': {'people_url': 'https://movie.douban.com/people/whiterhinoceros/'} }
'''
for i in range(0, len(people_names)):
    final_data.setdefault(people_names[i], {})
    final_data[people_names[i]]["people_url"] = people_urls[i]

# 保存用户信息(备用)
user_info_file = open('user_data.json', 'w', encoding='utf-8')
json.dump(final_data, user_info_file, ensure_ascii=False)
user_info_file.close()


def get_User_Info(people_name):
    print("正在爬取第" + str(user_count) + "位用户" + people_name + "的影评信息")
    my_proxies = get_proxy()  # 获取代理IP
    # 爬取该用户前90条影评,忽略没有进行评分的电影
    for i in range(0, 6):
        # 获取影评后缀
        comment_url_suffix = ("collect?start=" + str(i * 15) + "&sort=time&rating=all"
                                                               "&filter=all&mode=grid")
        comment_url = final_data[people_name]["people_url"] + comment_url_suffix
        # 生成该用户看过的电影记录的url,如：
        # https://movie.douban.com/people/whiterhinoceros/collect?start=0&sort=time&rating=all&filter=all&mode=grid
        print("get data from:" + comment_url)

        # req = urllib.request.Request(url=comment_url, headers=headers)
        # comment_data = urllib.request.urlopen(req).read().decode('utf-8')

        try:
            comment_request = requests.get(url=comment_url, headers=headers, proxies=my_proxies, timeout=15)
        except:
            print("get_User_Info(people_name) Error! in requests.get()  return (0)")
            return 0

        if comment_request.status_code == 200:
            comment_data = comment_request.text
        else:
            print("get_User_Info(people_name) Error! comment_request.status_code != 200 return (0)")
            return 0

        bs = BeautifulSoup(comment_data, 'html.parser')

        info_bs = bs.find("div", {"class": "grid-view"})
        if info_bs is None:
            print("get_User_Info(people_name) Error! info_bs == None return (0)")
            return 0
        else:
            infos = info_bs.findAll("div", {"class": "info"})

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
    print("第" + str(user_count) + "位用户" + people_name + "影评信息爬取成功\n")
    return 1


print("爬取用户影评中...")
for people_name in final_data:
    if get_User_Info(people_name=people_name) == 0:
        print("get_User_Info(" + people_name + ") Error, another try")
        retry = 1
        while retry <= 3:
            print("retry " + str(retry) + " time(s)")
            if get_User_Info(people_name=people_name) == 1:
                print("retry success!")
                break
            retry = retry + 1
        if retry == 4:
            print("retry failed!")
            final_data[people_name].setdefault("movies", {})

    user_count += 1

print("爬取用户影评完成")

# 保存用户名、主页url和该用户前90部的电影影评信息
file = open('movie_data.json', 'w', encoding='utf-8')
json.dump(final_data, file, ensure_ascii=False)
file.close()

# 读取数据
# file = open('movie_data.json', 'r', encoding='utf-8')
# s = json.load(file)
# file.close()

