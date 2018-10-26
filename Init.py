from RedditConnect import RedditConnect
from Logger import Logger
from ConfigParser import ConfigParser
from FileWriter import FileWriter


class Init:
    def __init__(self):
        config = ConfigParser()
        self.client_ID = config.__getattr__('client_id')
        self.client_Secret = config.__getattr__('client_secret')
        self.userName = config.__getattr__('username')
        self.password = config.__getattr__('password')
        self.subReddit = config.__getattr__('subreddit')
        self.limit =  config.__getattr__('limit')
        self.logFileName =  config.__getattr__('logfile')
        self.userFileName = config.__getattr__('userfile')
        self.start_duration = config.__getattr__('start_duration')
        self.end_duration = config.__getattr__('end_duration')
        self.pushShiftAPI = config.__getattr__('pushshiftapi')
        self.logger = Logger(self.logFileName)
        self.fileWriter = FileWriter(self.userFileName)

    def ConnectToReddit(self):
            return RedditConnect(self.client_ID, self.client_Secret, self.userName, self.password).Connect()


