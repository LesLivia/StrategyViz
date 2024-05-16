from typing import Dict, List

from tqdm import tqdm

from src.strategyviz.strategy2pta.pta import State, NetLocation, StateVariable, PTA, Edge
from src.strategyviz.viz_logging.logger import Logger

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
    def __init__(self, state: OptimizedState, best_actions: List[str], weight: float):
        self.state = state
        self.best_actions = best_actions
        self.payoff = weight

    @staticmethod
    def parse(key: str, d: Dict, statevars: List[str], location_names: Dict, actions: Dict[str, str]):
        state = OptimizedState.parse(key, statevars, location_names)

        minimize = True if d['minimize'] == 1 else False
        fun = min if minimize else max

        weights: Dict[float, List[str]] = dict()
        for a in actions:
            starting_loc = actions[a].split('->')
            if actions[a] == 'WAIT' or str(state.state.locs[0]) != starting_loc[0]:
                continue

            if a in d['regressor']:
                # we build a dictionary with keys=weights in a regressor
                # and values=list actions with such weight
                # the list is necessary in case multiple actions have the same weight
                try:
                    weights[float(d['regressor'][a])].append(actions[a])
                except KeyError:
                    weights[float(d['regressor'][a])] = [actions[a]]
            # TODO: what does it mean when an action is not part of the regressor?

        best_weight = fun(weights.keys())

        if minimize:
            return [Regressor(state, weights[w], -w) for w in weights if w == best_weight]
        else:
            return [Regressor(state, weights[w], w) for w in weights if w == best_weight]

    def __str__(self):
        return str(self.state)  # + '\n' + str(self.minimize) + '\n' + str(self.weights)

    def __hash__(self):
        return hash(str(self))


class OptimizedStrategy:
    def __init__(self, name: str, regressors: List[Regressor]):
        self.name = name
        self.regressors = regressors

    def refine_pta(self, pta: PTA):
        LOGGER.info('Refining TIGA strategy...')

        all_edges = len(pta.edges)

        edges_to_delete: List[Edge] = []
        for e in tqdm(pta.edges):
            edge_key = str(e.start) + ', \n' + \
                       ', '.join([x for x in e.guard.split('&&\n') if x.__contains__('==')]) + ', '
            if edge_key in list(self.regressors.keys()):
                best_actions = self.regressors[edge_key]
                best_actions_dest = [a.split(' ')[0].split('->')[1] for a in best_actions]
                if str(e.end) not in best_actions_dest:
                    edges_to_delete.append(e)

        pta.edges = list(set(pta.edges) - set(edges_to_delete))
        pta.name = 'optimized_' + pta.name

        LOGGER.info('TIGA strategy successfully refined: {}/{} edges eliminated.'
                    .format(len(edges_to_delete), all_edges))
        return pta
