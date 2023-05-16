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

    def test_parse_args(self) -> None:
        """Test parse_args()"""
        self.crawler.parse_args()
        self.assertEqual(self.crawler.board, 'beauty')
        self.assertEqual(self.crawler.start_page, 0)
        self.assertEqual(self.crawler.end_page, 0)
        self.assertEqual(self.crawler.path, './')
        self.assertEqual(self.crawler.directory_name, 'beauty')
        self.assertEqual(self.crawler.directory_path, './beauty/')
        self.assertEqual(self.crawler.thread_num, self.numbers_of_core)

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
