import configparser
import math
from typing import List

from graphviz import Digraph
from tqdm import tqdm

from src.strategyviz.viz_logging.logger import Logger
from src.strategyviz.z3gen.z3constrgenerator import guards2singleconstr

config = configparser.ConfigParser()
config.sections()
config.read("./resources/config/config.ini")
config.sections()

LOGGER = Logger('PTA')


class NetLocation:
    def __init__(self, tplt: str, label: str):
        self.tplt = tplt
        self.label = label

    @staticmethod
    def parse(line: str):
        fields = line.split('.')
        return NetLocation(fields[0], fields[1])

    def __str__(self):
        return self.tplt + '.' + self.label

    def __eq__(self, other):
        return self.tplt == other.tplt and self.label == other.label

    def __hash__(self):
        return hash(str(self))


class StateVariable:
    def __init__(self, identifier: str, value):
        self.identifier = identifier
        self.value = value

    @staticmethod
    def parse(line: str):
        fields = line.split('=')
        return StateVariable(fields[0], fields[1])

    def __str__(self):
        return self.identifier + '==' + str(self.value)

    def __eq__(self, other):
        return self.identifier == other.identifier and self.value == other.value

    def __hash__(self):
        return hash(str(self))


class State:
    def __init__(self, locs: List[NetLocation], vars: List[StateVariable]):
        self.locs = locs
        self.vars = vars

    def __str__(self):
        res = ''
        for l in self.locs:
            res += str(l) + ', '

        res += '\n'
        for v in self.vars:
            res += str(v) + ', '

        return res

    def __eq__(self, other):
        return len(set(self.locs) - set(other.locs)) == 0 and len(set(self.vars) - set(other.vars)) == 0


class Location:
    kind = 'LOC'

    def __init__(self, net_locs: List[NetLocation], initial=False, invariant: str = None, urgent: int = 0):
        self.net_locs = net_locs
        self.initial = initial
        self.label = ''
        for i, l in enumerate(net_locs):
            self.label += str(l)
            if i < len(net_locs) - 1:
                self.label += ',\n'
        self.invariant = invariant if invariant is not None else ''
        self.urgent = urgent  # 0: not urgent, not committed, 1: urgent, 2: committed

    def __str__(self):
        return self.label

    def __eq__(self, other):
        return self.label == other.label

    def __hash__(self):
        return hash(str(self))


class Edge:
    def __init__(self, guard: str, sync: str, update: str, start, end,
                 weight: str = None, controllable: bool = False):
        guard = guard.replace('(', '').replace(')', '').replace(' && ', ' &&\n')
        self.guard = guard
        self.sync = sync
        self.update = update
        self.start = start
        self.end = end
        self.weight = weight
        self.controllable = controllable

    def __str__(self):
        return self.guard + ' ' + self.sync + ' { ' + self.update + ' } ' + self.start.label + '->' + self.end.label

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))


class BranchPoint:
    kind = 'BP'

    def __init__(self, id: str):
        self.id = id
        self.label = id

    def __eq__(self, other):
        return self.label == other.label

    def __str__(self):
        return self.label

    def __hash__(self):
        return hash(str(self))


