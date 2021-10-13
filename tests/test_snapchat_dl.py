#!/usr/bin/env python
"""Tests for `snapchat_dl` package."""
import json
import os
import shutil
import unittest
from unittest import mock

from snapchat_dl.snapchat_dl import SnapchatDL
from snapchat_dl.utils import APIResponseError
from snapchat_dl.utils import NoStoriesAvailable


def teardown_module(module):
    shutil.rmtree(".test-data")


class TestSnapchat_dl(unittest.TestCase):
    """Tests for `snapchat_dl` package."""

    def setUp(self):
        """Set up test fixtures."""
        self.snapchat_dl = SnapchatDL(
            limit_story=10, quiet=True, directory_prefix=".test-data", dump_json=True,
        )
        self.test_url = "https://filesamples.com/samples/video/mp4/sample_640x360.mp4"
        self.test_url404 = "https://google.com/error.html"
        self.username = "invalidusername"
        self.html = open(
            "tests/mock_data/invalidusername.html", "r", encoding="utf8"
        ).read()
        self.html_nostories = open(
            "tests/mock_data/invalidusername-nostories.html", "r", encoding="utf8"
        ).read()

    def test_class_init(self):
        """Test snapchat_dl init."""
        self.assertTrue(self.snapchat_dl)

    def test_invalid_username(self):
        """Test snapchat_dl Stories are not available."""
        with self.assertRaises(APIResponseError):
            self.snapchat_dl.download("username")

    @mock.patch("snapchat_dl.snapchat_dl.SnapchatDL._api_response")
    def test_get_stories(self, api_response):
        """Test snapchat_dl Download."""
        api_response.return_value = self.html
        self.snapchat_dl.download(self.username)

    @mock.patch("snapchat_dl.snapchat_dl.SnapchatDL._api_response")
    def test_no_stories(self, api_response):
        """Test snapchat_dl Download."""
        api_response.return_value = self.html_nostories
        with self.assertRaises(NoStoriesAvailable):
            self.snapchat_dl.download(self.username)
