from Reddit_Endo.RedditConnect import RedditConnect
from Reddit_Endo.Logger import Logger
from Reddit_Endo.ConfigParser import ConfigParse

class Init:
    def __init__(self):
        config = ConfigParse()
        self.client_ID = config.__getattr__('client_id')
        self.client_Secret = config.__getattr__('client_secret')
        self.userName = config.__getattr__('username')
        self.password = config.__getattr__('password')
        self.subReddit = config.__getattr__('subreddit')
        self.limit =  config.__getattr__('limit')
        self.logFileName =  config.__getattr__('logfile')
        self.logger = Logger(self.logFileName)


    def ConnectToReddit(self):
            return RedditConnect(self.client_ID, self.client_Secret, self.userName, self.password).Connect()


