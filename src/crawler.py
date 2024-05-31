# -*- coding: utf-8 -*-
# Author: JudeTe
# Repo: https://github.com/JudeTe/ptt-image-crawler
# Date: 2023-05-12
# Python version: 3.9


"""Crawl any board from PTT and download all images from the articles.
Usage: python crawler.py -b <board name> -i <start_page> <end_page> --path <path> 
       -d <directory name> -t <threads>
Example: python crawler.py --b nba -i 50 100 -p C:// -d nba -t 10
Quick Start: python crawler.py
"""


import argparse
import logging
import os
import queue
import re
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
import requests
from bs4 import BeautifulSoup


@dataclass
class BaseCrawler(ABC):
    """Crawl from any source."""
    download_count: int = 0
    path: str = '.'
    directory_name: str = 'Download'
    directory_path: str = os.path.join(path, directory_name)
    session: requests.Session = field(default_factory=requests.Session)
    thread_num: int = os.cpu_count()

    def __post_init__(self) -> None:
        self.session.cookies.set('over18', '1')
        self.session.timeout = 5
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
            AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/58.0.3029.110 Safari/537.3'
        }

    @abstractmethod
    def crawl(self, is_testing=False): ...

    def execute_with_threads(self, func, args) -> None:
        """Run function with threads."""
        with ThreadPoolExecutor(max_workers=self.thread_num) as executor:
            executor.map(func, args)

    def download(self, url: str, file_name: str = None) -> None:
        """Download the file from the given URL and save it to the specified path."""
        if file_name is None:
            file_name = url.split('/')[-1]
        file_path = os.path.join(self.directory_path, file_name)
        try:
            response = self.session.get(url)
            response.raise_for_status()
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError,
                requests.exceptions.Timeout, requests.exceptions.TooManyRedirects,
                requests.exceptions.RequestException) as err_:
            logging.error("Download network error: %s", err_)
            return
        file_content = response.content
        try:
            with open(file_path, "wb") as file:
                file.write(file_content)
        except PermissionError:
            logging.error("PermissionError: %s", file_path)
            return
        except IOError as io_err:
            logging.error("I/O error: %s", str(io_err))
            return
        except Exception as err_:
            logging.error("Failed to save file due to unknown error: %s", err_)
            return
        self.download_count += 1

    def __del__(self) -> None:
        """Logging download count when the program ends."""
        logging.info("%s Downloaded %d files.", self.__class__.__name__, 
                     self.download_count)


@dataclass
class PttImageCrawler(BaseCrawler):
    """Crawl images from the given board."""
    PTT_URL = "https://www.ptt.cc/bbs"
    IMAGE_URL_PATTERN = re.compile(r"https?://(i\.|)imgur\.com/\w+(\.jpg|)")

    start_page: int = 0
    end_page: int = 0
    max_page_of_board: int = 0
    board: str = 'beauty'
    path: str = '.'
    directory_name: str = 'beauty'
    directory_path: str = os.path.join(path, directory_name)
    article_queue: queue.Queue = field(default_factory=queue.Queue)
    image_queue: queue.Queue = field(default_factory=queue.Queue)

    def parse_args(self) -> None:
        """Parse arguments from command line."""
        numbers_of_core = os.cpu_count()
        parser = argparse.ArgumentParser(description='ptt-image-crawler is a web crawling \
                                        tool that crawls images from PTT.')
        parser.add_argument('--board', '-b', type=str, default='beauty',
                            help='specify the board you want to download \
                            (default: "beauty")')
        parser.add_argument('-i', metavar=('start_page', 'end_page'),
                            type=int, nargs=2, help="start and end page")
        parser.add_argument('--path', '-p', type=str, default='.',
                            help='specify the path for storing the file (default: ".")')
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
            if self.start_page > self.end_page:
                self.start_page, self.end_page = self.end_page, self.start_page
        self.path = args.path if args.path else self.path
        self.directory_name = args.dir if args.dir else self.board
        self.directory_path = os.path.join(self.path, self.directory_name)
        if not os.path.exists(self.directory_path):
            os.mkdir(self.directory_path)
        self.thread_num = args.thread
        if self.thread_num <= 0:
            self.thread_num = 1

    def get_board_max_page(self) -> None:
        """Get the max page of the board."""
        board_index_url = f"{self.__class__.PTT_URL}/{self.board}/index.html"
        try:
            response = self.session.get(board_index_url)
            response.raise_for_status()
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError,
                requests.exceptions.Timeout, requests.exceptions.TooManyRedirects,
                requests.exceptions.RequestException) as err_:
            logging.error("Get board max page network error: %s", err_)
            return
        soup = BeautifulSoup(response.text, "html.parser")
        last_page_url = soup.find_all("a", class_="btn wide")[1]["href"]
        tags = soup.find_all('a', class_="btn wide", text="上頁")
        if tags:
            last_page_url = tags[0]["href"]
        self.max_page_of_board = int(last_page_url.split("index")[1].split(".")[0])
        logging.info("Max page: %d", self.max_page_of_board)

    def crawl_articles(self, page: int = 0) -> None:
        """Crawl articles from the given pages."""
        if page != 0:
            page = self.max_page_of_board - page + 1
        page_url = f"{self.__class__.PTT_URL}/{self.board}/index{page}.html"
        try:
            response = self.session.get(page_url)
            response.raise_for_status()
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError,
                requests.exceptions.Timeout, requests.exceptions.TooManyRedirects,
                requests.exceptions.RequestException) as err_:
            logging.error("Crawling articles network error: %s", err_)
            return
        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.select("div.title a[href]"):
            article_suffix = link["href"].split("/")[-1]
            self.article_queue.put(article_suffix)

    def crawl_images(self, article_suffix: str) -> None:
        """Crawl img from the given articles."""
        article_url = f"{self.__class__.PTT_URL}/{self.board}/{article_suffix}"
        try:
            response = self.session.get(article_url)
            response.raise_for_status()
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError,
                requests.exceptions.Timeout, requests.exceptions.TooManyRedirects,
                requests.exceptions.RequestException) as err_:
            logging.error("Crawling images network error: %s", err_)
            return
        soup = BeautifulSoup(response.text, "html.parser")
        for link_html in soup.find_all("a", {"href": self.__class__.IMAGE_URL_PATTERN}):
            img_url = link_html.text
            if not img_url.endswith(".jpg"):
                img_url = f"{img_url}.jpg"
            self.image_queue.put(img_url)

    def crawl(self, is_testing=False) -> None:
        """Crawl PTT."""
        self.parse_args()
        if is_testing:
            logging.basicConfig(level=logging.INFO)
            # self.path = os.path.dirname(os.path.abspath(__file__))
        start_time = time.time()
        self.get_board_max_page()
        self.execute_with_threads(self.crawl_articles,
                                  (i for i in range(self.start_page, self.end_page + 1)))
        logging.info("Download from %d articles...", self.article_queue.qsize())
        self.execute_with_threads(self.crawl_images,
                                  (self.article_queue.get() for _ in
                                   range(self.article_queue.qsize())))
        logging.info("Downloading %d files...", self.image_queue.qsize())
        self.execute_with_threads(self.download,
                                  (self.image_queue.get() for _ in
                                   range(self.image_queue.qsize())))
        logging.info("Time taken: %.2f seconds.", time.time() - start_time)


if __name__ == "__main__":
    crawler = PttImageCrawler()
    crawler.crawl()
