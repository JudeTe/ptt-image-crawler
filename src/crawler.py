# -*- coding: utf-8 -*-
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


class PttCrawler:
    BOARD_PREFIX = f"https://www.ptt.cc/bbs"
    start_page = 0
    end_page = 0
    board = 'nba'
    path = './'
    directory_name = {board}
    directory_path = f"{path}/{directory_name}/"
    thread_num = os.cpu_count()

    def __init__(self, q=None, download_count=0) -> None:
        if q is None:
            q = queue.Queue()
        self.crawler_queue = q
        self.download_count = download_count

    def parse_arg(self):
        numbers_of_core = os.cpu_count()
        parser = argparse.ArgumentParser(description='PttImageCrawler is a web crawling \
                                        tool that crawls images from PTT.')
        parser.add_argument('--board', '-b', type=str, default='beauty', 
                            help='specify the board you want to download \
                            (default: "beauty")')
        parser.add_argument('-i', metavar=('start_page', 'end_page'), 
                            type=int, nargs=2, help="start and end page")
        parser.add_argument('--path', '-p', type=str, default='', 
                            help='specify the path for storing the file (default: "./")')
        parser.add_argument('--dir', '-d', type=str, default='', 
                            help='specify the directory name for storing the file \
                            (default: "{board name}")')
        parser.add_argument('--thread', '-t', type=int, default=numbers_of_core, 
                            help='specify how many threads to use for \
                            running the program. (default: numbers of your core)')
        args = parser.parse_args()
        self.board = args.board
        if args.i:
            self.start_page = args.i[0]
            self.end_page = args.i[1]
            self.start_page = self.end_page if self.start_page > self.end_page else self.start_page
        self.path = args.path if args.path else os.path.dirname(os.path.abspath(__file__))
        self.directory_name = args.dir if args.dir else self.board
        self.directory_path = f"{self.path}/{self.directory_name}/"
        if not os.path.exists(self.directory_path):
            os.mkdir(self.directory_path)
        self.thread_num = args.thread
        if self.thread_num == 0: self.thread_num = 1

    def article_crawler(self, q: queue = None) -> None:
        """Scrape articles from given pages"""
        if q is None:
            q = self.crawler_queue
        
        for page in range(self.start_page, self.end_page + 1):
            url = f"https://www.ptt.cc/bbs/{self.board}/index{page}.html"
            response = requests.get(url, headers = {"cookie": "over18=1"}, timeout=30)
            soup = BeautifulSoup(response.text, "html.parser")
            for title in soup.find_all("div", class_="title"):
                try:
                    link_suffix = title.find("a")["href"].split('/')[-1]
                    if link_suffix:
                        q.put(link_suffix)
                except Exception as err_:
                    print(f"Crawling article's link error: {err_}")
                    continue
        return q

    def img_crawler(self, article_suffix: str) -> None:
        """Scrape img from given article"""
        article_url = f"{self.BOARD_PREFIX}/{self.board}/{article_suffix}"
        response = requests.get(article_url, headers={"cookie": "over18=1"}, timeout=30)
        soup = BeautifulSoup(response.text, "html.parser")
        for img_html in soup.find_all("a"):
            link = img_html.text
            if not link.endswith('.jpg') and not link.endswith('.png'):
                continue
            try:
                img = requests.get(link, headers = {"cookie": "over18=1"}, 
                                   timeout=30).content
                img_name = link.split('/')[-1]
                img_path = f"{self.directory_path}/{img_name}"
                with open(img_path, "wb") as files:
                    files.write(img)
                    self.download_count += 1
            except Exception as err_:
                print(f"Crawling img's link error: {err_}")
                continue

    def crawl_thread(self):
        while self.crawler_queue.qsize() > 0:
            url = self.crawler_queue.get()
            self.img_crawler(url)

    def crawl(self):
        workers = []
        for _ in range(self.thread_num):
            t = threading.Thread(target=self.crawl_thread, args=())
            t.start()
            workers.append(t)
        for worker in workers:
            worker.join()
    
    def run(self):
        self.parse_arg()
        self.article_crawler()
        print(f"Total articles: {self.crawler_queue.qsize()}")
        self.crawl()

    def __del__(self):
        print(f"Downloaded {self.download_count} files.")

if __name__ == "__main__":
    start_time = time.time()
    PttCrawler().run()
    print(f"Time taken: {time.time() - start_time:.2f} seconds.")
