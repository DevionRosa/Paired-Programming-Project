import unittest
from main import get_video_id, fetch_video, youtube_search, flatten_dict
import os 
import requests
import json

class TestMain(unittest.TestCase):
    # Uses a youtube search
    yt_test_search = youtube_search("minecraft hard core", os.getenv('YOUTUBE_KEY'))

    # #Case for youtube fetch status code
    def test_fetch(self):
        self.assertEqual(fetch_video("vm4H-GDUrWk", os.getenv('YOUTUBE_KEY')).status_code, 200)

    #Case for youtube search status code
    def test_search(self):
        self.assertEqual(self.yt_test_search.status_code, 200)

    # #Case for video id
    def test_input(self):
        self.assertTrue(get_video_id("https://www.youtube.com/watch?v=vm4H-GDUrWk&ab_channel=ForgeLabs"), "The string should not be empty.")

    def test_flatten_dict(self):
        self.assertEqual(len(flatten_dict(self.yt_test_search.json())), 5)

