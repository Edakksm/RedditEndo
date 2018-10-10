import configparser

class ConfigParser:

    def __init__(self):
        cfg = configparser.ConfigParser()
        cfg.read('config.ini')
        self.configuration = dict(cfg.items('configDetail'))

    def __getattr__(self, item):
        return self.configuration[item]
