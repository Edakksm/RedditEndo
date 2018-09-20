import praw

class RedditConnect:
    def __init__(self, clientID, clientSecret,userName, password):
        self.clientID = clientID
        self.clientSecret = clientSecret
        self.userName = userName
        self.password = password

    def Connect(self):
        return praw.Reddit(client_id =self.clientID, client_secret= self.clientSecret, username=self.userName, paswsword =self.password,  user_agent='edakksm')

