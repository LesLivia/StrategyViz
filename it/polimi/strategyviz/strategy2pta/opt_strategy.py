from typing import Dict, List

from it.polimi.strategyviz.strategy2pta.pta import State, NetLocation, StateVariable
from it.polimi.strategyviz.viz_logging.logger import Logger

LOGGER = Logger('OPTIMIZED STRATEGY')


class OptimizedState:
    def __init__(self, state: State):
        self.state = state

    @staticmethod
    def parse(key: str, statevars: List[str], location_names: Dict):
        statevars_values = key.replace('(', '').replace(')', '').split(',')

        state_locs: List[NetLocation] = []
        state_vars: List[StateVariable] = []
        for i, v in enumerate(statevars_values):
            if statevars[i] in location_names.keys():
                curr_loc_str = location_names[statevars[i]][v]
                state_locs.append(NetLocation(statevars[i].split('.')[0], curr_loc_str))
            else:
                state_vars.append(StateVariable(statevars[i], v))

        return OptimizedState(State(state_locs, state_vars))

    def __str__(self):
        return str(self.state)


class Regressor:
    def __init__(self, state: OptimizedState, minimize: bool, weights: Dict[str, float]):
        self.state = state
        self.minimize = minimize
        self.weights = weights

    @staticmethod
    def parse(key: str, d: Dict, statevars: List[str], location_names: Dict, actions: List[str]):
        state = OptimizedState.parse(key, statevars, location_names)

        minimize = True if d['minimize'] == '1' else False

        weights: Dict[str, float] = {}
        for a in d['regressor']:
            weights[actions[a]] = d['regressor'][a]

        return Regressor(state, minimize, weights)

    def __str__(self):
        return str(self.state) + '\n' + str(self.minimize) + '\n' + str(self.weights)


class OptimizedStrategy:

    def __init__(self, name: str, regressors: List[Regressor]):
        self.name = name
        self.regressors = regressors
