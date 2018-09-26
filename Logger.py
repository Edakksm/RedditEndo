import datetime

class Logger:
    def __init__(self, errorfileName, userfileName):
        self.errorfileName = errorfileName
        self.userfileName= userfileName

    def writeError(self, errorMessage):
        with open(self.errorfileName, 'a') as f:
            t = datetime.datetime.now()
            f.write(str(errorMessage) + ' ' + str(t) + '\r')

    def writeUser(self, user, count):
        with open(self.userfileName, 'a') as f:
            f.write(str(user) + ' ' + str(count) + '\r')
