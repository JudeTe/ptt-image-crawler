# Encoding: utf-8
# Author: JudeTe
# Repo: https://github.com/JudeTe/PttImageCrawler
# Date: 2023-05-12
# Python version: 3.9


"""Crawl any board from PTT and download all images from the articles.
Usage: python crawler.py -b <board name> -i <start_page> <end_page> --path <path> -d <directory name> -t <threads>
Example: python crawler.py --board nba -i 50 100 --path ./ --dir nba --thread 10
"""


import os
import time
import queue
import threading
import argparse
import requests
from bs4 import BeautifulSoup


numbers_of_core = os.cpu_count()
parser = argparse.ArgumentParser(description='PttImageCrawler is a web crawling tool that crawls images from PTT.')
parser.add_argument('--board', '-b', type=str, default='beauty', 
                    help='specify the board you want to download (default: "beauty")')
parser.add_argument('-i', metavar=('start_page', 'end_page'), type=int, nargs=2, help="start and end page")
parser.add_argument('--path', '-p', type=str, default='', 
                    help='specify the path for storing the file (default: "./")')
parser.add_argument('--dir', '-d', type=str, default='', 
                    help='specify the directory name for storing the file \
                    (default: "{board name}")')
parser.add_argument('--thread', '-t', type=int, default=numbers_of_core, 
                    help='specify how many threads to use for running the program. \
                    (default: numbers of your core)')

args = parser.parse_args()
board = args.board
if not args.i:
    start_page = 0
    end_page = 0
else:
    start_page = args.i[0]
    end_page = args.i[1]
    start_page = end_page if start_page > end_page else start_page
path = args.path if args.path else os.path.dirname(os.path.abspath(__file__))
directory_name = args.dir if args.dir else board
directory_path = f"{path}/{directory_name}/"
if not os.path.exists(directory_path):
    os.mkdir(directory_path)
thread_num = args.thread

BOARD_PREFIX = f"https://www.ptt.cc/bbs/{board}"
download_count = 0

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


def article_crawler(q: queue) -> None:
    """Scrape articles from given pages"""
    for page in range(start_page, end_page + 1):
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
    return q


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


if __name__ == "__main__":
    start_time = time.time()
    crawler_queue = article_crawler(queue.Queue())
    print(f"Total articles: {crawler_queue.qsize()}")
    workers = []
    for i in range(thread_num):
        t = Worker(crawler_queue, i)
        t.start()
        workers.append(t)
    for worker in workers:
        worker.join()
    end_time = time.time()
    print(f"Time takes: {end_time - start_time} seconds.")
    print(f"Download {download_count} files.")
