import os
import json
from datetime import datetime, timedelta
from tweepy import OAuthHandler

here = os.path.abspath(os.path.dirname(__file__))

# load auth json
with open(os.path.join(here, 'assets', 'auth.json'), 'r') as f:
    auth = json.load(f)
    
# load the route json
with open(os.path.join(here, 'assets', 'route.json'), 'r') as f:
    route = json.load(f)
    
# create Twitter OAuthHandler
twitter_auth = OAuthHandler(auth['ckey'], auth['csecret'])
twitter_auth.set_access_token(auth['atkn'], auth['asecret'])

# hashtags to filter on
tags = set([
    'greatamericaneclipse', 'eclipse2017', 'eclipse', 
    'fightsupremacy', 'saturdaymorning', 'newyork'
])

def make_test_route():
    dt_format = '%Y%m%d %H%M'
    interval = 1
    n = datetime.utcnow()
    test_route = []
    for place in route[-20:]:
        place_copy = place.copy()
        start = n + timedelta(minutes=interval)
        interval += 1
        stop = n + timedelta(minutes=interval)
        place_copy.update({'start': datetime.strftime(start, dt_format), 'stop': datetime.strftime(stop, dt_format)})
        test_route.append(place_copy)
    return test_route


def get_nysf_route():
    def get_timerange(plus_seconds, start=datetime.utcnow()):
        n = start + timedelta(seconds=5)
        e = n + timedelta(seconds=plus_seconds)
        return n, e

    nypoi = [-74,40,-73,41]
    _nystart, _nyend = get_timerange(120)
    nystart = datetime.strftime(_nystart, '%Y%m%d %H%M')
    nyend = datetime.strftime(_nyend, '%Y%m%d %H%M')

    sfpoi = [-122.75,36.8,-121.75,37.8]
    _sfstart, _sfend = get_timerange(120, start=_nyend)
    sfstart = datetime.strftime(_sfstart, '%Y%m%d %H%M')
    sfend = datetime.strftime(_sfend, '%Y%m%d %H%M')

    test_route = [{'start': nystart, 'stop': nyend, 'box': nypoi},
              {'start': sfstart, 'stop': sfend, 'box': sfpoi}]
    return test_route
