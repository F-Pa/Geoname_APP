import logging
from models.geonames import *

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

connection.setup(['127.0.0.1'], "geonames", protocol_version=3)

logger.info("Syncing table Geoname")
sync_table(Geoname)
