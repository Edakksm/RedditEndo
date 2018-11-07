import pandas as pd
import time
from datetime import datetime
import urllib.request
import json
from dateutil.relativedelta import relativedelta
from dateutil import parser
from Init import Init
from collections import defaultdict

init = Init()
def Process():
    endo_users = pd.read_csv('endoUsers.csv', header=None).iloc[:,0]
    non_endo_subreddits = pd.read_csv('statistics.csv').iloc[:,0]
    start_date = parser.parse("Oct 01 2017 12:00AM")
    init_date = parser.parse('Apr 01 2017 12:00AM')
    pos_users = defaultdict(list)
    neg_users = defaultdict(list)
    for sub_red in non_endo_subreddits:
        pos_users, neg_users = getEndoBatchUsers(endo_users, sub_red, start_date, init_date, pos_users, neg_users)
        print(len(pos_users))
        print(len(neg_users))
        print('completed')


def getEndoBatchUsers(endo_users, sub_red, start_date, init_date,pos_users, neg_users):
    d = defaultdict(list)
    start_date_epoch = time.mktime(start_date.timetuple())
    end_date = start_date - relativedelta(months=int(1))
    end_date_epoch = time.mktime(end_date.timetuple())
    while end_date > init_date:
         api_comment_url = 'https://api.pushshift.io/reddit/search/comment/?subreddit=' + sub_red + '&before='+ str(int(start_date_epoch)) + '&after=' + str(int(end_date_epoch)) + '&size=5000&sort=desc'
         url = urllib.request.urlopen(api_comment_url)
         user_data = json.loads(url.read().decode())
         for user_detail in user_data['data']:
             key = user_detail['author']
             value = user_detail['body']
             if key in endo_users:
                 if key in pos_users:
                     pos_users[key].append(value)
                 else:
                     pos_users[key] = [value]
             else:
                 if key in neg_users:
                     neg_users[key].append(value)
                 else:
                     neg_users[key] = [value]
         start_date = end_date
         start_date_epoch = end_date_epoch
         end_date = start_date - relativedelta(months=int(1))
         end_date_epoch = time.mktime(end_date.timetuple())

    return pos_users, neg_users

Process()
