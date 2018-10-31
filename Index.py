from Init import Init
from collections import defaultdict
from collections import OrderedDict
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
import urllib.request
import json
import itertools
import heapq
from heapq import heappush, heappop
import collections
import arrow
import time
from dateutil import parser

def getEndoUsers():
    init = Init()
    sub_reddits = init.subReddit.split(',') # Subreddits would be endo/adenomyosis/endometriosis
    users = defaultdict(date)
    for sub_red in sub_reddits:
        users = getEndoSubredditUser(users, sub_red)

def getEndoSubredditUser(users, sub_red):
    user_data = getEndoBatchUsers(sub_red)
    comments = user_data['data']
    for comm in comments:
        create_date = comm.created_date.date()
     #   if create_date < user[cmt.author.name]:
      #      user[cmt.author.name] = create_date

def getEndoBatchUsers(sub_red):
    #start_date = '1540874103'
    #start_date = time.strptime(datetime.now()).strftime('%s')
   # start_date = int(datetime.now().strftime('%s'))
    users = []
    start_date = datetime.now()
    start_date_epoch = time.mktime(start_date.timetuple())
    end_date = datetime.now() - relativedelta(months=int(1))
    end_date_epoch = time.mktime(end_date.timetuple())
    final_date = parser.parse("Jan 01 2018 12:00AM")
    while end_date > final_date:
         api_url = 'https://api.pushshift.io/reddit/search/comment/?subreddit=' + sub_red + '&before='+ str(int(start_date_epoch)) + '&after=' + str(int(end_date_epoch)) + '&size=5000&sort=desc'
         url = urllib.request.urlopen(api_url)
         user_data = json.loads(url.read().decode())
        # users.update(user_data)
         users.append(user_data['data'])
         start_date = end_date
         start_date_epoch = end_date_epoch
         end_date = start_date - relativedelta(months=int(1))
         end_date_epoch = time.mktime(end_date.timetuple())
    return users

endo_users = getEndoUsers()
