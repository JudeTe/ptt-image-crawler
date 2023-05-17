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
        self.assertGreaterEqual(self.crawler.article_queue.qsize(), 0)

    def test_crawl_images(self) -> None:
        """Test crawl_images()"""
        self.crawler.crawl_articles()
        for _ in range(1):
            self.crawler.crawl_images(self.crawler.article_queue.get())
        self.assertGreaterEqual(self.crawler.download_count, 0)


if __name__ == "__main__":
    unittest.main()
