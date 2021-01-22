import csv
import logging
from cassandra.cqlengine.query import BatchQuery
from models.geonames import *

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)


def clean_row(row):
    newrow = dict()
    for key in row.keys():
        if row[key]:
            newrow[key] = row[key]
    return newrow


def import_data():

    connection.setup(['127.0.0.1'], "geonames", protocol_version=3)
    fieldnames = [col for col in Geoname().__dict__['_values']]

    with open("geonames/allCountries.txt", encoding='utf8', newline='') as csvfile:

        # Création du DictReader
        csv.register_dialect('geoname', delimiter='\t', quoting=csv.QUOTE_NONE)
        reader = csv.DictReader(csvfile, dialect='geoname', fieldnames=fieldnames)

        # Ingestion par lots
        count = 0
        batch = BatchQuery()
        for row in reader:
            new_row = clean_row(row)
            Geoname.batch(batch).create(**new_row)
            count += 1
            if not count % 1000:
                batch.execute()
                batch = BatchQuery()
                logger.info('Importés: {}'.format(count))

        batch.execute()


if __name__ == "__main__":
    import_data()
