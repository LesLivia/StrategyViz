import configparser
import sys
from typing import List

from graphviz import Digraph

config = configparser.ConfigParser()
config.sections()
config.read("./resources/config/config.ini")
config.sections()


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

    def __init__(self, net_locs: List[NetLocation], initial=False, invariant: str = None):
        self.net_locs = net_locs
        self.initial = initial
        self.label = ''
        for i, l in enumerate(net_locs):
            self.label += str(l)
            if i < len(net_locs) - 1:
                self.label += ',\n'
        self.invariant = invariant if invariant is not None else ''

    def __str__(self):
        return self.label

    def __eq__(self, other):
        return self.label == other.label

    def __hash__(self):
        return hash(str(self))


class Edge:
    def __init__(self, guard: str, sync: str, update: str, start, end, weight: str = None):
        guard = guard.replace('(', '').replace(')', '').replace(' && ', ' &&\n')
        self.guard = guard
        self.sync = sync
        self.update = update
        self.start = start
        self.end = end
        self.weight = weight

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
    def __init__(self, name: str, locs: List[Location], edges: List[Edge], bps: List[BranchPoint] = None):
        self.name = name
        self.locations = locs
        self.edges = edges
        self.branchpoints = bps if bps is not None else []

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
            label = "<" + l.label + "<BR/>" + invariant + ">"

            if l.initial:
                gra.node(l.label, label=label, _attributes={'peripheries': '2'})
            else:
                gra.node(l.label, label=label)

        for i, e in enumerate(self.edges):
            # TODO: main issue, strategy explodes
            if i > 30:
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
