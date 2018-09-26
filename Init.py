from RedditConnect import RedditConnect
from Logger import Logger
from ConfigParser import ConfigParse

class Init:
    def __init__(self):
        config = ConfigParse()
        self.client_ID = config.__getattr__('client_id')
        self.client_Secret = config.__getattr__('client_secret')
        self.userName = config.__getattr__('username')
        self.password = config.__getattr__('password')
        self.subReddit = config.__getattr__('subreddit')
        self.limit =  config.__getattr__('limit')
        self.errorlogFileName =  config.__getattr__('errorlogfile')
        self.userlogFileName =  config.__getattr__('userlogfile')
        self.logger = Logger(self.errorlogFileName, self.userlogFileName)
        self.duration = config.__getattr__('duration')


    def ConnectToReddit(self):
            return RedditConnect(self.client_ID, self.client_Secret, self.userName, self.password).Connect()


