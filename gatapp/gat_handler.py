import os
import threading
import json
from collections import deque, defaultdict
from gat_config import here

class OnDataHandler(object):

    def __init__(self):
        self.all_data = deque()
        self.new_data = deque()
        self.columns = ['x', 'y', 'url', 'text', 'media', 'display_img', 'coords', 'hashtags', 'time'] 

    def process_data(self, data):
        print(data)
        self.all_data.append(data)
        self.new_data.append(data)

    def get_new_data(self):
        merged = {k: [d.get(k) for d in self.new_data] for k in {k for d in self.new_data for k in d}}
        self.new_data.clear()
        return merged

    def save_data(self, filepath=os.path.join(here, 'data/gat_tweets.json')):
        with open(filepath, 'w') as f:
            json.dump(list(self.all_data), f)
        
