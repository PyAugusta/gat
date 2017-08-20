import threading
from collections import deque, defaultdict

class OnDataHandler(object):

    def __init__(self):
        self.all_data = deque()
        self.new_data = deque()
        self.columns = ['x', 'y', 'url', 'text', 'media', 'display_img', 'coords', 'hashtags'] 

    def process_data(self, data):
        print(data)
        self.all_data.append(data)
        self.new_data.append(data)

    def get_new_data(self):
        print(self.new_data)
        merged = {k: [d.get(k) for d in self.new_data] for k in {k for d in self.new_data for k in d}}
        print(merged)
        self.new_data.clear()
        return merged
