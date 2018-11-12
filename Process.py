import pandas as pd
import time
from datetime import datetime
import urllib.request
import json
from dateutil.relativedelta import relativedelta
from dateutil import parser
from Init import Init
from collections import defaultdict
import pytz    # $ pip install pytz
import tzlocal
import itertools
import os

init = Init()
def Process():
    api_comment_url = 'https://api.pushshift.io/reddit/search/comment/?author=juliadream88&size=1000'
    url = urllib.request.urlopen(api_comment_url)
    local_timezone = tzlocal.get_localzone()  # get pytz tzinfo
    user_data = json.loads(url.read().decode())
    for u in user_data['data']:
        t = u['created_utc']
        l = datetime.fromtimestamp(t).strftime('%c')
        print('{0}:{1}:{2}'.format(u['subreddit'],l, u['body']))
     #   utc_time = datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
      #  local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_timezone)

    endo_users = pd.read_csv('endoUsers.csv')
    non_endo_subreddits = pd.read_csv('10to50.csv').iloc[:,0]
   # endo_users = dict(itertools.zip_longest(*[iter(endo_users)] * 2, fillvalue=""))
   # e = endo_users.to_dict('dict')
    endo_users = endo_users.set_index('user_name').T.to_dict('list')
    start_date = parser.parse("Nov 10 2018 12:00AM")
  #  start_date = parser.parse('Tue Oct 31 12:36:32 2018')
    #start_date = parser.parse('Fri Nov 09 12:36:32 2018')
    init_date = parser.parse('Apr 01 2017 12:00AM')
    pos_users = defaultdict(list)
    neg_users = defaultdict(list)
    final_users = defaultdict(list)
    d = os.getcwd()
    if not (os.path.exists(os.path.join(d, 'pos'))):
      os.mkdir('pos')
      os.mkdir('neg')
    for sub_red in non_endo_subreddits:
        pos_users, neg_users = getEndoBatchUsers(endo_users, sub_red, start_date, init_date, pos_users, neg_users)
      #  final_users[sub_red].append([len(pos_users), len(neg_users)])

        with open('usercount.csv','a') as f:
            s = sub_red + ',' + str(len(pos_users)) + ',' + str(len(neg_users))
            f.write(s)
        d_pos = os.path.join(d, 'pos')
        d_neg = os.path.join(d, 'neg')
        for i,user in pos_users.items():
            try:
                if not(os.path.exists(os.path.join(d_pos,sub_red))):
                    os.chdir(d_pos)
                    os.mkdir(sub_red)
            except Exception as ex:
                print(ex)
            file_name = os.path.join(d_pos, sub_red, i + '.txt')
            with open(file_name, 'w') as f:
                f.write(sub_red)
                f.write('\n')
                f.write(user[0])
                f.write('\n\n')

        for i,user in neg_users.items():
            try:
                if not (os.path.exists(os.path.join(d_neg, sub_red))):
                    os.chdir(d_neg)
                    os.mkdir(sub_red)
            except Exception as ex:
                print(ex)
            file_name = os.path.join(d_neg, sub_red, i + '.txt')
            try:
                with open(file_name, 'w') as f:
                    f.write(sub_red)
                    f.write('\n')
                    f.write(user[0])
                    f.write('\n\n')
            except Exception as ex:
                print(ex)

        print('len of pos users is :{0}',len(pos_users))
        print('len of neg users is :{0}',len(neg_users))
        print('completed')


def getEndoBatchUsers(endo_users, sub_red, start_date, init_date,pos_users, neg_users):
    d = defaultdict(list)
    start_date_epoch = time.mktime(start_date.timetuple())
    end_date = start_date - relativedelta(days=int(1))
    end_date_epoch = time.mktime(end_date.timetuple())
    while end_date > init_date:
         api_comment_url = 'https://api.pushshift.io/reddit/search/comment/?subreddit=' + sub_red + '&before='+ str(int(start_date_epoch)) + '&after=' + str(int(end_date_epoch)) + '&size=5000&sort=desc'
         url = urllib.request.urlopen(api_comment_url)
         user_data = json.loads(url.read().decode())
         count = 0
         for user_detail in user_data['data']:
             try:
                 t = user_detail['created_utc']
                 msg_created_time = datetime.fromtimestamp(t).strftime('%c')
                # print('{0}:{1}:{2}'.format(user_detail['subreddit'], user_detail['author'],l))
                 key = user_detail['author']
                 value=user_detail['body']
                 count += 1
                 if key == 'juliadream88':
                     s = 'stop'
                 if key in list(endo_users):
                     endo_first_comment_time = endo_users[key]
                     if parser.parse(msg_created_time) < parser.parse(endo_first_comment_time[0]):
                         if key in pos_users:
                             pos_users[key].append(value)
                         else:
                             pos_users[key] = [value]
                 else:
                     if key in neg_users:
                         neg_users[key].append(value)
                     else:
                         neg_users[key] = [value]

             except Exception as ex:
                  print(ex.message)
         api_submission_url = 'https://api.pushshift.io/reddit/search/submission/?subreddit=' + sub_red + '&before=' + str(int(start_date_epoch)) + '&after=' + str(int(end_date_epoch)) + '&size=5000&sort=desc'
         url = urllib.request.urlopen(api_submission_url)
         user_data = json.loads(url.read().decode())
         print('*****')
         print('count of {0} batch is  {1} between {2} and {3}'.format(sub_red, count, end_date, start_date))
         for user_detail in user_data['data']:
             try:
                 t = user_detail['created_utc']
                 msg_created_time = datetime.fromtimestamp(t).strftime('%c')
                # print('{0}:{1}:{2}'.format(user_detail['subreddit'], user_detail['author'], l))
                 key = user_detail['author']
                 value = user_detail['title']
                 if key in list(endo_users):
                     endo_first_comment_time = endo_users[key]
                     if parser.parse(msg_created_time) < parser.parse(endo_first_comment_time[0]):
                         if key in pos_users:
                             pos_users[key].append(value)
                         else:
                             pos_users[key] = [value]
                 else:
                     if key in neg_users:
                         neg_users[key].append(value)
                     else:
                         neg_users[key] = [value]
             except Exception as ex:
                 print(ex.message)

         start_date = end_date
         start_date_epoch = end_date_epoch
         end_date = start_date - relativedelta(days=int(1))
         end_date_epoch = time.mktime(end_date.timetuple())
         print('pos users:{0}'.format(len(pos_users)))
         print('neg users:{0}'.format(len(neg_users)))
    return pos_users, neg_users

Process()
