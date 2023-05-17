# -*- coding: utf-8 -*-
# Author: JudeTe
# Repo: https://github.com/JudeTe/ptt-image-crawler
# Date: 2023-05-16
# Python version: 3.9

"""Unittest for ptt-image-crawler"""


import os
import unittest
from src.crawler import PttImageCrawler


class TestPttImageCrawler(unittest.TestCase):
    """Unittest for ptt-image-crawler"""
    numbers_of_core = os.cpu_count()

    def setUp(self) -> None:
        """Set up unit test"""
        self.crawler = PttImageCrawler()

    def tearDown(self) -> None: ...

    def test_crawl_articles(self) -> None:
        """Test crawl_articles()"""
        self.crawler.crawl_articles()
        self.assertGreater(self.crawler.article_queue.qsize(), 0)

    def test_crawl_images(self) -> None:
        """Test crawl_images()"""
        self.crawler.crawl_images("M.1684280091.A.C27.html")
        self.assertGreater(self.crawler.image_queue.qsize(), 0)

    def test_download(self) -> None:
        """Test download()"""
        self.crawler.download(url="https://i.imgur.com/9QXwvI2.jpg")
        self.assertGreater(self.crawler.download_count, 0)

if __name__ == "__main__":
    unittest.main()
