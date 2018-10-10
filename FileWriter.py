import pandas as pd

class FileWriter:
    def __init__(self, fileName):
        self.fileName = fileName

    def writeData(self, datam):
        with open(self.fileName, 'a') as f:
            for k,v in datam.items():
                f.write(k)
                f.write('$$')
                f.write('  ')
                for k1,v1 in v.items():
                    f.write(k1)
                    f.write(':')
                    f.write(str(v1))
                    f.write(' ')
                f.write('\n')
                f.write('\n')
                f.write('\n')
