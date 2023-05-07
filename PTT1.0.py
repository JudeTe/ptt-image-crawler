import os
import sys
import random
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen , urlretrieve


"""待補: 
1. Threading
2. sys path且支援不同OS

"""


base_page = 0
board = input("請輸入想抓的看板：")
pages = input("請輸入想要的頁數：")
path = input("請輸入想放的路徑，如按Enter則預設為當前資料夾")
directory_name = input("這邊可以指定您想要放入的資料夾名稱，如未指定則預設為看板名稱，如已有同名稱之資料夾，圖片會被覆蓋")

if not board:
    board = 'beauty'
if not directory_name:
    directory_name = board
if path == "":
    # dir = f"C:/{directory_name}/"
    dir = f"./{directory_name}/"
else :
    dir = f"{path}/{directory_name}/"
if not os.path.exists(dir):
    os.mkdir(dir)
try:
    pages = int(pages)
except:
    pages = 1

BOARD_PREFIX = f"https://www.ptt.cc/bbs/{board}"
for page in range(base_page, base_page + pages):
    articles = []
    url = f"https://www.ptt.cc/bbs/{board}/index{page}.html"
    response = requests.get(url, headers = {"cookie": "over18=1"})
    soup = BeautifulSoup(response.text, "html.parser")
    for title in soup.find_all("div", class_="title"):
        try:
            link_suffix = title.find("a")["href"].split('/')[-1]
        except:
            continue
        articles.append(link_suffix)
    for article_suffix in articles:
        article_url = f"{BOARD_PREFIX}/{article_suffix}"
        response = requests.get(article_url, headers={"cookie": "over18=1"})
        soup = BeautifulSoup(response.text, "html.parser")
        for img_html in soup.find_all("a"):
            link = img_html.text
            if not link.endswith('.jpg') and not link.endswith('.png'):
                continue
            try:
                img = requests.get(link, headers = {"cookie": "over18=1"}).content
                img_name = link.split('/')[-1]
                img_path = f"{dir}/{img_name}"
                with open(img_path, "wb") as files:
                    files.write(img)
            except:
                continue




