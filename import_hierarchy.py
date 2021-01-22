import csv
import logging
from cassandra.cqlengine import columns
from cassandra.cqlengine import connection
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.query import BatchQuery

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
    return  newrow


# Definit le modèle de la table que l'on va importer dans Cassandra
class HierarchyModel(Model):
    parentid = columns.Integer(primary_key=True)
    childid = columns.Integer(primary_key=True, clustering_order="DESC")
    type = columns.Text()


# Se connecte au keyspace geonames
connection.setup(['127.0.0.1'], "geonames", protocol_version=3)
sync_table(HierarchyModel)


# Importe les données :
# La table sera donc présentée sous la forme : [parentid, childid, type]
with open("geonames/hierarchy.txt", encoding='utf8', newline='') as csvfile:

    # Création du DictReader
    reader = csv.DictReader(csvfile, fieldnames=['parentid', 'childid', 'type'], delimiter='\t')

    # Ingestion par lots
    count = 0
    batch = BatchQuery()
    for row in reader:
        new_row = clean_row(row)
        HierarchyModel.batch(batch).create(**new_row)
        count += 1
        if not count % 1000:
            batch.execute()
            batch = BatchQuery()
            logger.info('Importés: {}'.format(count))

    batch.execute()