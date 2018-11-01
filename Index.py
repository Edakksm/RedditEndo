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
    return users


def getEndoSubredditUser(users, sub_red):
    start_date = datetime.now()
    init_date = parser.parse(init.initDate)
    user_data = getEndoBatchUsers2(sub_red, start_date, init_date)
    for batch in user_data:
        for items in batch:
            author = items['author']
            created_date = datetime.utcfromtimestamp(items['created_utc'])
            if author not in users:
                users[author] = created_date
            else:
                if created_date < users[author]:
                    users[author] = created_date
    print(len(users))
    return users

def getNonEndoSubredditUsers(nonEndoSubreddits):
    users = defaultdict(date)
    start_date = datetime.now()
    init_date = parser.parse(init.initDate)
    for sub_red in nonEndoSubreddits:
        users = getEndoBatchUsers3(users, sub_red)
    return users

#def getEndoBatchUsers3(users):


def getEndoBatchUsers2(sub_red, start_date, init_date):
    users = []
   # start_date = datetime.now()
    start_date_epoch = time.mktime(start_date.timetuple())
    end_date = datetime.now() - relativedelta(months=int(1))
    end_date_epoch = time.mktime(end_date.timetuple())
  #  init_date = parser.parse(init.initDate)
    while end_date > init_date:
         api_url = 'https://api.pushshift.io/reddit/search/comment/?subreddit=' + sub_red + '&before='+ str(int(start_date_epoch)) + '&after=' + str(int(end_date_epoch)) + '&size=5000&sort=desc'
         url = urllib.request.urlopen(api_url)
         user_data = json.loads(url.read().decode())
         users.append(user_data['data'])
         start_date = end_date
         start_date_epoch = end_date_epoch
         end_date = start_date - relativedelta(months=int(1))
         end_date_epoch = time.mktime(end_date.timetuple())
    return users

def getRedditsOfEndoUsers(users):
    users_non_endo_submissions = defaultdict(list)
    for user_name, first_submission_date in users.items():
            url = urllib.request.urlopen("https://api.pushshift.io/reddit/comment/search?metadata=true&before=0d&limit=1000&sort=desc&author=" + user_name)
            user_data = json.loads(url.read().decode())
            comment_num = user_data["metadata"]["results_returned"]
            total = user_data["metadata"]["total_results"]
            users_non_endo_submissions[user_name] = defaultdict(int)
            for j in range(0, comment_num):
                comment = user_data["data"][j]
                body = comment['body']
                subreddit = comment['subreddit']
                users_non_endo_submissions[user_name][subreddit] += 1
    return users_non_endo_submissions

   # return sort_non_subreddits(users_non_endo_submissions, len(users_non_endo_submissions))

def sort_non_subreddits(non_subreddits, n):
    if non_subreddits is not None and len(non_subreddits)>0:
        try:
            heap = [(-value, key) for key,value in non_subreddits.items()]
            most_common_subreddits = heapq.nsmallest(n, heap)
            most_common_subreddits = [(key, -value) for value,key in most_common_subreddits]
            return most_common_subreddits
        except Exception as e:
            init.logger.writeError(e.message)
            return non_subreddits

def createPositiveNegativeCases(endo_users, non_subreddits):
    for reddit in non_subreddits:
         pos,positive_users, negative_users = process(endo_users, pos,positive_users, negative_users,reddit)

def WriteStatistics_NonEndoReddits(nonEndoSubReddits, endo_user_count):
    import  csv
    non_reddit = collections.defaultdict(dict)
    s = ''
    with open('statistics.csv', 'w', newline='') as f:
        filewriter = csv.writer(f)
        for subreddit, count in nonEndoSubReddits:
            filewriter.writerow([subreddit,count,(count/endo_user_count) * 100])
           # filewriter.writerow()

          #    s = subreddit + '\t' + str(count) + '\t' + str(count/endo_user_count * 100)
           #   f.write(subreddit)
            #  f.write(' ')
             # f.write(str(count))
              #f.write(' ')
              ##f.write(str(count/endo_user_count))
              #f.write('\n')
              #  f.write(subreddit)
               # f.write('\t')
              #  f.write(':')
                #f.write(str(count))
                #f.write('\t')
                #f.write(str((count/endo_user_count)))
                #f.write('\n')
          #  non_reddit[subreddit]['count'] = count
           # non_reddit[subreddit]['percentage'] = count/endo_user_count * 100
           # f.write(str(non_reddit[subreddit]))
           # f.write('\n')

def process(users, pos,positive_users, negative_users, n_subRed):
        sub = init.ConnectToReddit()
        cnt = 0
        endo = sub.subreddit(n_subRed).hot(limit=None)
        for hot_msg in endo:
            if not hot_msg.stickied:
                created_date = datetime.utcfromtimestamp(hot_msg.created)
                hot_msg.comments.replace_more(limit=5) #
                comments = hot_msg.comments.list()
                for cmt in comments:
                   cnt = cnt + 1
                   if hasattr(cmt, 'author') and hasattr(cmt.author, 'name'):
                     start_time = datetime.now()
                     if cmt.author.name not in positive_users and cmt.author.name not in negative_users:
                         if cmt.author.name in users:
                             user_endo_comment_createdDate = users[cmt.author.name]
                             three_months = user_endo_comment_createdDate - relativedelta(months=int(init.start_duration))
                             six_months = user_endo_comment_createdDate - relativedelta(months=int(12))
                             if created_date.date() < three_months and created_date.date() > six_months:
                                 positive_users[cmt.author.name] = 1
                             if created_date.date() < user_endo_comment_createdDate:
                                 pos[cmt.author.name] = 1
                          #   dates[cmt.author.name]['3months'] = three_months
                           #  dates[cmt.author.name]['createdDate'] = created_date.date()
                            # dates[cmt.author.name]['6months'] = six_months
                             #with open('dates2.csv','a') as f:
                              #   f.write(str(dates[cmt.author.name]))
                               #  f.write('\n')
                         else:
                             negative_users[cmt.author.name] = 1
                         end_time = datetime.now()
                         s = (end_time - start_time).seconds
                 #    print(s)
        print('len of pos user is {0}'.format(len(pos)))
        return  pos,positive_users, negative_users

init = Init()
endo_users = getEndoUsers()
subreddits = getRedditsOfEndoUsers(endo_users)
non_subreddits = defaultdict(int)

if subreddits is not None and len(subreddits) > 0:
    try:
        for i,j in subreddits.items():
            for k,v in j.items():
                non_subreddits[k] += 1
     #   init.fileWriter.writeData(users_non_endo_submissions)
    except Exception as e:
        init.logger.writeError(e.message)
non_endo_subreddits = [reddit for reddit in non_subreddits if reddit[0].lower() not in init.subReddit.split(',')]
non_endo_subreddits = sort_non_subreddits(non_subreddits, len(non_subreddits))
WriteStatistics_NonEndoReddits(non_endo_subreddits,len(endo_users))
#non_endo_subreddit_users = getNonEndoSubredditUsers()

#positive_users, negative_users = CreatePositiveNegativeUsers(endo_users, non_subreddits)
