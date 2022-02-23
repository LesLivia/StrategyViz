import configparser
import sys
import xml.etree.ElementTree as et
import xml.etree.cElementTree as cet

from it.polimi.strategyviz.strategy2pta.pta import PTA
from it.polimi.strategyviz.viz_logging.logger import Logger

config = configparser.ConfigParser()
config.sections()
config.read(sys.argv[1])
config.sections()

LOGGER = Logger('UPPAAL MODEL GENERATOR')


def get_new_coord(x: int, y: int):
    incr = 100
    max_row = 5

    if x >= incr * max_row:
        return 0, y + incr
    else:
        return x + incr, y


def to_uppaal_model(pta: PTA):
    if len(sys.argv) < 5:
        LOGGER.error("Wrong input parameters.")
        raise RuntimeError

    MODEL_NAME = sys.argv[4]
    MODEL_PATH = config['MODEL CONFIGURATION']['MODEL_PATH'] + MODEL_NAME + config['MODEL CONFIGURATION']['MODEL_EXT']

    tree = et.parse(MODEL_PATH)
    root = tree.getroot()

    new_root: cet.Element = cet.Element('nta')

    # COPY GLOBAL DECLARATIONS
    only_global = True
    for gd in root.iter('declaration'):
        if not only_global:
            break
        global_declarations = cet.SubElement(new_root, 'declaration')
        global_declarations.text = gd.text
        only_global = False

    # COPY EXISTING TEMPLATES
    pta_local_content = ''
    for tplt in root.iter('template'):
        tplt_copy = cet.SubElement(new_root, 'template')
        # TODO: fix me, it's hard-coded
        if tplt.find('name').text == 'Traveler':
            pta_local_content = tplt.find('declaration').text

        for c in tplt.getchildren():
            new_c = cet.SubElement(tplt_copy, c.tag, c.attrib)
            new_c.text = c.text
            for c2 in c.getchildren():
                new_c2 = cet.SubElement(new_c, c2.tag, c2.attrib)
                new_c2.text = c2.text

    # ADD TEMPLATE FOR NEW STRATEGY PTA
    new_template = cet.SubElement(new_root, 'template')
    new_tplt_name = cet.SubElement(new_template, 'name', {'x': '9', 'y': '9'})
    new_tplt_name.text = pta.name.split('_')[-1]
    new_declarations = cet.SubElement(new_template, 'declaration')
    new_declarations.text = pta_local_content

    # ADD LOCATIONS
    init_id = ''

    x = 0
    y = 0
    for i, l in enumerate(pta.locations):
        x, y = get_new_coord(x, y)
        new_attrib = {'id': 'id' + str(i), 'x': str(x), 'y': str(y)}
        new_loc = cet.SubElement(new_template, 'location', new_attrib)
        new_name = cet.SubElement(new_loc, 'name', {'x': str(x), 'y': str(y - 10)})
        new_name.text = l.label.split('.')[-1]
        if l.initial:
            init_id = 'id' + str(i)

    for i, bp in enumerate(pta.branchpoints):
        x, y = get_new_coord(x, y)
        new_attrib = {'id': 'id' + str(i), 'x': str(x), 'y': str(y)}
        new_bp = cet.SubElement(new_template, 'branchpoint', new_attrib)

    new_init = cet.SubElement(new_template, 'init', {'ref': init_id})

    # COPY SYSTEM DECLARATION
    for s in root.iter('system'):
        system_decl = cet.SubElement(new_root, 'system')
        system_decl.text = s.text

    new_tree = cet.ElementTree(new_root)
    new_tree.write('./resources/test.xml')
