from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from cassandra.cluster import Cluster
from geopy import distance

cluster = Cluster().connect('geonames')
client = Elasticsearch([{'host': 'localhost', 'port': 9200}])


def id_lat_long(lat, long):
    res = {
        'query': {
            'bool': {
                'must': [
                    {'match': {'latitude': lat}},
                    {'match': {'longitude': long}}
                ]
            }
        }
    }
    req = client.search(index='geoname', body=res)
    if req['hits']['max_score'] is not None:
        data = [doc for doc in req['hits']['hits']]
        for doc in data:
            let_id = doc['_source']['geonameid']
            return let_id


def admin_loc(lat, long):
    geonameid = id_lat_long(lat, long)
    request1 = 'SELECT admin1_code, admin2_code, admin3_code, admin4_code FROM geoname WHERE "geonameid"=%s'
    session1 = cluster.execute(request1, [int(geonameid)])
    colonne = session1.one()
    result = []
    if colonne.admin4_code is not None:
        result = [colonne.admin1_code, colonne.admin2_code, colonne.admin3_code, colonne.admin4_code]
    else:
        if colonne.admin3_code is not None:
            result = [colonne.admin1_code, colonne.admin2_code, colonne.admin3_code]
        else:
            if colonne.admin2_code is not None:
                result = [colonne.admin1_code, colonne.admin2_code]
            else:
                result = [colonne.admin1_code]

    search = Search(index="geoname").using(client)
    search = search.query('match', admin1_code=result[0])

    geoname_tab = []
    it = 0
    if search.count() > 1000:
        it = 1000
    else:
        it = search.count()
    for hit in search[0:it]:
        coords_1 = (lat, long)
        coords_2 = (hit.latitude, hit.longitude)
        geoname_tab.append({
            'geonameid': hit.geonameid,
            'asciiname': hit.asciiname,
            'latitude': hit.latitude,
            'longitude': hit.longitude,
            'distance': distance.geodesic(coords_1, coords_2).km
        })

    geoname_tab = sorted(geoname_tab, key=lambda k: k['distance'])
    return geoname_tab

#
# for ti in admin_loc(43.82512, 1.72382)[0:10]:
#     print(ti)