from it.polimi.strategyviz.viz_logging.logger import Logger
from it.polimi.strategyviz.strategy2pta.converter import convert
from it.polimi.strategyviz.pta2upp.uppgenerator import to_uppaal_model

LOGGER = Logger('MAIN')

LOGGER.info('Starting conversion...')

strategized_pta = convert()

LOGGER.msg('Conversion complete.')

LOGGER.info('Starting Uppaal model generation...')

to_uppaal_model(strategized_pta)

LOGGER.msg('Uppaal model successfully generated.')
