import psycopg2
from Vertex import Vertex
from Graph import Graph
from GeoCode import GeoCode
from distCal import lonlat2ID, cor2ID, distanceCal, calPathDis, R

def createMiniWorld(miniGraph, startPt, endPt): 
    #define the boundary of the miniworld
    padding = 0.005
    minLng = min(startPt[0], endPt[0])-padding
    maxLng = max(startPt[0], endPt[0])+padding
    minLat = min(startPt[1], endPt[1])-padding
    maxLat = max(startPt[1], endPt[1])+padding
    try:
        conn = psycopg2.connect("dbname='CamBosRoad' user = 'postgres' host = 'localhost' password='********'")
        cur = conn.cursor()
    except:
        print 'connection problem'     
    cur.execute("SELECT * FROM Edges WHERE fnodelng>{} and fnodelat>{} \
                 and fnodelng<{} and fnodelat<{} \
                ".format(minLng, minLat, maxLng, maxLat))
    miniDB = cur.fetchall()
    #for data in miniDB:
    #    print data
    print ('{} edges found within miniGraph').format(len(miniDB))
    for edge in miniDB:
        fnode = (edge[0], edge[1])
        tnode = (edge[2], edge[3]) 
        miniGraph.addEdge_directional(fnode, tnode, edge[4], edge[5])
    return [[minLat, minLng],[maxLat, maxLng]]
    
    
def PathTestMashUp(startPt, endPt, runDis, ):

    startCor = GeoCode(startPt);
    endCor = GeoCode(endPt)
    
    miniGraph = Graph()
    bounds = createMiniWorld(miniGraph, startCor, endCor)
    
    startNode = [0, 0]
    dist = miniGraph.findNearestNode(startCor, startNode)
    print 'the closest node found to startPt is '+ str(startNode) +', with dist '+str(dist)
    endNode = [0, 0]
    dist = miniGraph.findNearestNode(endCor, endNode)
    print 'the closest node found to endPt is '+str(endNode) +', with dist '+str(dist)
    
    startNode = cor2ID(startNode)
    endNode = cor2ID(endNode)
    K=5
    pathDict = miniGraph.findPath(startNode, endNode, runDis, K)
    for k in range(0, K):
        print 'The actual path dis is '+ str(pathDict[k]['cost'])
        #print pathDict[k]['path']
    return {'miniGraph': miniGraph, 
            'startPt':startCor, 
            'endPt':endCor, 
            'startNode':startNode,
            'endNode':endNode,
            'pathDict':pathDict}
