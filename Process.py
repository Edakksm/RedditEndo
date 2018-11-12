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
start_date = datetime.now()
init_date = parser.parse('Apr 01 2017 12:00AM') # The hard start date
cut_off_date = parser.parse('Jan 01 2018 12:00AM') # The hard end date - All endo users first post should be between Jan 01 2018 and current date
cut_off_date_3months = parser.parse('Aug 01 2018 12:00AM') # Added this for negative users - to give a buffer of 3 months. For example, if a user posts on Nov 1st (
                            # today is Nov 12th, then since there are only 12 days from Nov 1st to 12th, we cant say that the user is a non endo users just because
                            # the user didnt get a chance to post to endo

def Process():
    endo_users = pd.read_csv('endoUsers.csv')
    non_endo_subreddits = pd.read_csv('10to50.csv').iloc[:,0]
    endo_users = endo_users.set_index('user_name').T.to_dict('list')

    pos_users = defaultdict(list)
    neg_users = defaultdict(list)
    final_users = defaultdict(list)
    d = os.getcwd()
    if not (os.path.exists(os.path.join(d, 'pos'))):
      os.mkdir('pos')
      os.mkdir('neg')
    for sub_red in non_endo_subreddits:
        pos_users, neg_users = getEndoBatchUsers(endo_users, sub_red, start_date, init_date, pos_users, neg_users)

        with open('usercount.csv','a') as f:
            s = sub_red + ',' + str(len(pos_users)) + ',' + str(len(neg_users))
            f.write(s)
            f.write('\n')
        d_pos = os.path.join(d, 'pos')
        d_neg = os.path.join(d, 'neg')
        for i,user in pos_users.items():
            try:
                if not(os.path.exists(os.path.join(d_pos,sub_red))):
                    os.chdir(d_pos)
                    os.mkdir(sub_red)
                file_name = os.path.join(d_pos, sub_red, i + '.txt')
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(sub_red)
                    f.write('\n')
                    f.write(user[0])
                    f.write('\n\n')
            except Exception as ex:
                print(ex)

        for i,user in neg_users.items():
            try:
                if not (os.path.exists(os.path.join(d_neg, sub_red))):
                    os.chdir(d_neg)
                    os.mkdir(sub_red)

                file_name = os.path.join(d_neg, sub_red, i + '.txt')
                with open(file_name, 'w', encoding='utf-8') as f:
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
                 key = user_detail['author']
                 value=user_detail['body']
                 count += 1
                 if key in list(endo_users):
                     endo_first_comment_time = endo_users[key]
                     three_months = parser.parse(endo_first_comment_time[0]) - relativedelta(months=int(3))
                     six_months = parser.parse(endo_first_comment_time[0]) - relativedelta(months=int(9))
                     if six_months < parser.parse(msg_created_time) < three_months:
                         if key in pos_users:
                             pos_users[key].append(value)
                         else:
                             pos_users[key] = [value]
                 else:
                     if parser.parse(msg_created_time) < cut_off_date_3months:
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
                 key = user_detail['author']
                 value = user_detail['title']
                 if key in list(endo_users):
                     endo_first_comment_time = endo_users[key]
                     three_months = parser.parse(endo_first_comment_time[0]) - relativedelta(months=int(3))
                     six_months = parser.parse(endo_first_comment_time[0]) - relativedelta(months=int(9))
                     if six_months < parser.parse(msg_created_time) < three_months:
                         if key in pos_users:
                             pos_users[key].append(value)
                         else:
                             pos_users[key] = [value]
                     else:
                         if parser.parse(msg_created_time) < cut_off_date_3months:
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
