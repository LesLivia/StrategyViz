from typing import List, Set

from tqdm import tqdm

from it.polimi.strategyviz.strategy2pta.pta import PTA, Location, State, StateVariable, NetLocation, Edge
from it.polimi.strategyviz.viz_logging.logger import Logger

LOGGER = Logger('TIGA STRATEGY')


class TigaState:
    opener = 'State: '
    str_format = '{}{}'

    # E.g.
    # State: ( Kim.GoBack ) retry=1
    def __init__(self, state: State):
        self.state = state

    @classmethod
    def parse(cls, line: str):
        if not line.__contains__(cls.opener):
            raise ValueError

        fields = line.split(cls.opener)

        ext_locs_str = fields[1].split(')')[0].replace('(', '').split(' ')
        ext_locs_str = list(filter(lambda s: len(s) > 0, ext_locs_str))
        ext_locs = [NetLocation.parse(s) for s in ext_locs_str]

        state_vars_str = fields[1].split(')')[1].split(' ')
        state_vars_str = list(filter(lambda s: s.__contains__('='), state_vars_str))
        state_vars = [StateVariable.parse(s) for s in state_vars_str]

        return TigaState(State(ext_locs, state_vars))

    def __str__(self):
        return self.str_format.format(self.opener, self.state)


class TigaEdge:
    opener = 'When you are in '
    middle = ', take transition '
    str_format = '{}{}{}{}'

    # E.g.
    # When you are in (time<=15 && T<=2 && T-time<-3), take transition Kim.GoBack->Kim.Aalborg { 1, tau, 1 }
    # When you are in (6<time && time<=15 && T<=2), take transition Kim.Wait->Kim.GoBack { 1, tau, T := 0, retry := 1 }
    def __init__(self, guard: str, next_state: State):
        self.guard = guard
        self.next_state = next_state

    @classmethod
    def parse(cls, line: str, curr_state: TigaState):
        if not line.__contains__(cls.opener):
            raise ValueError

        curr_state_locs = curr_state.state.locs
        curr_state_vars = curr_state.state.vars

        fields = line.split(cls.opener)[1].split(cls.middle)
        guard = fields[0]
        next_str = fields[1]
        next_loc_str = next_str.split(' {')[0].split('->')[1]
        next_loc = NetLocation(next_loc_str.split('.')[0], next_loc_str.split('.')[1])
        next_locs = [next_loc]
        # TODO: hard-coded, just for demo purposes
        if next_loc.label == 'moving':
            next_locs.append(NetLocation('h', 'walk'))
        elif next_loc.label == 'idle':
            next_locs.append(NetLocation('h', 'stand'))
        curr_state_locs = list(filter(lambda l: l.tplt not in [l.tplt for l in next_locs], curr_state_locs))
        next_locs.extend(curr_state_locs)

        next_vars_str = next_str.split(' {')[1].replace(' }\n', '').split(', ')
        next_vars: List[StateVariable] = []
        curr_vars_ids = [v.identifier for v in curr_state_vars]
        for v in next_vars_str:
            if v.__contains__(':='):
                assigment = v.split(' := ')
                if assigment[0] in curr_vars_ids:
                    next_vars.append(StateVariable(assigment[0], assigment[1]))

        next_vars_ids = [v.identifier for v in next_vars]
        for missing_v in set(curr_vars_ids) - set(next_vars_ids):
            missing_value = list(filter(lambda v: v.identifier == missing_v, curr_state_vars))[0].value
            next_vars.append(StateVariable(missing_v, missing_value))

        # TODO: the strategy only contains the destination location for the automaton making the transition
        # but it is possible that such transition causes other automata to switch as well (e.g., through channels),
        # and these should be calculated as well
        return TigaEdge(guard, State(next_locs, next_vars))

    def __str__(self):
        return self.str_format.format(self.opener, self.guard, self.middle, self.next_state)


class TigaWait:
    opener = 'While you are in\t'
    end = ', wait.'
    str_format = '{}{}{}'

    # E.g.
    # While you are in	(time-T<=9 && T<=6 && T-time<-3), wait.
    def __init__(self, guard: str):
        self.guard = guard

    @classmethod
    def parse(cls, line: str):
        if not line.__contains__(cls.opener):
            raise ValueError

        fields = line.split(cls.opener)[1].split(cls.end)
        return TigaWait(fields[0])

    def __str__(self):
        return self.str_format.format(self.opener, self.guard, self.end)


class TigaBlock:
    # E.g.
    # State: ( Kim.GoBack ) retry=1
    # When you are in (time<=15 && T<=2 && T-time<-3), take transition Kim.GoBack->Kim.Aalborg { 1, tau, 1 }
    def __init__(self, state: TigaState, edges: List[TigaEdge], wait: TigaWait):
        self.state = state
        self.edges = edges
        self.wait = wait

    @staticmethod
    def parse(lines: List[str]):
        if len(lines) < 2:
            raise ValueError

        state = TigaState.parse(lines[0])
        edges = []
        for line in lines[1:]:
            try:
                edges.append(TigaEdge.parse(line, state))
            except ValueError:
                pass

        wait = None
        if len(edges) == 0:
            for line in lines[1:]:
                try:
                    wait = TigaWait.parse(line)
                except ValueError:
                    raise ValueError

        return TigaBlock(state, edges, wait)

    def __str__(self):
        res = str(self.state)
        if len(self.edges) > 0:
            for e in self.edges:
                res += str(e)
        else:
            res += str(self.wait)
        return res + '\n'


class TigaStrategy:
    def __init__(self, name: str, blocks: List[TigaBlock], initial_state: State):
        self.name = name
        self.blocks = blocks
        self.initial_state = initial_state

    def to_pta(self, network: List[PTA], view=False):
        LOGGER.info('Converting TIGA strategy to TA...')

        locations: Set[Location] = set()
        edges: Set[Edge] = set()
        for b in tqdm(self.blocks):
            # TODO: main issue, the strategy explodes
            if len(locations) >= 100 or len(edges) >= 50:
                LOGGER.warn('Truncating due to excessive size.')
                break
            curr_loc = Location(b.state.state.locs, len(set(b.state.state.locs) - set(self.initial_state.locs)) == 0)
            locations.add(curr_loc)

            if len(b.edges) == 0:
                external_pta: PTA = network[0]
                edges.update(set(filter(lambda e: e.start.label == curr_loc.label, external_pta.edges)))

            for e in b.edges:
                new_guard = ''
                for v in b.state.state.vars:
                    new_guard += str(v) + '&&\n'
                new_guard = new_guard + e.guard
                edges.add(Edge(new_guard, '', '', curr_loc, Location(e.next_state.locs)))

        # TODO Clearly, it only works if there is only one pta in the network
        # (or, at least, if there is only one with controllable edges)
        bps_ids = [bp.label for bp in network[0].branchpoints]
        edges_from_bps = list(filter(lambda e: e.start.label in bps_ids, network[0].edges))
        edges.update(edges_from_bps)

        pta = PTA(self.name, list(locations), list(edges), network[0].branchpoints)

        if view:
            pta.plot()

        LOGGER.info('TA successfully created.')
        return pta
