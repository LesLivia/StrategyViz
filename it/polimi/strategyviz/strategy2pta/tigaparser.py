from typing import List

from tqdm import tqdm

from it.polimi.strategyviz.strategy2pta.pta import State, StateVariable, NetLocation
from it.polimi.strategyviz.strategy2pta.tiga_strategy import TigaBlock, TigaStrategy
from it.polimi.strategyviz.viz_logging.logger import Logger

LOGGER = Logger('TIGA PARSER')


def parse_tiga_strategy(name: str, file_content: List[str]):
    initial_str = file_content[file_content.index('Initial state:\n') + 1]
    initial_locs_str = initial_str.split(' ) ')[0].replace('( ', '').split(' ')
    initial_locs = [NetLocation(s.split('.')[0], s.split('.')[1]) for s in initial_locs_str]
    initial_vars_str = initial_str.split(' ) ')[1].replace(' \n', '').split(' ')
    initial_vars = [StateVariable(s.split('=')[0], s.split('=')[1]) for s in initial_vars_str]
    initial_state = State(initial_locs, initial_vars)

    start_index = [i for i, line in enumerate(file_content) if line.__contains__('Strategy to')][0]
    block_lines = file_content[start_index + 1:]
    str_blocks = []
    for line in block_lines:
        if line == '\n':
            str_blocks.append([])
        else:
            str_blocks[-1].append(line)

    blocks = []
    for block in tqdm(str_blocks):
        try:
            blocks.append(TigaBlock.parse(block))
        except ValueError:
            LOGGER.error("An error occurred while parsing the TIGA strategy.")

    return TigaStrategy(name, blocks, initial_state)
