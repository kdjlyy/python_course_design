# -*- coding: utf-8 -*-
"""
根据皮尔森系数，找出与我相似的用户，再找这些用户最喜欢的电影
推荐20部我可能喜欢的电影
"""

import json
from math import sqrt
import matplotlib.pyplot as plt
from math import *

file = open('movie_data.json', 'r', encoding='utf-8')
movie_data = json.load(file)
file.close()

# 这里填豆瓣id
my_name = "180311913"
sim_person = []
sim_person_data = []

# 返回p1和p2的皮尔逊相关系数，即两个人品味的相似度
def sim_pearson(data, p1, p2):
    """
    计算皮尔森相似度
    :param data: 爬取的用户影评数据
    :param p1: 用户1
    :param p2: 用户2
    :return: 返回相似度
    """
    si = {}
    for item in data[p1]["movies"]:
        if item in data[p2]["movies"]:
            si[item] = 1

    # 没有共同影评，返回0
    if len(si) == 0:
        return 0

    # 根据公式计算皮尔森系数
    n = len(si)
    sum1 = sum([int(data[p1]["movies"][it]["movie_rate"]) for it in si])
    sum2 = sum([int(data[p2]["movies"][it]["movie_rate"]) for it in si])
    sim1_sq = sum([pow(int(data[p1]["movies"][it]["movie_rate"]), 2) for it in si])
    sim2_sq = sum([pow(int(data[p2]["movies"][it]["movie_rate"]), 2) for it in si])
    p_sum = sum([int(data[p1]["movies"][it]["movie_rate"]) * int(data[p2]["movies"][it]["movie_rate"]) for it in si])
    # 计算皮尔森系数 R
    num = p_sum - (sum1 * sum2 / n)
    den = sqrt((sim1_sq - pow(sum1, 2) / n) * (sim2_sq - pow(sum2, 2) / n))
    if den == 0:
        return 0
    r = num / den
    return r


def top_matches(data, person, similarity=sim_pearson):
    """
    找到5个相似度最高的用户
    :param data: 爬取的数据
    :param person: 用户本人
    :param n: 前n个最相似的用户
    :param similarity: 皮尔森相关系数
    :return:
    """
    sorted_data = {person: data[person]}
    min_sim = 0.5
    sim_persons_list = []
    sim_person.clear()
    sim_person_data.clear()
    for other in data:
        if other == person:
            continue
        if similarity(data, person, other) >= min_sim:
            sorted_data[other] = data[other]
            sim_person.append(other)
            sim_person_data.append(sorted_data[other])
            # print(other, sorted_data[other])
    return sorted_data


def get_recommendations(data1, person, n=5, similarity=sim_pearson):
    """
    获取推荐结果
    :param data: 电影评分数据
    :param person: 待推荐用户名称
    :param n: 推荐条目
    :param similarity: 皮尔森相似度
    :return: 返回电影数据
    """
    totals = {}
    sim_sum = {}
    data = top_matches(data1, person)
    # data = data1
    for other in data:
        if other == person:  # 计算除自己以外的相似度
            continue
        sim = similarity(data, person, other)
        # print("皮尔森相似度:", sim)
        # 将等于0或更小的项目去掉
        if sim <= 0:
            continue
        for item in data[other]["movies"]:
            # 仅找出我未看过的电影
            if item not in data[person]["movies"] or data[person]["movies"][item] == 0:
                # Similarity * Score 相似度乘评分
                totals.setdefault(item, 0)
                totals[item] += int(data[other]["movies"][item]["movie_rate"]) * sim
                # Sum of similarities 总相似度
                sim_sum.setdefault(item, 0)
                sim_sum[item] += sim
        # print(totals)
        # print(sim_sum)

    # 创建评分列表
    rankings = [(total / sim_sum[item], item) for item, total in totals.items()]
    # 将rating排序并返回
    rankings.sort()
    rankings.reverse()
    # print(rankings)
    return rankings[0:n]

def showmenu():
    prompt = """
        (1)计算某个用户最相似的用户
        (2)根据用户推荐电影给其他人
        (3)计算两用户之间的相关系数
        (Q)退出
        Enter choice:"""
    chosen = True
    while chosen:
        choice = input(prompt).strip()[0].upper()
        if choice == '1':
            print(choice)
            print("请输入需要计算相似率的用户：")
            user = input()
            RES = top_matches(movie_data, user)
            for i in range(len(sim_person)):
                print(sim_person[i])
                print(sim_person_data[i])
            # fraces = []
            # labels = []
            # x = [1, 2, 3, 4, 5]
            # for i in RES:
            #     labels.append(i[0])
            #     fraces.append(i[1])
            # plt.plot(x, fraces)
            # for a, b, c in zip(x, fraces, labels):
            #     plt.text(a, b, c, ha='center', va='bottom', fontsize=10)
            # plt.show()
        elif choice == '2':
            print(choice)
            print("请输入需要被推荐电影的用户：")
            user = input()
            Recommendations = get_recommendations(movie_data, user, 5)
            for movie in Recommendations:
                print(movie)
        elif choice == '3':
            print("请输入需要比较的两个用户：")
            print("请输入第一个用户编号：")
            user1 = input()
            print("请输入第二个用户编号：")
            user2 = input()
            R = sim_pearson(movie_data, user1, user2)
            print(R)
        elif choice == 'Q':
            print("退出程序！！！")
            chosen = False

if __name__ == '__main__':
    # 打印推荐结果
    # for res in get_recommendations(movie_data, my_name, n=5):
    #     print(res)
    showmenu()

