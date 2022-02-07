import sys
from enum import Enum
import configparser
from datetime import datetime

config = configparser.ConfigParser()
config.sections()
config.read(sys.argv[1])
config.sections()


class LogLevel(Enum):
    INFO = 1
    DEBUG = 2
    WARNING = 3
    ERROR = 4
    MSG = 99

    def __str__(self):
        if self.value == 1:
            return 'INFO'
        elif self.value == 2:
            return 'DEBUG'
        elif self.value == 3:
            return 'WARNING'
        elif self.value == 4:
            return 'ERROR'
        elif self.value == 99:
            return 'MSG'
        else:
            return ''

    @staticmethod
    def parse_str(s):
        if s == 'INFO':
            return LogLevel.INFO
        elif s == 'DEBUG':
            return LogLevel.DEBUG
        elif s == 'WARNING':
            return LogLevel.WARNING
        elif s == 'ERROR':
            return LogLevel.ERROR
        elif s == 'MSG':
            return LogLevel.MSG
        else:
            return None


# INIT LOGGING LEVEL BASED ON CONFIG FILE
if 'LoggingLevel' in config['DEFAULT']:
    MIN_LOG_LEVEL = LogLevel.parse_str(config['DEFAULT']['LoggingLevel']).value
else:
    MIN_LOG_LEVEL = LogLevel.WARNING.value


#

class Logger:
    format = "\n[{}:{}] ({})\t{}"

    def __init__(self, speaker):
        self.speaker = speaker
        pass

    def info(self, msg):
        if MIN_LOG_LEVEL <= LogLevel.INFO.value:
            print(self.format.format(self.speaker, datetime.now(), str(LogLevel.INFO), msg))

    def debug(self, msg):
        if MIN_LOG_LEVEL <= LogLevel.DEBUG.value:
            print(self.format.format(self.speaker, datetime.now(), str(LogLevel.DEBUG), msg))

    def warn(self, msg):
        if MIN_LOG_LEVEL <= LogLevel.WARNING.value:
            print(self.format.format(self.speaker, datetime.now(), str(LogLevel.WARNING), msg))

    def error(self, msg):
        if MIN_LOG_LEVEL <= LogLevel.ERROR.value:
            print(self.format.format(self.speaker, datetime.now(), str(LogLevel.ERROR), msg))

    def msg(self, msg):
        if MIN_LOG_LEVEL <= LogLevel.MSG.value:
            print(self.format.format(self.speaker, datetime.now(), str(LogLevel.MSG), msg))
