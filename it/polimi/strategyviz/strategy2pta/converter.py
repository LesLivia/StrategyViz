import configparser
import sys
from typing import List

from it.polimi.strategyviz.strategy2pta.pta import PTA, Location
from it.polimi.strategyviz.strategy2pta.stratego_parser import parse_optimized_strategy
from it.polimi.strategyviz.strategy2pta.tigaparser import parse_tiga_strategy, TigaStrategy
from it.polimi.strategyviz.upp2pta.converter import parse_uppaal_model
from it.polimi.strategyviz.viz_logging.logger import Logger
from it.polimi.strategyviz.z3gen.z3constrgenerator import guards2singleconstr

config = configparser.ConfigParser()
config.sections()
config.read("./resources/config/config.ini")
config.sections()

LOGGER = Logger('STRATEGY2PTA CONVERTER')


def connected_to_root(pta: PTA, curr_loc: Location, already_checked: List[Location]):
    already_checked.append(curr_loc)
    if curr_loc.kind == 'LOC' and curr_loc.initial:
        return True
    else:
        incoming_edges = list(filter(lambda e: e.end.label == curr_loc.label, pta.edges))
        predecessors = [e.start for e in incoming_edges]
        for p in predecessors:
            if p.kind == 'BP':
                edges_to_bp = list(filter(lambda e: e.end.label == p.label, pta.edges))
                predecessors += [e.start for e in edges_to_bp]
        predecessors = list(filter(lambda p: p.kind == 'LOC', predecessors))
        predecessors = list(filter(lambda p: p not in already_checked, predecessors))
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
    unconnected_locs = set([])
    for l in pta.locations + pta.branchpoints:
        if not connected_to_root(pta, l, []):
            unconnected_locs.add(l)

    unconnected_edges = list(filter(lambda e: (e.start in unconnected_locs) or
                                              (e.end in unconnected_locs), pta.edges))

    new_locs = list(set(pta.locations) - set(unconnected_locs))
    new_edges = list(set(pta.edges) - set(unconnected_edges))
    new_pta = PTA('trimmed_' + pta.name, new_locs, new_edges, pta.branchpoints)

    # cleans unconnected locations which are present only as edges start/end
    for e in new_pta.edges:
        if not connected_to_root(new_pta, e.start, []):
            unconnected_locs.add(e.start)
            unconnected_edges.append(e)
        if not connected_to_root(new_pta, e.end, []):
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

    STRATEGIES_PATH = config['STRATEGY CONFIGURATION']['STRATEGY_PATH']
    TIGA_PATH = STRATEGIES_PATH + sys.argv[2] + config['STRATEGY CONFIGURATION']['TIGA_EXT']
    # optimized strategy is an optional parameter
    if len(sys.argv) >= 4:
        STRATEGO_PATH = STRATEGIES_PATH + sys.argv[3] + config['STRATEGY CONFIGURATION']['STRATEGO_EXT']
    else:
        STRATEGO_PATH = None

    LOGGER.info("Parsing TIGA strategy...")
    with open(TIGA_PATH) as tiga_strategy_file:
        lines = tiga_strategy_file.readlines()
        tiga_strategy: TigaStrategy = parse_tiga_strategy(sys.argv[2], lines)
        network = parse_uppaal_model(view=False)
        tiga_strategy_pta = tiga_strategy.to_pta(network, view=True)
        try:
            tiga_strategy_pta = clean_pta(tiga_strategy_pta)
        except IndexError:
            LOGGER.error("An error occurred while trimming the PTA.")
        # tiga_strategy_pta.plot()

    LOGGER.msg("TIGA strategy successfully parsed.")

    # if the path to an optimized strategy has been given as input,
    # use it to refine the TIGA strategy
    if STRATEGO_PATH is not None:
        LOGGER.info("Parsing optimized strategy...")

        with open(STRATEGO_PATH) as opt_strategy_file:
            data: str = opt_strategy_file.read()
            optimized_strategy = parse_optimized_strategy(sys.argv[3], data)

        final_pta = optimized_strategy.refine_pta(tiga_strategy_pta)
    else:
        final_pta = tiga_strategy_pta

    try:
        final_pta = clean_pta(final_pta)
    except IndexError:
        LOGGER.error("An error occurred while trimming the PTA.")
    final_pta.equalities2intervals()
    # final_pta.combine_edges()
    final_pta.plot()

    LOGGER.msg("Stratego strategy successfully parsed.")

    return final_pta
