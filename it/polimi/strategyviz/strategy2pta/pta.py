from typing import List


class Location:
    def __init__(self, label: str):
        self.label = label


class Edge:
    def __init__(self, guard: str, sync: str, update: str, start: Location, end: Location):
        self.guard = guard
        self.sync = sync
        self.update = update
        self.start = start
        self.end = end


class PTA:
    def __init__(self, locs: List[Location], edges: List[Edge]):
        self.locations = locs
        self.edges = edges
