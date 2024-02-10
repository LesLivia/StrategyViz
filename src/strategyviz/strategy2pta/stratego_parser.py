import json
from typing import List, Dict

from tqdm import tqdm

from src.strategyviz.strategy2pta.opt_strategy import OptimizedStrategy, Regressor
from src.strategyviz.viz_logging.logger import Logger

LOGGER = Logger('STRATEGO PARSER')


def parse_optimized_strategy(name: str, data: str):
    json_content = json.loads(data)

    regressors_dict = json_content['regressors']
    regressors: Dict[str, List[str]] = dict()
    state_vars = json_content['statevars']
    locationnames = json_content['locationnames']
    actions = json_content['actions']

    for state_str in tqdm(regressors_dict):
        new_regressor = Regressor.parse(state_str, regressors_dict[state_str], state_vars, locationnames, actions)
        # TODO: fix that state also depends on other automata
        regressors[str(new_regressor)] = new_regressor.best_actions

    LOGGER.info('Found {} regressors.'.format(len(regressors)))

    return OptimizedStrategy(name, regressors)
