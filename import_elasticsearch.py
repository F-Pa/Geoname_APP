import csv
from elasticsearch import Elasticsearch
from elasticsearch import helpers

client = Elasticsearch([{'host': 'localhost', 'port': 9200}])

# Vérifie si la connection avec Elasticsearch est bien établie
def connect_elasticsearch():
    if client.ping():
        print('Connecté')
    else:
        print('Problème de connexion')
    return client


# Crée un index dans Elasticsearch avec le nom spécifié
def create_index(index_name):
    try:
        if not client.indices.exists(index_name):
            print("creating 'example_index' index...")
            client.indices.create(index=index_name)
    except Exception as ex:
        print(str(ex))

#=======================================================================================================================
# Permet d'insérer les données dans Elasticsearch, cette fonction n'est pas générique :
# Elle permet soit de créer l'index hierarchy et d'y insérer les données nécéssaires pour les requêtes sur la hierarchie
#             soit de créer l'index geoname et d'y insérer les données nécéssaires pour la longitude et la latitude
# Il suffit de changer le doc et le helpers
#=======================================================================================================================
def insert_index():
    with open('geonames/allCountries.txt', newline='', encoding='utf8') as csvfile:
        reader = csv.DictReader(csvfile,
                                fieldnames=["geonameid", "name", "asciiname",
                                            "alternatenames", "latitude",
                                            "longitude", "feature_class",
                                            "feature_code", "country_code",
                                            "cc2", "admin1_code", "admin2_code",
                                            "admin3_code", "admin4_code", "population",
                                            "elevation", "dem", "timezone",
                                            "modification_date"],
                                delimiter='\t')
        print('ok')
        count = 0
        # Bulk data va permettre d'importer les données plus rapidement dans Elasticsearch en faisant un seul import
        bulk_data = []
        for row in reader:
            # doc = {
            #     'geonameid': row['geonameid'],
            #     'name': row['name'],
            #     'admin1_code': row['admin1_code'],
            #     'admin2_code': row['admin2_code'],
            #     'admin3_code': row['admin3_code'],
            #     'admin4_code': row['admin4_code'],
            #     'feature_class': row['feature_class'],
            # }
            doc = {
                'geonameid': row['geonameid'],
                'admin1_code': row['admin1_code'],
                'latitude': row['latitude'],
                'longitude': row['longitude'],
                'name': row['name'],
                'asciiname': row['asciiname'],
            }
            bulk_data.append(doc)
            if count % 1000 == 0:
                print(count)
            count += 1
        try:
            # helpers.bulk(client, bulk_data, index='hierarchy')
            helpers.bulk(client, bulk_data, index='geoname')
        except Exception as e:
            print(e)


# Permet de supprimer l'index donné dans Elasticsearch
def delete_index(index_name):
    client.indices.delete(index=index_name)


if __name__ == '__main__':
    insert_index()