import datetime

class Logger:
    def __init__(self, fileName):
        self.fileName = fileName

    def writeError(self, errorMessage):
        with open(self.fileName, 'a') as f:
            t = datetime.datetime.now()
            f.write(str(errorMessage) + ' ' + str(t) + '\r')
