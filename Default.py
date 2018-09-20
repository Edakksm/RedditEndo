from Reddit_Endo.Init import Init

init = Init()
try:
    sub = init.ConnectToReddit()
    hot_endo = sub.subreddit(init.subReddit).hot(limit = int(init.limit)) # pull from config file
    for hot_msg in hot_endo:
        comments = hot_msg.comments.list()
        for cmt in comments:
            print(cmt.body)
            print(cmt.author)
            print('*********')
except Exception as e:
     init.logger.writeError(e)
