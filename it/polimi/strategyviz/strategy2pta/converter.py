import configparser
import sys

from it.polimi.strategyviz.logging.logger import Logger
from it.polimi.strategyviz.strategy2pta.tigaparser import parse_tiga_strategy

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

    LOGGER.info("Parsing TIGA strategy...")
    with open(TIGA_PATH) as tiga_strategy:
        lines = tiga_strategy.readlines()
        parse_tiga_strategy(lines)
    LOGGER.info("TIGA strategy successfully parsed.")

    with open(STRATEGO_PATH) as stratego_strategy:
        lines = stratego_strategy.readlines()
        print(len(lines))
