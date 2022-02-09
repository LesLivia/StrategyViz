import configparser
import sys

from it.polimi.strategyviz.strategy2pta.tigaparser import parse_tiga_strategy, TigaStrategy
from it.polimi.strategyviz.upp2pta.converter import parse_uppaal_model
from it.polimi.strategyviz.viz_logging.logger import Logger

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
    with open(TIGA_PATH) as tiga_strategy_file:
        lines = tiga_strategy_file.readlines()
        tiga_strategy: TigaStrategy = parse_tiga_strategy(sys.argv[2], lines)
        EXISTING_PTA = parse_uppaal_model()
        tiga_strategy.to_pta(view=True)

    LOGGER.info("TIGA strategy successfully parsed.")

    LOGGER.info("Parsing Stratego strategy...")
    with open(STRATEGO_PATH) as stratego_strategy:
        # TODO
        lines = stratego_strategy.readlines()
    LOGGER.info("Stratego strategy successfully parsed.")
