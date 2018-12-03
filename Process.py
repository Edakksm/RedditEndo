import pandas as pd
import time
from datetime import datetime
import urllib.request
import json
from dateutil.relativedelta import relativedelta
from dateutil import parser
from Init import Init
from collections import defaultdict
import html.parser
import pytz    # $ pip install pytz
import tzlocal
import itertools
import os
from bs4 import BeautifulSoup
import re
import xml.sax.saxutils as saxutils


def cleanhtml(raw_html):
  #raw_html = '&<gt>'
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  #cleantext = re.sub(r'^https?:\/\/.*[\r\n]*', '', cleantext, flags=re.MULTILINE)
  cleantext = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', cleantext)
  cleantext = re.sub(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]','',cleantext.strip())
  cleantext =  re.sub("[\n\t\r]",'',cleantext)
  cleantext = re.sub(r'[^A-Za-z0-9]+', ' ', cleantext)
  #cleantext = re.sub(r"\s", "", cleantext)
 # cleantext = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]  |[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', cleantext)
  return cleantext

def Find(string):
    # findall() has been used
    # with valid conditions for urls in string
    url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]  |[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)
    return url


init = Init()
#start_date = datetime.now()
#init_date = parser.parse('Apr 01 2017 12:00AM') # The hard start date
start_date = parser.parse('May 20 2017 01:00AM')
init_date = parser.parse('May 01 2017 12:00AM')
cut_off_date = parser.parse('Jan 01 2018 12:00AM') # The hard end date - All endo users first post should be between Jan 01 2018 and current date
cut_off_date_3months = parser.parse('Aug 01 2018 12:00AM') # Added this for negative users - to give a buffer of 3 months. For example, if a user posts on Nov 1st (
                            # today is Nov 12th, then since there are only 12 days from Nov 1st to 12th, we cant say that the user is a non endo users just because
                            # the user didnt get a chance to post to endo

def Process():
    endo_users = pd.read_csv('endoUsers_2018.csv')
    non_endo_subreddits = pd.read_csv('FinalReddits.csv').iloc[:,0]
    endo_users = endo_users.set_index('user_name').T.to_dict('list')

    pos_users = defaultdict(list)
    neg_users = defaultdict(list)
    outside_users = defaultdict(list)
    d = os.getcwd()
    if not (os.path.exists(os.path.join(d, 'pos3'))):
      os.mkdir('pos3')
      os.mkdir('neg3')
    for sub_red in non_endo_subreddits:
        pos_users, neg_users, outside_users = getEndoBatchUsers(endo_users, sub_red, start_date, init_date, pos_users, neg_users, outside_users)
        print('len of pos users is :{0}', len(pos_users))
        print('len of neg users is :{0}', len(neg_users))
        print('len of neg users is :{0}', len(outside_users))
        print('completed')
        with open('usercount.csv','a') as f:
          s = sub_red + ',' + str(len(pos_users)) + ',' + str(len(neg_users)) + ',' + str(len(outside_users))
          f.write(s)
          f.write('\n')

    d_pos = os.path.join(d, 'pos3')
    d_neg = os.path.join(d, 'neg3')
    if not (os.path.exists(os.path.join(d_pos, sub_red))):
        os.chdir(d_pos)
    for i,user in pos_users.items():
        try:
            file_name = os.path.join(d_pos, i + '.txt')
            with open(file_name, 'a', encoding='utf-8') as f:
                f.write(sub_red)
                f.write('|')
                msg_created_time = datetime.fromtimestamp(user[0][1]).strftime('%c')
                f.write(msg_created_time) #convert to reg date
                f.write('|')
                f.write(str(len(user[0][0])))
                f.write('|')
                f.write(user[0][0])
                f.write('\n')
        except Exception as ex:
            print(ex)

    if not (os.path.exists(os.path.join(d_neg, sub_red))):
        os.chdir(d_neg)
    for i,user in neg_users.items():
        try:
            with open(file_name, 'a', encoding='utf-8') as f:
                    f.write(sub_red)
                    f.write('|')
                    msg_created_time = datetime.fromtimestamp(user[0][1]).strftime('%c')
                    f.write(msg_created_time)  # convert to reg date
                    f.write('|')
                    f.write(str(len(user[0][0])))
                    f.write('|')
                    f.write(user[0][0])
                    f.write('\n')
        except Exception as ex:
            print(ex)



