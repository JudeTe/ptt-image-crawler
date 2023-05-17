# -*- coding: utf-8 -*-
# Author: JudeTe
# Repo: https://github.com/JudeTe/ptt-image-crawler
# Date: 2023-05-12
# Python version: 3.9


"""Crawl any board from PTT and download all images from the articles.
Usage: python crawler.py -b <board name> -i <start_page> <end_page> --path <path> 
       -d <directory name> -t <threads>
Example: python crawler.py --board nba -i 3990 4000 --path ./ --dir nba --thread 10
Quick Start: python crawler.py
"""


import os
import time
import re
import queue
import argparse
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup


class PttImageCrawler:
    """Crawl any board from PTT and download all images from the articles."""
    PTT_URL = "https://www.ptt.cc/bbs"
    IMAGE_URL_PATTERN = re.compile(r"https?://(i\.|)imgur\.com/\w+(\.jpg|)")

    def __init__(self) -> None:
        self.download_count = 0
        self.article_queue = queue.Queue()
        self.start_page = 0
        self.end_page = 0
        self.board = 'beauty'
        self.path = './'
        self.directory_name = 'beauty'
        self.directory_path = f"{self.path}{self.directory_name}/"
        self.thread_num = os.cpu_count()

    def parse_args(self) -> None:
        """Parse arguments from command line"""
        numbers_of_core = os.cpu_count()
        parser = argparse.ArgumentParser(description='ptt-image-crawler is a web crawling \
                                        tool that crawls images from PTT.')
        parser.add_argument('--board', '-b', type=str, default='beauty',
                            help='specify the board you want to download \
                            (default: "beauty")')
        parser.add_argument('-i', metavar=('start_page', 'end_page'),
                            type=int, nargs=2, help="start and end page")
        parser.add_argument('--path', '-p', type=str, default='./',
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
            self.start_page = self.end_page if self.start_page > self.end_page else \
            self.start_page
        self.path = args.path if args.path else self.path
        os.path.dirname(os.path.abspath(__file__))
        self.directory_name = args.dir if args.dir else self.board
        self.directory_path = f"{self.path}{self.directory_name}/"
        if not os.path.exists(self.directory_path):
            os.mkdir(self.directory_path)
        self.thread_num = args.thread
        if self.thread_num <= 0:
            self.thread_num = 1

    def crawl_articles(self, page: int = 0) -> None:
        """Crawl articles from given pages"""
        url = f"{self.PTT_URL}/{self.board}/index{page}.html"
        response = requests.get(url, headers = {"cookie": "over18=1"}, timeout=30)
        soup = BeautifulSoup(response.text, "html.parser")
        for div_title in soup.find_all("div", class_="title"):
            link = div_title.find("a")
            if link is None:
                continue
            try:
                article_suffix = link["href"].split('/')[-1]
                if article_suffix:
                    self.article_queue.put(article_suffix)
            except Exception as err_:
                print(f"Crawling article's link error: {err_}")
                continue

    def crawl_images(self, article_suffix: str) -> None:
        """Crawl img from given article"""
        article_url = f"{self.PTT_URL}/{self.board}/{article_suffix}"
        response = requests.get(article_url, headers={"cookie": "over18=1"}, timeout=30)
        soup = BeautifulSoup(response.text, "html.parser")
        for link_html in soup.find_all("a", {"href": self.IMAGE_URL_PATTERN}):
            img_url = link_html.text
            if not img_url.endswith(".jpg"):
                img_url = f"{img_url}.jpg"
            img = requests.get(img_url, headers = {"cookie": "over18=1"},
                                timeout=30).content
            img_name = img_url.split('/')[-1]
            img_path = f"{self.directory_path}/{img_name}"
            try:
                with open(img_path, "wb") as files:
                    files.write(img)
                    self.download_count += 1
            except Exception as err_:
                print(f"Crawling img's link error: {err_}")
                continue

    def execute_with_threads(self, func, args) -> None:
        """Run function with threads"""
        with ThreadPoolExecutor(max_workers=self.thread_num) as executor:
            executor.map(func, args)

    def run(self) -> None:
        """Run the program"""
        article_queue = self.article_queue
        self.parse_args()
        start_time = time.time()
        self.execute_with_threads(self.crawl_articles,
                                  range(self.start_page, self.end_page + 1))
        print(f"Succeeded! \nDownloading {article_queue.qsize()} articles...")
        self.execute_with_threads(self.crawl_images,
                                  (article_queue.get() for _ in
                                   range(article_queue.qsize())))
        print(f"Time taken: {time.time() - start_time:.2f} seconds.")

    def __call__(self, unittest=False) -> None:
        """Make class callable"""
        if unittest:
            ...

    def __del__(self) -> None:
        """Print download count when the program ends"""
        print(f"Downloaded {self.download_count} files.")


if __name__ == "__main__":
    PttImageCrawler().run()
    