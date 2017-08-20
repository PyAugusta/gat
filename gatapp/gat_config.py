import os
import json
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
