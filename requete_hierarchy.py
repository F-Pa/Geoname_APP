from cassandra.cluster import Cluster
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

# Connexion à cassandra et Elasticsearch
cluster = Cluster().connect('geonames')
client = Elasticsearch([{'host': 'localhost', 'port': 9200}])


# Renvoie les geonameid ayant le même admin_code et la même feature_class que celui en entrée
def admin_class(admin_code, feature_class, num):
    # Requête dans l'index hierarchy d'Elasticsearch pour récupérer tout les résultats ayant le même admin_code et la
    # même feature_class
    search = Search(index="hierarchy").using(client)
    if num == 1:
        search = search.query('match', admin1_code=admin_code)
    elif num == 2:
        search = search.query('match', admin2_code=admin_code)
    elif num == 3:
        search = search.query('match', admin3_code=admin_code)
    elif num == 4:
        search = search.query('match', admin4_code=admin_code)

    search = search.query('match', feature_class=feature_class)

    # On insère dans geoname_tab tout les geonameid retourné par notre requête Elasticsearch
    geoname_tab = []
    for hit in search[0:search.count()]:
        geoname_tab.append(hit.geonameid)

    return geoname_tab


# Si le geonameid n'a pas de parent direct on cherche un voisin dont la hiérarchie existe
def admin_code(geonameid):
    request1 = 'SELECT admin1_code, admin2_code, admin3_code, admin4_code FROM geoname WHERE "geonameid"=%s'
    session1 = cluster.execute(request1, [geonameid])
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

    neighbourhood = admin_class(result[len(result) - 1], 'A', len(result))
    for neighbour in neighbourhood:
        try:
            request2 = 'SELECT parentid FROM hierarchy_model WHERE "childid"=%s limit 1 ALLOW FILTERING'
            session2 = cluster.execute(request2, [int(neighbour)])
        except Exception as e:
            print(e)
            return 6295630
        if session2:
            for it in session2:
                let_id = it.parentid
            break
    return let_id

#=======================================================================================================================
# Renvoie la hierarchie complète, dans un premier temps récupère les geonameid de la hierarchie puis les asciiname
# de ces derniers
#=======================================================================================================================
def hierarchy(child_id):
    hier_geonameid = []
    hier_geonameid.append(child_id)
    # On cherche à atteindre l'id de la Terre
    while child_id != 6295630:
        request1 = 'SELECT "parentid" FROM hierarchy_model WHERE "childid"=%s limit 1 ALLOW FILTERING'
        session1 = cluster.execute(request1, [child_id])
        if not session1:
            child_id = admin_code(child_id)
        else:
            for row in session1:
                child_id = row.parentid
        hier_geonameid.append(child_id)

    # On récupère les asciiname de la hiérarchie retournée ci-dessus
    hier_asciiname = []
    for ids in hier_geonameid:
        request2 = 'SELECT asciiname FROM geoname WHERE geonameid=%s '
        session2 = cluster.execute(request2, [ids])
        for row in session2:
            hier_asciiname.append(row.asciiname)

    return hier_asciiname


if __name__ == "__main__":
    print(hierarchy(2984630))