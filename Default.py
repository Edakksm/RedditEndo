from Init import Init
from collections import defaultdict
from collections import OrderedDict
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta

# https://github.com/arimorcos/getRedditDataset
init = Init()
user = defaultdict(int)
try:
    duration = init.duration
    six_months = date.today() - relativedelta(months=int(duration))
    sub = init.ConnectToReddit()
    hot_endo = sub.subreddit(init.subReddit).hot(limit=None)
    count = 0
    for hot_msg in hot_endo:
        if not hot_msg.stickied:
            created_date = datetime.utcfromtimestamp(hot_msg.created)
         #  count += 1

            if created_date.date() > six_months:
                hot_msg.comments.replace_more(limit=5) #
                comments = hot_msg.comments.list()
                for cmt in comments:
                    user[cmt.author] += 1

    # pick the top users who comment the most
    sorted_user = OrderedDict(sorted(user.items(), key=lambda kv:kv[1], reverse=True))
    for k, v in sorted_user.items():
        init.logger.writeUser(k,v)

except Exception as e:
     init.logger.writeError(e)