class PTA:
    def __init__(self, name: str, locs: List[Location], edges: List[Edge], bps: List[BranchPoint] = None,
                 declarations: str = ''):
        self.name = name
        self.locations = locs
        self.edges = edges
        self.branchpoints = bps if bps is not None else []
        self.declarations = declarations

    @staticmethod
    def fix_label_for_html(s: str, color=None):
        if s == '':
            return s
        res = s.replace('&', '&amp;')
        res = res.replace('<', '&lt;')
        res = res.replace('>', '&gt;')
        res = res.replace('\n', '<BR/>')
        if color is not None:
            res = '<font color=\'{}\'>'.format(color) + res + '</font>'
        return res

    def to_digraph(self):
        GREEN = '#3a9e05'
        RED = '#ad0900'
        BLUE = 'blue'
        PURPLE = '#ba03fc'

        gra = Digraph(self.name)

        for l in self.locations:
            invariant = PTA.fix_label_for_html(l.invariant, PURPLE)
            if l.urgent > 0:
                urgency_label = '(U) ' if l.urgent == 1 else '(C) '
            else:
                urgency_label = ''
            label = "<" + urgency_label + l.label + "<BR/>" + invariant + ">"

            if l.initial:
                gra.node(l.label, label=label, _attributes={'peripheries': '2'})
            else:
                gra.node(l.label, label=label)

        for i, e in enumerate(self.edges):
            # TODO: main issue, strategy explodes
            if i > 30:
                LOGGER.warn('PTA partially plotted due to excessive size.')
                break

            guard = PTA.fix_label_for_html(e.guard, GREEN)
            sync = PTA.fix_label_for_html(e.sync, RED)
            update = PTA.fix_label_for_html(e.update, BLUE)
            label = "<" + guard + '<BR/>' + sync + '<BR/>' + update
            attrib = {}
            if e.weight is not None:
                label += "<BR/>" + str(e.weight)
                attrib['style'] = 'dashed'
            label += ">"
            gra.edge(e.start.label, e.end.label, label=label, _attributes=attrib)

        for bp in self.branchpoints:
            gra.node(bp.id, _attributes={'shape': 'point'})

        return gra

    def plot(self):
        OUT_PATH = config['PTA CONFIGURATION']['SAVE_PATH']
        self.to_digraph().render(directory=OUT_PATH, view=True)

    @staticmethod
    def get_interval(tup):
        # FIXME
        T = 10
        if tup[0] in ['h_dd', 'r_dd']:
            return int(tup[1]) - T / 2, int(tup[1]) + T / 2
        else:
            return int(tup[1]) - (100 * (1 - math.exp(-0.005 * T / 2))), int(tup[1]) + (
                    100 * (1 - math.exp(-0.005 * T / 2)))

    def equalities2intervals(self):
        LOGGER.info('Converting equality constraints to intervals...')
        for e in tqdm(self.edges):
            equalities = [c.replace('\n', '') for c in e.guard.split('&&') if c.__contains__('==')]
            inequalities = [c for c in e.guard.split('&&') if not c.__contains__('==')]
            elems = [(eq.split('==')[0], eq.split('==')[1]) for eq in equalities]
            new_guard = ''
            for i, tup in enumerate(elems):
                # FIXME
                if tup[0] in ['h_dd', 'h_df', 'r_dd']:
                    interval = PTA.get_interval(tup)
                    new_guard += '({}<={}&&{}<={})\n'.format(interval[0], tup[0], tup[0], interval[1])
                else:
                    new_guard += '({}=={})\n'.format(tup[0], tup[1])
                if i < len(elems) - 1:
                    new_guard += '&&'
            if len(inequalities) > 0:
                new_guard += '&&' + '&&'.join(inequalities) if new_guard != '' else '&&'.join(inequalities)
            e.guard = new_guard

    def combine_edges(self):
        LOGGER.info('Combining edges...')
        # TODO: needs refinement
        already_processed = []
        old_edges = self.edges.copy()
        new_edges = []
        for i, edge in tqdm(enumerate(self.edges)):
            if i in already_processed:
                continue
            eq_edges = []
            for j, edge_2 in enumerate(self.edges):
                if i == j or j in already_processed:
                    continue
                same_start = edge.start.label == edge_2.start.label
                same_end = edge.end.label == edge_2.end.label
                same_sync = edge.sync == edge_2.sync
                same_update = edge.update == edge_2.update
                if same_start and same_end and same_sync and same_update:
                    already_processed.append(j)
                    eq_edges.append(edge_2)
            if len(eq_edges) > 0:
                guards = [e.guard for e in eq_edges + [edge]]
                new_guard = guards2singleconstr(guards)
                LOGGER.debug(new_guard)
                new_edges.append(Edge(new_guard, edge.sync, edge.update, edge.start,
                                      edge.end, edge.weight, edge.controllable))
        new_edges += [e for i, e in enumerate(old_edges) if i not in already_processed]
        self.edges = new_edges
