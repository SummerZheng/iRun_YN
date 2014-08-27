###
#This file load the adjacency list representation of the 
#map from pickle file and write it into PostgreSQL database
###
import pickle
import psycopg2
roadAdjList = pickle.load( open( "CamBosRoadMapFT.p", "rb" ) )
from distCal import distanceCal4par
###
#Save node info into postgreSQL database
#u->v1, v2, v3
#keep two copies, 
###

try:
    conn = psycopg2.connect("dbname='CamBosRoad' user = 'postgres' host = 'localhost' password='********'")
except:
    print 'connection problem'

cur = conn.cursor()
duplicateCt = 0
ct = 0
try:
    print 'Creating SQL Table Edges from Graph Adjcency List...'
    cur.execute('DROP TABLE IF EXISTS Edges;');
    cur.execute('CREATE TABLE Edges (fNodeLng FLOAT NOT NULL, fNodeLat FLOAT NOT NULL, tNodeLng FLOAT NOT NULL, tNodeLat FLOAT NOT NULL, dist FLOAT NOT NULL, score FLOAT NOT NULL, PRIMARY KEY(fNodeLng, fNodeLat, tNodeLng, tNodeLat));')
    for node in roadAdjList.vertList:
        for cnode in roadAdjList.vertList[node].getConnections():
            ct+=1
            try:
                dist = distanceCal4par(node[0], node[1], cnode[0], cnode[1])
                cur.execute("INSERT INTO Edges (fNodeLng, fNodeLat, tNodeLng, tNodeLat, dist, score) VALUES (%s, %s, %s, %s, %s, %s)", (node[0], node[1], cnode[0], cnode[1], dist, roadAdjList.vertList[node].connectedTo[cnode][1]))
                if (ct%1000)==0:
                    print '{}\'s edge inserted: ({}+{}) to ({}+{}) with dist {} and score {}'.format(ct, node[0],node[1], cnode[0],cnode[1], dist, roadAdjList.vertList[node].connectedTo[cnode][1])  
            except:
                duplicateCt += 1
                print 'duplicate edge found for ({}+{}) to ({}+{}) with dist {} and score {}'.format(node[0],node[1], cnode[0],cnode[1], dist, roadAdjList.vertList[node].connectedTo[cnode][1])             
    print 'total duplicate found '+str(duplicateCt)+' in total of '+str(ct)+' edges'
    ###
    #Create a index for fNode coordinates for fast real-time data retrieval
    #Btree, log(n) range search
    ###
    cur.execute('CREATE INDEX fNodeCor ON Edges (fNodeLng, fNodeLat);');
    try:
        cur.execute('DROP INDEX fNodeCor');
    except:
        print 'INDEX cannot be created for (lng, lat) pair'
    conn.commit();

    cur.close()
    conn.close();
except:
    print 'cannot create table Edges'


