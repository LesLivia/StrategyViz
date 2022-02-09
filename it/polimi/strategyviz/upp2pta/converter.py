import xml.etree.ElementTree as et

import configparser
import sys

from it.polimi.strategyviz.viz_logging.logger import Logger

from it.polimi.strategyviz.strategy2pta.pta import Location, Edge, NetLocation, PTA
from typing import List

LOGGER = Logger('UPPAAL2PTA CONVERTER')

config = configparser.ConfigParser()
config.sections()
config.read(sys.argv[1])
config.sections()


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
        locations: List[Location] = []
        edges: List[Edge] = []

        pta_name = tplt.find('name').text
        initial_id = tplt.find('init').attrib['ref']
        for node in tplt.iter('location'):
            loc_id = node.attrib['id']
            loc_label = node.find('name').text
            net_locs: List[NetLocation] = [NetLocation(pta_name, loc_label)]
            locations.append(Location(net_locs, initial_id == loc_id))

        PTAS.append(PTA(pta_name, locations, edges))

    [p.plot() for p in PTAS]
