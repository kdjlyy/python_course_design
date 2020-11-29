# python_course_design Python课程设计 
**get_data.py** 爬取用户信息和影评信息  
**user_info.py** 爬取推荐用户的id  
**recommend.py** 使用协同过滤算法推荐电影

**user_data.json** 保存用户id和主页url(未使用)  
**movie_data.json** 保存用户和影评信息  
**get_data_log** get_data.py爬取数据的日志信息

***注：***   
① movie_data.json文件已获取，直接运行recommend.py可进行电影推荐。  

### v1.1.3
添加了代码注释，删除了非必要的文件和代码。

### v1.1.2
绘制柱状图可能显示过多，改为最多显示前5个用户。

### v1.1.1
##### ① 更新了爬虫模块的代码
使用本地IP爬取豆瓣网站，当爬取信息数量过大时会被封IP。改用代理IP的方式爬取：从IP代理网站生成的API链接，调用GET请求即可返回所需的IP结果，每次连接都使用一个新的IP。

##### ② 更新了数据集
爬取了近200个用户的前90条有效影评信息。

##### ③ 改正了一些bug :bug:
1. 在输入用户id进行一系列操作之前，先判断用户是否在数据集中。如果不在数据集中，则调用user_info.py文件的add_user_info函数，从豆瓣官网获取该用户信息，添加到数据集中。
2. 改正了选择页面输入空格出错的问题。

##### ④ 添加了一个新功能:  
        (1) 计算某个用户最相似的用户
        (2) 向用户推荐电影
        (3) 计算两用户之间的相关系数
        (4) 添加用户到数据集
        (Q) 退出
        Enter choice:  
  