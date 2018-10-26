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

# https://github.com/arimorcos/getRedditDataset
init = Init()
users = defaultdict(date)
six_months = date.today() - relativedelta(months=int(init.end_duration))

def returnUserDemographics(user, n_subRed):
    try:
        sub = init.ConnectToReddit()
        endo = sub.subreddit(n_subRed).hot(limit=None)
        for hot_msg in endo:
            if not hot_msg.stickied:
                created_date = datetime.utcfromtimestamp(hot_msg.created)
                if created_date.date() > six_months:
                    hot_msg.comments.replace_more(limit=5) #
                    comments = hot_msg.comments.list()
                    for cmt in comments:
                       # user[cmt.author] += 1 We are taking all the users
                       if hasattr(cmt, 'author') and hasattr(cmt.author, 'name'):
                         if cmt.author.name not in user:
                            user[cmt.author.name] = created_date.date()
                         else:
                            if created_date.date() < user[cmt.author.name]:
                                user[cmt.author.name] = created_date.date()

        return user

    except Exception as e:
         init.logger.writeError(e)

def createPositiveNegativeCases(users,positive_users, negative_users, n_subRed):
    try:
        sub = init.ConnectToReddit()
        endo = sub.subreddit(n_subRed).hot(limit=None)
        for hot_msg in endo:
            if not hot_msg.stickied:
                created_date = datetime.utcfromtimestamp(hot_msg.created)
                hot_msg.comments.replace_more(limit=5) #
                comments = hot_msg.comments.list()
                for cmt in comments:
                   if hasattr(cmt, 'author') and hasattr(cmt.author, 'name'):
                     if cmt.author.name in users:
                         user_endo_comment_createdDate = users[cmt.author.name]
                         three_months = user_endo_comment_createdDate - relativedelta(months=int(init.start_duration))
                         six_months = user_endo_comment_createdDate - relativedelta(months=int(init.end_duration))
                         if created_date.date() < three_months and created_date.date() > six_months:
                             positive_users[cmt.author.name] = 1
                     else:
                         negative_users[cmt.author.name] = 1

        return  positive_users, negative_users

    except Exception as e:
         init.logger.writeError(e)

def sort_non_subreddits(non_subreddits, n):
    if non_subreddits is not None and len(non_subreddits)>0:
        try:
            heap = [(-value, key) for key,value in non_subreddits.items()]
            most_common_subreddits = heapq.nsmallest(n, heap)
            most_common_subreddits = [(key, -value) for value,key in most_common_subreddits if value < -10]
            return most_common_subreddits

        except Exception as e:
            init.logger.writeError(e.message)

sub_reddits = init.subReddit.split(',')
for sub_red in sub_reddits:
      users =  returnUserDemographics(users, sub_red)

#sorted_user = OrderedDict(sorted(users.items(), key=lambda kv:kv[1], reverse=True))
#users = sorted_user # TO ASK: Should we take all these users?
#users = list(itertools.islice(sorted_user.items(), 0, 20))
#https://github.com/praw-dev/praw/issues?page=2&q=is%3Aissue+is%3Aclosed
users_non_endo_submissions = defaultdict(list)

for user_name, first_submission_date in users.items():
    try:
            url = urllib.request.urlopen("https://api.pushshift.io/reddit/comment/search?metadata=true&before=0d&limit=1000&sort=desc&author=" + user_name)
            user_data = json.loads(url.read().decode())
            comment_num = user_data["metadata"]["results_returned"]
            total = user_data["metadata"]["total_results"]
            users_non_endo_submissions[user_name] = defaultdict(int)
            for j in range(0, comment_num):
                comment = user_data["data"][j]
                body = comment['body']
                subreddit = comment['subreddit']
                date = datetime.utcfromtimestamp(comment['created_utc']) # take those comments which were posted 3 months prior to the date of first
                                            # post of the user in Endo subreddit and within 1 year
               # three_months = first_submission_date - relativedelta(months=int(init.start_duration))
               # six_months = first_submission_date - relativedelta(months=int(init.end_duration))
              #  if  date.date() < six_months:
                users_non_endo_submissions[user_name][subreddit] += 1
    except Exception as e:
        print(e)
        init.logger.writeError(e.message)

# sort each user with the number of subreddit

non_subreddits = defaultdict(int)
if users_non_endo_submissions is not None and len(users_non_endo_submissions) > 0:
    try:
        for i,j in users_non_endo_submissions.items():
            for k,v in j.items():
                non_subreddits[k] += 1
        #init.fileWriter.writeData(users_non_endo_submissions)
    except Exception as e:
        init.logger.writeError(e.message)

most_common_subreddits = sort_non_subreddits(non_subreddits, len(non_subreddits)- 1)
non_subreddits = [reddit for reddit in most_common_subreddits if reddit[0] not in sub_reddits]
print('Completed')
# n is the number of most common subreddits that we are interested in

# Get the users posting in each of these subreddits
positive_users = defaultdict(int)
negative_users = defaultdict(int)
for sub_red in non_subreddits:
     positive_users, negative_users =  createPositiveNegativeCases(users,positive_users,negative_users , sub_red[0])

print('Completed')
print(len(positive_users))
print(len(negative_users))
#positive_users = users_non_endo_submissions # positive cases
#negative_users = [user for user in users_posting_in_non_endo_group if user not in positive_users ]


