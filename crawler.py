# Encoding: utf-8
# Author: JudeTe
# Repo: https://github.com/JudeTe/PttImageCrawler
# Date: 2023-05-10
# Python version: 3.9


"""Crawl any board from PTT and download all images from the articles.
Usage: python crawler.py -b <board name> -p <pages> -d <directory name> -t <threads> -p <processes>
Example: python crawler.py -b beauty -p 1 -d beauty -t 4 -p 4
"""


import os
import time
import queue
import threading
import multiprocessing
from multiprocessing import Process, Pool
from multiprocessing import Queue as MQ
import argparse
import requests
from bs4 import BeautifulSoup


numbers_of_core = os.cpu_count()
parser = argparse.ArgumentParser(description='Ptt Crawler')
parser.add_argument('--board', '-b', type=str, default='beauty', 
                    help='specify the board you want to download (default: "beauty")')
parser.add_argument('--pages', type=int, default=1, 
                    help='specify how many pages you want to download in the given board \
                    (default: 1)')
parser.add_argument('--path', type=str, default='', 
                    help='specify the path for storing the file (default: "./")')
parser.add_argument('--dir', '-d', type=str, default='', 
                    help='specify the directory name for storing the file \
                    (default: "{board name}")')
parser.add_argument('--thread', '-t', type=int, default=0, 
                    help='specify how many threads to use for running the program. \
                    (default: 0)')
parser.add_argument('--process', type=int, default=0,
                    help='specify how many processes to use for running the program. \
                    (default: 0)')
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
directory_path = f"{path}/{directory_name}/"
if not os.path.exists(directory_path):
    os.mkdir(directory_path)
BASEPAGE = 0
download_count = 0
BOARD_PREFIX = f"https://www.ptt.cc/bbs/{board}"

def article_crawler(q: queue) -> None:
    """Scrape articles from given pages"""
    for page in range(BASEPAGE, BASEPAGE + pages):
        url = f"https://www.ptt.cc/bbs/{board}/index{page}.html"
        response = requests.get(url, headers = {"cookie": "over18=1"}, timeout=30)
        soup = BeautifulSoup(response.text, "html.parser")
        for title in soup.find_all("div", class_="title"):
            try:
                link_suffix = title.find("a")["href"].split('/')[-1]
                if link_suffix:
                    q.put(link_suffix)
            except Exception as err_:
                print(f"Error: {err_}")
                continue

def img_crawler(article_suffix: str) -> None:
    """Scrape img from given article"""
    article_url = f"{BOARD_PREFIX}/{article_suffix}"
    response = requests.get(article_url, headers={"cookie": "over18=1"}, timeout=30)
    soup = BeautifulSoup(response.text, "html.parser")
    for img_html in soup.find_all("a"):
        link = img_html.text
        if not link.endswith('.jpg') and not link.endswith('.png'):
            continue
        try:
            img = requests.get(link, headers = {"cookie": "over18=1"}, timeout=30).content
            img_name = link.split('/')[-1]
            img_path = f"{directory_path}/{img_name}"
            with open(img_path, "wb") as files:
                files.write(img)
                global download_count
                download_count += 1
        except Exception as err_:
            print(f"Error: {err_}")
            continue

def crawl_process(queue: queue, workers=None) -> None:
    """Non blocking get queue"""
    for i in range(10):
        t = Worker(queue, i)
        t.start()
        workers.append(t)
    # while queue.qsize() > 0:
    #     url = queue.get_nowait()
    #     img_crawler(url)

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
    crawler_queue = multiprocessing.Queue()
    article_crawler(crawler_queue)
    print(f"Total articles: {crawler_queue.qsize()}")
    workers = []
    worker_nums = thread_num if thread_num else process_num
    for i in range(worker_nums):
        if thread_num:
            t = Worker(crawler_queue, i)
            t.start()
            workers.append(t)
        elif process_num:
            p = Process(target=crawl_process, args=(crawler_queue, workers))
            p.start()
            workers.append(p)
    for worker in workers:
        worker.join()

    # with Pool(processes=8) as pool:
    #     responses = pool.apply_async(crawl_process, args=(crawler_queue, ))

    # pool = Pool(worker_nums)
    # pool_outputs = pool.map(crawl_process, (crawler_queue, ))

    # pool = Pool(worker_nums)
    # pool_outputs = pool.map_async(crawl_process, (crawler_queue, ))
    # pool.close()
    # pool.join()

    end_time = time.time()
    print(f"Time takes: {end_time - start_time} seconds.")
    print(f"Download {download_count} files.")




