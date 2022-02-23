from it.polimi.strategyviz.viz_logging.logger import Logger
from it.polimi.strategyviz.strategy2pta.converter import convert

LOGGER = Logger('MAIN')

LOGGER.info('Starting conversion...')

convert()

LOGGER.msg('Conversion complete.')
