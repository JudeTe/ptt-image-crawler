import os
import sys
import gc
import time
import requests
import threading
import queue
from bs4 import BeautifulSoup


"""待補: 
1. Multi-Process
1. sys path且支援不同OS
2. 增加抓取進度條

"""


base_page = 0
board = input("請輸入想抓的看板: ")
pages = input("請輸入想要的頁數: ")
path = input("請輸入想放的路徑，如按Enter則預設為當前資料夾")
directory_name = input("這邊可以指定您想要放入的資料夾名稱，如未指定則預設為看板名稱，如已有同名稱之資料夾，圖片會被覆蓋")
thread_num = input("請輸入要設定的執行緒數: ")

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
try:
    thread_num = int(thread_num)
except:
    thread_num = 10

BOARD_PREFIX = f"https://www.ptt.cc/bbs/{board}"
def article_crawler() -> list:
    """Scrape articles from given pages"""
    articles = []
    for page in range(base_page, base_page + pages):
        url = f"https://www.ptt.cc/bbs/{board}/index{page}.html"
        response = requests.get(url, headers = {"cookie": "over18=1"})
        soup = BeautifulSoup(response.text, "html.parser")
        for title in soup.find_all("div", class_="title"):
            try:
                link_suffix = title.find("a")["href"].split('/')[-1]
            except:
                continue
            articles.append(link_suffix)
    return articles

def img_crawler(article_suffix: str) -> None:
    """Scrape img from given article"""
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


class Worker(threading.Thread):
    """Worker for scraping"""
    def __init__(self, queue, num):
        # super().__init__()
        threading.Thread.__init__(self)
        self.queue = queue
        self.num = num

    def run(self):
        while self.queue.qsize() > 0:
            msg = self.queue.get()
            print(f"Worker {self.num}: {msg}")

if __name__ == "__main__":
    start_time = time.time()
    crawler_queue = queue.Queue()
    articles = article_crawler()
    for article in articles:
        crawler_queue.put(img_crawler(article))

    for i in range(thread_num):
        globals() [f'worker_{i}'] = Worker(crawler_queue, i)
        # my_worker1 = Worker(crawler_queue, 1)
    # start_time = time.time()
    for obj in gc.get_objects():
        if isinstance(obj, Worker):
            obj.start()
    for obj in gc.get_objects():
        if isinstance(obj, Worker):
            obj.join()
    end_time = time.time()
    print(f"Time takes: {end_time - start_time} seconds.")
    print("Done.")

