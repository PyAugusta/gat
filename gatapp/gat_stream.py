import threading
from math import radians
from datetime import datetime
from dateutil.parser import parse
from time import sleep
from tweepy import Stream
from tweepy.streaming import StreamListener
from gat_handler import OnDataHandler
from gat_config import *
from gat_utils import *

class Clock(threading.Thread):

    def __init__(self):
        self._lock = threading.Lock()
        self._time = datetime.utcnow()
        self._stop_event = threading.Event()
        threading.Thread.__init__(self)
        
    def run(self):
        while True:
            if self._stop_event.is_set():
                break
            self._time = datetime.utcnow()
            sleep(1)
            
    def time(self):
        self._lock.acquire()
        try:
            return self._time
        finally:
            self._lock.release()
            
    def stop(self):
        self._stop_event.set()
        
    def stopped(self):
        return self._stop_event.is_set()
        
# start the clock
clock = Clock()
clock.start()

# function to stop the clock
def stop_clock():
    clock.stop()
    clock.join()
    
    
class StopTime(Exception):
    pass
    

# create an OnDataHanler instance
data_handler = OnDataHandler()


class Listener(StreamListener, threading.Thread):

    def __init__(self, stop_at, box):
        self._stop_event = threading.Event()
        self.stop_at = stop_at
        self.box = [float(c) for c in box]
        self.tweets = []
        self.stream = Stream(twitter_auth, self)
        threading.Thread.__init__(self)
        
    @property
    def stop_time(self):
        return parse(self.stop_at)
        
    def on_data(self, data):
        time = clock.time()
        if time >= self.stop_time:
            print('time up, stopping listener')
            raise StopTime
        all_data = json.loads(data)
        try:
            ext_data = all_data['extended_tweet']
        except KeyError:
            return
        target_data = {}
        media = [row['media_url'] for row in ext_data.get('entities', dict()).get('media', list())]
        hashtags = [row['text'] for row in ext_data['entities']['hashtags']]
        lowered = set([s.lower() for s in hashtags])
        gattags = lowered.intersection(tags)
        if len(media) > 0: #and len(gattags) > 0:
            text = ext_data['full_text']
            display_img = media[0]
            try:
                coords = all_data['coordinates']['coordinates']
                x, y = wgs84(coords)
                target_data.update({'x': x, 'y': y})
            except:
                print(all_data['coordinates'])
                coords = all_data['place']['bounding_box']['coordinates']
                x, y = get_center(coords)
                x, y = wgs84(x, y)
                target_data.update({'x': x, 'y': y})
            username = all_data['user']['screen_name']
            try:
                url = all_data['entities']['urls'][0]['url']
            except (KeyError, IndexError):
                url = None
            target_data.update({'url': url, 'text': text, 'display_img': display_img, 'media': media, 'coords': coords, 'hashtags': hashtags, 'time': time})
            data_handler.process_data(target_data)
            #self.tweets.append(target_data)
            self.tweets.append(all_data)
    
    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        try:
            self.stream.filter(locations=self.box)
        except StopTime:
            self.stop()
            return
            
        
if __name__ == '__main__':
    try:
        from datetime import timedelta
        seconds = 20 * 60
        stop_time = datetime.strftime(datetime.utcnow() + timedelta(seconds=seconds), '%Y%m%d %H%M')
        print("will stop around {}".format(stop_time))
        ny = [-74,40,-73,41]
        sf = [-122.75,36.8,-121.75,37.8]
        listeners  = [Listener(stop_time, box) for box in [ny, sf]]
        for l in listeners:
            l.start()

        # retrieve data periodically
        for i in range(seconds//10):
            print(len(data_handler.get_df()))
            sleep(10)
        print('periodic check done')

    finally:
        for l in listeners:
            l.join()
        stop_clock()
        df = data_handler.get_df()
        df.to_csv('data/gat_tweets.csv')
