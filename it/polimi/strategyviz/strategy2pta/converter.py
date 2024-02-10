import configparser
import sys
import time
from typing import Set

from it.polimi.strategyviz.strategy2pta.pta import PTA, Location
from it.polimi.strategyviz.strategy2pta.stratego_parser import parse_optimized_strategy
from it.polimi.strategyviz.strategy2pta.tigaparser import parse_tiga_strategy, TigaStrategy
from it.polimi.strategyviz.upp2pta.converter import parse_uppaal_model
from it.polimi.strategyviz.viz_logging.logger import Logger

config = configparser.ConfigParser()
config.sections()
config.read("./resources/config/config.ini")
config.sections()

LOGGER = Logger('STRATEGY2PTA CONVERTER')


def connected_to_root(pta: PTA, curr_loc: Location, already_checked: Set[Location]):
    already_checked.add(curr_loc)
    if curr_loc.kind == 'LOC' and curr_loc.initial:
        return True
    else:
        incoming_edges = list(filter(lambda e: e.end.label == curr_loc.label, pta.edges))
        predecessors = set([e.start for e in incoming_edges])
        to_add = set()
        for p in predecessors:
            if p.kind == 'BP':
                edges_to_bp = list(filter(lambda e: e.end.label == p.label, pta.edges))
                to_add.update(set([e.start for e in edges_to_bp]))
        predecessors.update(to_add)
        predecessors = set(filter(lambda p: p.kind == 'LOC', predecessors))
        predecessors = set(filter(lambda p: p not in already_checked and p != curr_loc, predecessors))
        if len(predecessors) == 0:
            return False
        else:
            return any([connected_to_root(pta, p, already_checked) for p in predecessors])


def clean_pta(pta: PTA):
    # cleans initial locs not set as initial
    initial_loc = list(filter(lambda l: l.initial, pta.locations))[0]
    for e in pta.edges:
        if e.start.label == initial_loc.label:
            e.start.initial = True
        if e.end.label == initial_loc.label:
            e.end.initial = True

    # cleans unconnected locations
    unconnected_locs = set()
    checked_locs = set()
    for l in pta.locations + pta.branchpoints:
        checked_locs.add(l)
        if not connected_to_root(pta, l, set()):
            unconnected_locs.add(l)

    unconnected_edges = list(filter(lambda e: (e.start in unconnected_locs) or
                                              (e.end in unconnected_locs), pta.edges))

    new_locs = list(set(pta.locations) - set(unconnected_locs))
    new_edges = list(set(pta.edges) - set(unconnected_edges))
    new_pta = PTA('trimmed_' + pta.name, new_locs, new_edges, pta.branchpoints)

    edges_to_recheck = list(filter(lambda e: e.start not in checked_locs or e.end not in checked_locs, new_pta.edges))
    # cleans unconnected locations which are present only as edges start/end
    for e in edges_to_recheck:
        if not connected_to_root(new_pta, e.start, set()):
            unconnected_locs.add(e.start)
            unconnected_edges.append(e)
        if not connected_to_root(new_pta, e.end, set()):
            unconnected_locs.add(e.end)
            unconnected_edges.append(e)

    new_locs = list(set(new_pta.locations) - unconnected_locs)
    new_edges = list(set(new_pta.edges) - set(unconnected_edges))

    # cleans breakpoints
    new_bps = list(set(pta.branchpoints) - set(unconnected_locs))

    new_pta = PTA('trimmed_' + pta.name, new_locs, new_edges, new_bps, pta.declarations)

    return new_pta


def convert():
    if len(sys.argv) < 3:
        LOGGER.error('Not enough input parameters.')
        raise RuntimeError

    start_ts = time.time()
    STRATEGIES_PATH = config['STRATEGY CONFIGURATION']['STRATEGY_PATH']
    TIGA_PATH = STRATEGIES_PATH + sys.argv[2] + config['STRATEGY CONFIGURATION']['TIGA_EXT']
    # optimized strategy is an optional parameter
    if len(sys.argv) >= 4:
        STRATEGO_PATH = STRATEGIES_PATH + sys.argv[3] + config['STRATEGY CONFIGURATION']['STRATEGO_EXT']
    else:
        STRATEGO_PATH = None

    with open(TIGA_PATH) as tiga_strategy_file:
        LOGGER.info("Parsing TIGA strategy...")
        lines = tiga_strategy_file.readlines()
        tiga_strategy: TigaStrategy = parse_tiga_strategy(sys.argv[2], lines)
        network = parse_uppaal_model(view=False)
        tiga_strategy_pta = tiga_strategy.to_pta(network, view=True)
        LOGGER.msg("TIGA strategy successfully parsed.")
        try:
            tiga_strategy_pta = clean_pta(tiga_strategy_pta)
        except IndexError:
            LOGGER.error("An error occurred while trimming the PTA.")
        tiga_strategy_pta.plot()
    end_ts = time.time()
    LOGGER.msg("TA extraction from TIGA strategy took {:.2f}s.".format(end_ts - start_ts))

    # if the path to an optimized strategy has been specified,
    # use it to refine the TIGA strategy
    if STRATEGO_PATH is not None:
        start_ts = time.time()
        LOGGER.info("Parsing optimized strategy...")

        with open(STRATEGO_PATH) as opt_strategy_file:
            data: str = opt_strategy_file.read()
            optimized_strategy = parse_optimized_strategy(sys.argv[3], data)

        final_pta = optimized_strategy.refine_pta(tiga_strategy_pta)
        LOGGER.msg("Optimized strategy successfully parsed.")
    else:
        final_pta = tiga_strategy_pta

    try:
        final_pta = clean_pta(final_pta)
    except IndexError:
        LOGGER.error("An error occurred while trimming the PTA.")

    end_ts = time.time()
    LOGGER.msg("PTA extraction from optimized strategy took {:.2f}s.".format(end_ts - start_ts))

    # final_pta.equalities2intervals()
    # final_pta.combine_edges()
    final_pta.plot()

    return final_pta
