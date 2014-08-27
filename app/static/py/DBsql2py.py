###
# This module import edge information from sql into python
# Only choose nodes within bbox
# And create a adjacency list representation of miniworld
###
import psycopg2
from Graph import Graph

def createMiniWorld(miniGraph, startPt, endPt): 
    #define the boundary of the miniworld
    padding = 0.01
    minLat = min(startPt[0], endPt[0])-padding
    maxLat = max(startPt[0], endPt[0])+padding
    minLng = min(startPt[1], endPt[1])-padding
    maxLng = max(startPt[1], endPt[1])+padding
    try:
        conn = psycopg2.connect("dbname='CamBosRoad' user = 'postgres' host = 'localhost' password='*******'")
        cur = conn.cursor()
    except:
        print 'connection problem'     
    cur.execute("SELECT * FROM Edges WHERE fnodelat \
        > {} and fnodelng>{} and fnodelat<{} and fnodelng<{} \
        ".format(minLat, minLng, maxLat, maxLng))
    miniDB = cur.fetchall()
    #for data in miniDB:
    #    print data
    #print len(miniDB)
    for edge in miniDB:
        fnode = (edge[0], edge[1])
        tnode = (edge[2], edge[3]) 
        miniGraph.addEdge_directional(fnode, tnode, edge[4], edge[5])


myGraph = Graph()
createMiniWorld(myGraph, (-71.0963, 42.3542), (-70.0709, 42.3661))
print myGraph.numEdges
print myGraph.numVertices


"""
def inBounds(node, minX, maxX, minY, maxY):
    flag1 = (node.getLat()<maxY and node.getLat()>minY)
    flag2 = (node.getLon()<maxX and node.getLon()>minX)
    if  flag1 and flag2:
        return True
    return False
""" 

