import configparser
import sys
from typing import List

from graphviz import Digraph

config = configparser.ConfigParser()
config.sections()
config.read(sys.argv[1])
config.sections()


class ExtLocation:
    def __init__(self, tplt: str, label: str):
        self.tplt = tplt
        self.label = label

    @staticmethod
    def parse(line: str):
        fields = line.split('.')
        return ExtLocation(fields[0], fields[1])

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
        return self.identifier + '=' + str(self.value)

    def __eq__(self, other):
        return self.identifier == other.identifier and self.value == other.value

    def __hash__(self):
        return hash(str(self))


class State:
    def __init__(self, locs: List[ExtLocation], vars: List[StateVariable]):
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
    def __init__(self, state: List[ExtLocation], initial=False):
        self.state = state
        self.initial = initial
        self.label = ''
        for i, l in enumerate(state):
            self.label += str(l)
            if i < len(state) - 1:
                self.label += ',\n'

    def __eq__(self, other):
        return all([x in other.state for x in self.state])

    def __hash__(self):
        return hash(str(self))


class Edge:
    def __init__(self, guard: str, sync: str, update: str, start: Location, end: Location):
        guard = guard.replace('(', '').replace(')', '').replace(' && ', ' &&\n')
        self.guard = guard
        self.sync = sync
        self.update = update
        self.start = start
        self.end = end


class PTA:
    def __init__(self, locs: List[Location], edges: List[Edge]):
        self.locations = locs
        self.edges = edges

    def to_digraph(self, name: str):
        gra = Digraph(name)

        for l in self.locations:
            if l.initial:
                gra.node(l.label, _attributes={'peripheries': '2'})
            else:
                gra.node(l.label)

        for e in self.edges:
            gra.edge(e.start.label, e.end.label, label=e.guard + '\n' + e.sync)

        return gra

    def plot(self, name: str):
        OUT_PATH = config['PTA CONFIGURATION']['SAVE_PATH']
        self.to_digraph(name).render(directory=OUT_PATH, view=True)
