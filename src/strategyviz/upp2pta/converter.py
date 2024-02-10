import configparser
import sys
import xml.etree.ElementTree as et
from typing import List
from xml.etree.ElementTree import Element

from src.strategyviz.strategy2pta.pta import Location, NetLocation, PTA, Edge, BranchPoint
from src.strategyviz.viz_logging.logger import Logger

LOGGER = Logger('UPPAAL2PTA CONVERTER')

config = configparser.ConfigParser()
config.sections()
config.read("./resources/config/config.ini")
config.sections()


def parse_locations(tplt: Element, pta_name: str, initial_id: str):
    locations = {}
    for node in tplt.iter('location'):
        loc_id = node.attrib['id']
        try:
            loc_label = node.find('name').text
        except AttributeError:
            loc_label = loc_id

        if node.find('urgent') is not None:
            urgency = 1
        elif node.find('committed') is not None:
            urgency = 2
        else:
            urgency = 0

        try:
            loc_labels = node.iter('label')
            loc_invariant = ''
            for label in loc_labels:
                if label.attrib['kind'] == 'invariant':
                    loc_invariant = label.text
        except AttributeError:
            loc_invariant = None

        net_locs: List[NetLocation] = [NetLocation(pta_name, loc_label)]
        locations[loc_id] = Location(net_locs, initial_id == loc_id, invariant=loc_invariant, urgent=urgency)

    return locations


def parse_branchpoints(tplt: Element):
    bps = []

    for bp in tplt.iter('branchpoint'):
        bps.append(BranchPoint(bp.attrib['id']))

    return bps


def parse_edges(tplt: Element, locations, bps):
    edges = []

    for trans in tplt.iter('transition'):
        try:
            controllable = False if trans.attrib['controllable'] == 'false' else True
        except KeyError:
            controllable = True

        source_id = trans.find('source').attrib['ref']
        target_id = trans.find('target').attrib['ref']
        guard = ''
        sync = ''
        update = ''
        weight = None
        for label in trans.iter('label'):
            if label.attrib['kind'] == 'guard':
                guard = label.text
            elif label.attrib['kind'] == 'assignment':
                update = label.text
            elif label.attrib['kind'] == 'synchronisation':
                sync = label.text
            elif label.attrib['kind'] == 'probability':
                weight = label.text

        try:
            source = locations[source_id]
        except KeyError:
            source = list(filter(lambda b: b.id == source_id, bps))[0]
        try:
            target = locations[target_id]
        except KeyError:
            target = list(filter(lambda b: b.id == target_id, bps))[0]

        edges.append(Edge(guard, sync, update, source, target, weight, controllable))

    return edges


def parse_uppaal_model(view=False):
    if len(sys.argv) < 3:
        LOGGER.error("Wrong input parameters.")
        raise RuntimeError

    MODEL_NAME = sys.argv[1]
    MODEL_PATH = config['MODEL CONFIGURATION']['MODEL_PATH'] + MODEL_NAME + config['MODEL CONFIGURATION']['MODEL_EXT']

    PTAS = []

    tree = et.parse(MODEL_PATH)
    root = tree.getroot()
    instances = [i.text for i in root.iter('system')][0].split('\n')
    instances = [i.replace(' ', '') for i in instances if i.__contains__('=')]
    for tplt in root.iter('template'):
        tplt_name = tplt.find('name').text
        pta_names = [i.split('=')[0] for i in instances if i.__contains__(tplt_name)]
        initial_id = tplt.find('init').attrib['ref']

        for instance in pta_names:
            try:
                local_declaration = tplt.find('declaration').text
            except AttributeError:
                local_declaration = ''

            locations = parse_locations(tplt, instance, initial_id)
            bps = parse_branchpoints(tplt)
            edges = parse_edges(tplt, locations, bps)

            PTAS.append(PTA(instance, list(locations.values()), edges, bps, local_declaration))

    if view:
        [pta.plot() for pta in PTAS]

    return PTAS
