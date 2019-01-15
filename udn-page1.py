# coding=UTF-8
#udn新聞第一頁
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
url = "https://udn.com/news/breaknews/1/99#breaknews"
response = requests.get(url)
html = BeautifulSoup(response.text)
x1 = time.time()
# with open("udntext.txt","w",encoding="utf-8") as files:
#     for x in range(1) :
#         try:
#             for a in html.find("div",id="breaknews_body").find_all("dt"):
#                 newsurl = a.find("a")
#                 try:
#                     Nresponse = requests.get("https://udn.com"+newsurl["href"])
#                     Nhtml = BeautifulSoup(Nresponse.text)
#                     for content in Nhtml.find("div", id="story_body_content").find_all("p"):
#                         files.write(content.text)
#                 # except TypeError:
#                 #     pass
#                 # continue
#                 except AttributeError:
#                     continue
#                 except TypeError:
#                     continue
#         except AttributeError:
#             continue
#         except TypeError:
#             continue
# x2 = time.time()
# print("花費時間：",x2-x1,"秒")
# with open("udntitle.txt","w",encoding="utf-8") as file:
for a in html.find("div",id="breaknews_body").find_all("dt"):
    category = a.find("a",class_="cate")
    title = a.find("h2")
    times = a.find("div",class_="dt")
    view = a.find("div",class_="view")
    newsurl = a.find("a")
    try:
        titles = (category.text, times.text, title.text, view.text, "https://udn.com" + newsurl["href"])
        df = pd.DataFrame(columns=[category.text, times.text, title.text, view.text,"https://udn.com" + newsurl["href"]])
            # file.write(str(df))
    except AttributeError:
        continue
    df.to_csv("udntitle.csv",encoding="utf-8",index=False)
x3 = time.time()
print("花費時間",x3-x1,"秒")