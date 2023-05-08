import os
import sys
import gc
import time
import queue
import threading
import multiprocessing
from multiprocessing import Process, Pool
import argparse
import requests
from bs4 import BeautifulSoup


"""To be added: 
1. Multi-Process
2. Scrapy progress bar

"""
numbers_of_core = os.cpu_count()
parser = argparse.ArgumentParser(description='Ptt Crawler')
parser.add_argument('--board', type=str, default='beauty', help='board name')
parser.add_argument('--pages', type=int, default=1, help='number of pages')
parser.add_argument('--path', type=str, default=f'', help='path to save')
parser.add_argument('--dir', type=str, default='', help='directory name')
parser.add_argument('--thread', type=int, default=0, help='number of threads')
parser.add_argument('--process', type=int, default=0, help='number of process')
args = parser.parse_args()
board = args.board
pages = args.pages
path = args.path if args.path else os.path.dirname(os.path.abspath(__file__))
directory_name = args.dir if args.dir else board
thread_num = args.thread
process_num = args.process

if not thread_num and not process_num:
    process_num = numbers_of_core
elif thread_num and process_num:
    thread_num = None
    process_num = numbers_of_core
dir = f"{path}/{directory_name}/"
if not os.path.exists(dir):
    os.mkdir(dir)
BASEPAGE = 0
BOARD_PREFIX = f"https://www.ptt.cc/bbs/{board}"

def article_crawler() -> queue:
    """Scrape articles from given pages"""
    crawler_queue = queue.Queue()
    for page in range(BASEPAGE, BASEPAGE + pages):
        url = f"https://www.ptt.cc/bbs/{board}/index{page}.html"
        response = requests.get(url, headers = {"cookie": "over18=1"})
        soup = BeautifulSoup(response.text, "html.parser")
        for title in soup.find_all("div", class_="title"):
            try:
                link_suffix = title.find("a")["href"].split('/')[-1]
            except:
                continue
            crawler_queue.put(link_suffix)
    return crawler_queue

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

def crawler_thread(crawler_queue: queue) -> None:
    """Non blocking get queue"""
    while crawler_queue.qsize() > 0:
        url = crawler_queue.get_nowait()
        img_crawler(url)

class Worker(threading.Thread):
    """Worker for scraping"""
    def __init__(self, queue, num):
        # super().__init__()
        threading.Thread.__init__(self)
        self.queue = queue
        self.num = num

    def run(self):
        while self.queue.qsize() > 0:
            url = self.queue.get()
            print(f"Worker {self.num}: {url}")
            img_crawler(url)

if __name__ == "__main__":
    start_time = time.time()
    crawler_queue = article_crawler()
    print(f"Total articles: {crawler_queue.qsize()}")
    if thread_num:
        threads = []
        for i in range(thread_num):
            threads.append(Worker(crawler_queue, i))
            # t = threading.Thread(target=crawler_thread, args=(crawler_queue, ))
            # threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    elif process_num:
        processes = []
        for i in range(process_num):
            p = Process(target=crawler_thread, args=(crawler_queue, ))
            processes.append(p)
        for p in processes:
            p.start()
        for p in processes:
            p.join()

        # pool = Pool(process_num)
        # pool_outputs = pool.map(crawler_thread, (crawler_queue, ))
        # print("將會阻塞並於 pool.map 子程序結束後觸發")

        # pool_outputs = pool.map_async(crawler_thread, (crawler_queue, ))
        # print('將不會阻塞並和 pool.map_async 並行觸發')
        # # close 和 join 是確保主程序結束後，子程序仍然繼續進行
        # pool.close()
        # pool.join()

    end_time = time.time()
    print(f"Time takes: {end_time - start_time} seconds.")
    print("Done.")

