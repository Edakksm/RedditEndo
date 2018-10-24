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
users = defaultdict(int)

def returnUserDemographics(user, n_subRed):
    try:
        duration = init.duration
        six_months = date.today() - relativedelta(months=int(duration))
        sub = init.ConnectToReddit()
        if n_subRed == 'hot':
          endo = sub.subreddit(init.subReddit).hot(limit=100)
        else:
          endo = sub.subreddit(init.subReddit).new(limit=None)
        count = 0
        for hot_msg in endo:
            if not hot_msg.stickied:
                created_date = datetime.utcfromtimestamp(hot_msg.created)
             #  count += 1

                if created_date.date() > six_months:
                    hot_msg.comments.replace_more(limit=5) #
                    comments = hot_msg.comments.list()
                    for cmt in comments:
                        user[cmt.author] += 1

        return user

    except Exception as e:
         init.logger.writeError(e)

sub_reddits = ['hot']
for sub_red in sub_reddits:
      users =  returnUserDemographics(users, sub_red)

sorted_user = OrderedDict(sorted(users.items(), key=lambda kv:kv[1], reverse=True))
users = list(itertools.islice(sorted_user.items(), 0, 20))
#https://github.com/praw-dev/praw/issues?page=2&q=is%3Aissue+is%3Aclosed
users_non_endo_submissions = defaultdict(list)
for user in users:
    try:
        url = urllib.request.urlopen("https://api.pushshift.io/reddit/comment/search?metadata=true&before=0d&limit=1000&sort=desc&author=" + user[0].name)
        user_data = json.loads(url.read().decode())
        comment_num = user_data["metadata"]["results_returned"]
        total = user_data["metadata"]["total_results"]
        users_non_endo_submissions[user[0].name] = defaultdict(int)
        for j in range(0, comment_num):
            comment = user_data["data"][j]
            body = comment['body']
            subreddit = comment['subreddit']
            date = datetime.utcfromtimestamp(comment['created_utc']) #check for 1 year
            users_non_endo_submissions[user[0].name][subreddit] += 1
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
       # init.fileWriter.writeData(users_non_endo_submissions)
    except Exception as e:
        init.logger.writeError(e.message)

# n is the number of most common subreddits that we are interested in
def sort_non_subreddits(non_subreddits, n):
	if non_subreddits is not None and len(non_subreddits)>0:
		try:
			heap = [(-value, key) for key,value in non_subreddits.items()]
			most_common_subreddits = heapq.nsmallest(n, heap)
			most_common_subreddits = [(key, -value) for value,key in most_common_subreddits]
			return most_common_subreddits
	    except Exception as e:
	        init.logger.writeError(e.message)		


# https://www.reddit.com/r/redditdev/comments/8suiqu/scrape_all_submissions_and_comments_made_by_a/

# Create the positive case - users posting in both endo and 5 of other
# Create the negative case - users posting in other reddits but not in endo
    # a. Get the top (how many) non endo reddits
    # b. Get the list of user posting/comments in these reddits
    # c. Get the MINUS of this list and the postitive case list


# What features?



