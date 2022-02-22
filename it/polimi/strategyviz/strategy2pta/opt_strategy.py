from typing import Dict, List

from it.polimi.strategyviz.strategy2pta.pta import State, NetLocation, StateVariable, PTA, Edge
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

        minimize = True if d['minimize'] == 1 else False

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

    def refine_pta(self, pta: PTA):
        LOGGER.info('Refining TIGA strategy...')

        edges_to_delete: List[Edge] = []
        for reg in self.regressors:
            f = min if reg.minimize else max
            best_weight = f(list(reg.weights.values()))
            to_be_deleted = [e for e in list(reg.weights.keys()) if reg.weights[e] != best_weight]
            to_be_deleted = [e.split(' {')[0].split('->')[1] for e in to_be_deleted]
            curr_locs = '\n'.join([str(x) for x in reg.state.state.locs])
            for e in pta.edges:
                same_start = curr_locs == str(e.start)
                same_end = str(e.end) in to_be_deleted
                same_guard = all([e.guard.__contains__(str(v)) for v in reg.state.state.vars])
                if same_start and same_end and same_guard:
                    edges_to_delete.append(e)

        pta.edges = list(set(pta.edges) - set(edges_to_delete))
        pta.name = 'optimized_' + pta.name

        LOGGER.info('TIGA strategy successfully refined.')
        return pta