def getEndoBatchUsers(endo_users, sub_red, start_date, init_date,pos_users, neg_users, outside_users):
    d = defaultdict(list)
    start_date_epoch = time.mktime(start_date.timetuple())
    end_date = start_date - relativedelta(hours=int(1))
    end_date_epoch = time.mktime(end_date.timetuple())
    dates = set()
    comment_length = set()
    while end_date > init_date:
        try:
             api_comment_url = 'https://api.pushshift.io/reddit/search/comment/?subreddit=' + sub_red + '&before='+ str(int(start_date_epoch)) + '&after=' + str(int(end_date_epoch)) + '&size=5000&sort=desc'
             url = urllib.request.urlopen(api_comment_url)
             user_data = json.loads(url.read().decode())
             count = 0
             for user_detail in user_data['data']:
                 try:
                     t = user_detail['created_utc']
                     msg_created_time = datetime.fromtimestamp(t).strftime('%c')
                     if 'author' in user_detail and 'body' in user_detail:
                         key = user_detail['author']
                         value = cleanhtml(saxutils.unescape(user_detail['body']))
                         count += 1
                         if len(value) > 0:
                             if key in list(endo_users):
                                 endo_first_comment_time = endo_users[key]
                                 three_months = parser.parse(endo_first_comment_time[0]) - relativedelta(months=int(3))
                                 six_months = parser.parse(endo_first_comment_time[0]) - relativedelta(months=int(9))
                                 if six_months < parser.parse(msg_created_time) < three_months:
                                     if key in pos_users:
                                         pos_users[key].append((value,t, len(value)))
                                     else:
                                         pos_users[key] = [(value,t, len(value))]
                                     dates.add(t)
                                     comment_length.add(len(value))
                                 else:
                                     if key in outside_users:
                                         outside_users[key].append((value,t, len(value)))
                                     else:
                                         outside_users[key] = [(value,t, len(value))]
                             else:
                                 if t in dates or len(value) in comment_length:
                                     if parser.parse(msg_created_time) < cut_off_date_3months:
                                         if key in neg_users:
                                             neg_users[key].append((value,t, len(value)))
                                         else:
                                             neg_users[key] = [(value,t, len(value))]

                 except Exception as ex:
                      print(ex)
             api_submission_url = 'https://api.pushshift.io/reddit/search/submission/?subreddit=' + sub_red + '&before=' + str(int(start_date_epoch)) + '&after=' + str(int(end_date_epoch)) + '&size=5000&sort=desc'
             url = urllib.request.urlopen(api_submission_url)
             user_data = json.loads(url.read().decode())
             print('*****')
             print('count of {0} batch is  {1} between {2} and {3}'.format(sub_red, count, end_date, start_date))
             for user_detail in user_data['data']:
                 try:
                     t = user_detail['created_utc']
                     if 'author' in user_detail and 'title' in user_detail:
                         key = user_detail['author']
                     value = cleanhtml(saxutils.unescape(user_detail['title']))
                     msg_created_time = datetime.fromtimestamp(t).strftime('%c')
                     if len(value) > 0:
                         if key in list(endo_users):
                             endo_first_comment_time = endo_users[key]
                             three_months = parser.parse(endo_first_comment_time[0]) - relativedelta(months=int(3))
                             six_months = parser.parse(endo_first_comment_time[0]) - relativedelta(months=int(9))
                             if six_months < parser.parse(msg_created_time) < three_months:
                                 if key in pos_users:
                                     pos_users[key].append((value, t, len(value)))
                                 else:
                                     pos_users[key] = [(value, t, len(value))]
                                 dates.add(t)
                                 comment_length.add(len(value))
                             else:
                                 if key in outside_users:
                                     outside_users[key].append((value, t, len(value)))
                                 else:
                                     outside_users[key] = [(value, t, len(value))]
                         else:
                             if t in dates or len(value) in comment_length:
                                 if parser.parse(msg_created_time) < cut_off_date_3months:
                                     if key in neg_users:
                                         neg_users[key].append((value, t, len(value)))
                                     else:
                                         neg_users[key] = [(value, t, len(value))]
                 except Exception as ex:
                     print(ex)

             start_date = end_date
             start_date_epoch = end_date_epoch
             end_date = start_date - relativedelta(hours=int(1))
             end_date_epoch = time.mktime(end_date.timetuple())
             print('pos users:{0}'.format(len(pos_users)))
             print('neg users:{0}'.format(len(neg_users)))
             print('outside users:{0}'.format(len(outside_users)))
        except Exception as e:
            print(e)
    return pos_users, neg_users, outside_users

Process()
