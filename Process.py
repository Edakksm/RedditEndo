import pandas as pd
import time
from datetime import datetime
import urllib.request
import json
from dateutil.relativedelta import relativedelta
from dateutil import parser
from Init import Init

init = Init()
def Process():
    endo_users = pd.read_csv('endoUsers.csv', header=None).iloc[:,0]
    non_endo_subreddits = pd.read_csv('statistics.csv').iloc[:,0]
    start_date = parser.parse("Oct 01 2017 12:00AM")
    init_date = parser.parse('Apr 01 2017 12:00AM')
    pos_users = []
    neg_users = []
    for sub_red in non_endo_subreddits:
        pos_users, neg_users = getEndoBatchUsers(endo_users, sub_red, start_date, init_date)

def getEndoBatchUsers(endo_users, sub_red, start_date, init_date):
    users = []
    body = []
    d = {}
   # start_date = datetime.now()
    start_date_epoch = time.mktime(start_date.timetuple())
    end_date = start_date - relativedelta(months=int(1))
    end_date_epoch = time.mktime(end_date.timetuple())
  #  init_date = parser.parse(init.initDate)
    while end_date > init_date:
         api_comment_url = 'https://api.pushshift.io/reddit/search/comment/?subreddit=' + sub_red + '&before='+ str(int(start_date_epoch)) + '&after=' + str(int(end_date_epoch)) + '&size=5000&sort=desc'
         url = urllib.request.urlopen(api_comment_url)
         user_data = json.loads(url.read().decode())
         temp_users = [d['author'] for d in user_data['data'] if d['author'] != '[deleted]']
         users.append(temp_users)
         temp_body = [d['body'] for d in user_data['data'] if d['author'] != '[deleted]']
         body.append(temp_body)
         api_submission_url = 'https://api.pushshift.io/reddit/search/submission/?subreddit=' + sub_red + '&before='+ str(int(start_date_epoch)) + '&after=' + str(int(end_date_epoch)) + '&size=5000&sort=desc'
         url = urllib.request.urlopen(api_submission_url)
         user_data = json.loads(url.read().decode())
         temp_users = [d['author'] for d in user_data['data'] if d['author'] != '[deleted]']
         users.append(temp_users)
         temp_body = [d['title'] for d in user_data['data'] if d['author'] != '[deleted]'] # No body available for submission
         body.append(temp_body)
      #   d =  dict(zip(set(users),body))
         d = {k: v for k, v in zip(users[0], body)}
         start_date = end_date
         start_date_epoch = end_date_epoch
         end_date = start_date - relativedelta(months=int(1))
         end_date_epoch = time.mktime(end_date.timetuple())
    return users

Process()
