import configparser
import sys
import xml.etree.ElementTree as et
from typing import List
from xml.etree.ElementTree import Element

from it.polimi.strategyviz.strategy2pta.pta import Location, NetLocation, PTA, Edge, BranchPoint
from it.polimi.strategyviz.viz_logging.logger import Logger

LOGGER = Logger('UPPAAL2PTA CONVERTER')

config = configparser.ConfigParser()
config.sections()
config.read(sys.argv[1])
config.sections()


def parse_locations(tplt: Element, pta_name: str, initial_id: str):
    locations = {}
    for node in tplt.iter('location'):
        loc_id = node.attrib['id']
        loc_label = node.find('name').text
        net_locs: List[NetLocation] = [NetLocation(pta_name, loc_label)]
        locations[loc_id] = Location(net_locs, initial_id == loc_id)

    return locations


def parse_branchpoints(tplt: Element):
    bps = []

    for bp in tplt.iter('branchpoint'):
        bps.append(BranchPoint(bp.attrib['id']))

    return bps


def parse_edges(tplt: Element, locations, bps):
    edges = []

    for trans in tplt.iter('transition'):
        source_id = trans.find('source').attrib['ref']
        target_id = trans.find('target').attrib['ref']
        guard = ''
        sync = ''
        update = ''
        for label in trans.iter('label'):
            if label.attrib['kind'] == 'guard':
                guard = label.text
            if label.attrib['kind'] == 'assignment':
                update = label.text
            if label.attrib['kind'] == 'synchronisation':
                sync = label.text

        try:
            source = locations[source_id]
        except KeyError:
            source = list(filter(lambda b: b.id == source_id, bps))[0]
        try:
            target = locations[target_id]
        except KeyError:
            target = list(filter(lambda b: b.id == target_id, bps))[0]

        edges.append(Edge(guard, sync, update, source, target))

    return edges


def parse_uppaal_model():
    if len(sys.argv) < 5:
        LOGGER.error("Wrong input parameters.")
        raise RuntimeError

    MODEL_NAME = sys.argv[4]
    MODEL_PATH = config['MODEL CONFIGURATION']['MODEL_PATH'] + MODEL_NAME + config['MODEL CONFIGURATION']['MODEL_EXT']

    PTAS = []

    tree = et.parse(MODEL_PATH)
    root = tree.getroot()
    for tplt in root.iter('template'):
        pta_name = tplt.find('name').text
        initial_id = tplt.find('init').attrib['ref']

        locations = parse_locations(tplt, pta_name, initial_id)
        bps = parse_branchpoints(tplt)
        edges = parse_edges(tplt, locations, bps)

        PTAS.append(PTA(pta_name, list(locations.values()), edges, bps))

    [p.plot() for p in PTAS]
