import configparser
import sys

from it.polimi.strategyviz.logging.logger import Logger

config = configparser.ConfigParser()
config.sections()
config.read(sys.argv[1])
config.sections()

LOGGER = Logger('STRATEGY2PTA CONVERTER')


def convert():
    if len(sys.argv) < 4:
        LOGGER.error('Not enough input parameters.')
        raise RuntimeError

    STRATEGIES_PATH = config['STRATEGY CONFIGURATION']['STRATEGY_PATH']
    TIGA_PATH = STRATEGIES_PATH + sys.argv[2] + config['STRATEGY CONFIGURATION']['TIGA_EXT']
    STRATEGO_PATH = STRATEGIES_PATH + sys.argv[3] + config['STRATEGY CONFIGURATION']['STRATEGO_EXT']

    with open(TIGA_PATH) as tiga_strategy:
        lines = tiga_strategy.readlines()
        print(len(lines))

    with open(STRATEGO_PATH) as stratego_strategy:
        lines = stratego_strategy.readlines()
        print(len(lines))
