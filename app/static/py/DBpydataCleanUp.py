###
#preSQL, convert geojson data into adjacency list representation
#and pickle dump
###
import json
import sys
from pprint import pprint
from distCal import lonlat2ID, cor2ID, distanceCal, calPathDis, R, innerProduct, directionalVec
from Vertex import Vertex
from Graph import Graph
from Queue import Queue
import pickle
import psycopg2
from sets import Set

json_data = open('CamBosRoadFT.geojson')
#json_data = open('MITmapV1.geojson')
road_data =json.load(json_data)
road_list_osm = road_data['features']
json_data.close()
print 'data imported'

lineNum = 0
roadAdjList = Graph()

def addPath2AdjList(linCor, roadAdjList, oneWay):
    x = [i for i,j in linCor]
    y = [j for i,j in linCor]
    for idx in xrange(1,len(linCor)):
        cor1 = lonlat2ID(x[idx-1], y[idx-1])
        cor2 = lonlat2ID(x[idx], y[idx])
        roadAdjList.addEdge(cor1, cor2, distanceCal(linCor[idx-1], linCor[idx]), 0, oneWay)


for linObj in road_list_osm:
    oneWayFlag = False
    if linObj['geometry']['type']=='LineString':
        linCor = linObj['geometry']['coordinates']
        #oneWayFlag = (linObj['properties']['oneway']=='yes')
        lineNum += len(linCor)
        addPath2AdjList(linCor, roadAdjList, oneWayFlag)  
    elif linObj['geometry']['type']=='MultiLineString':
        for i in range(len(linObj['geometry']['coordinates'])):            
            linCor = linObj['geometry']['coordinates'][i]
            #oneWayFlag = (linObj['properties']['oneway']=='yes')
            lineNum += len(linCor)
            addPath2AdjList(linCor, roadAdjList, oneWayFlag) 
    else:
        print 'type '+ linObj['geometry']['type'] +' unspecified'   

print 'Before data clean Up...'
print 'total number of line segments:' +str(lineNum)
print 'with total number of vertices: '+str(roadAdjList.numVertices)
###Data clean Up
#Step 1.
#Clean up small connected components
#filter out all isolated objects<50 nodes
###
print 'Clean Up isolated small islands...'
minConCt = 50
visited = set()
ndKeys = roadAdjList.getVertices();
for nd in ndKeys:
    if nd not in visited:
        conComponent = {'conND': set(), 'ct': 0}
        roadAdjList.ccBFS(nd, visited, conComponent)
        print conComponent['ct']
        if conComponent['ct'] < minConCt:
            for delnd in conComponent['conND']:
                roadAdjList.removeVertex(delnd)


###
#Step 2.
#Iterative clean up of spur nodes
#that is nodes with only one connected neighbor
###
print 'Clean Up spur nodes...'
delVnum = 1
roundNum= 0
totalDelN = 0
ndKeys = roadAdjList.getVertices()
ndKeys = Set(ndKeys)
delVnum = 1
while (delVnum>0):
    roundNum += 1
    delVnum = 0
    delVertex = Set() 
    for u in ndKeys:
        if roadAdjList.vertList[u].neighborNumber()==1:
            delVnum += 1
            v = roadAdjList.vertList[u].getConnections()[0]
            roadAdjList.removeVertex(u)
            roadAdjList.removeEdge(v, u)
            delVertex.add(u)
    for u in delVertex:
        ndKeys.remove(u)
    totalDelN += delVnum
    print ('{} spur nodes removed in round {}').format(delVnum, roundNum)
print ('total number of spur nodes removed is {}'.format(totalDelN))


###
#Step 3
#Coarse Grain representation of the graph
#Combine nodes at the road intersection, s.t. 
#I can combine parallel roads in step 4
###
print 'Clean redundant nodes...'
delVnum = 1
roundNum= 0
resDis = 20
totalDelN = 0
ndKeys = roadAdjList.getVertices()
ndKeys = Set(ndKeys)
delVnum = 1
while (delVnum>0):
    roundNum += 1
    delVnum = 0
    delVset = Set()
    addVset = Set()
    for u in ndKeys:
        #if u is an intersection
        if (u in roadAdjList.vertList) and (roadAdjList.vertList[u].neighborNumber()>2):
            combineSet = Set()
            checkQueue = Queue()
            visited = Set()

            visited.add(u)
            checkQueue.put(u)
            #if the connected node v is also an intersection and dis(u, v)<minDis, combine
            while not checkQueue.empty():
                curNd = checkQueue.get()
                for v in roadAdjList.vertList[curNd].getConnections():
                    if (v in roadAdjList.vertList and\
                        roadAdjList.vertList[v].neighborNumber()>2 \
                        and distanceCal(v, curNd)< resDis):
                       if curNd not in combineSet:
                           combineSet.add(curNd)
                       if v not in combineSet:
                           combineSet.add(v)
                       if v not in visited:
                           visited.add(v)
                           checkQueue.put(v)
                       
            if combineSet:       
                delVnum = delVnum+len(combineSet)-1    
                newKey = roadAdjList.combine(combineSet)
                delVset = delVset.union(combineSet)
                addVset.add(newKey)
    for u in delVset: 
        ndKeys.discard(u)
    for u in addVset:
        ndKeys.add(u)            
    totalDelN += delVnum 
    print ('{} nearby intersection nodes removed in round {}').format(delVnum, roundNum)
print ('total number of nearby intersection nodes removed is {}'.format(totalDelN))


###
#Step 4.
#delete unnecessary intermediate nodes
#If a node has only one in-edge and one out-edge and the two edges are 
#almost parallel to each other, delete the intermediate node
#It's also an iterative process
###
print 'Clean redundant intermediate nodes...'
delVnum = 1
roundNum= 0
totalDelN = 0
ndKeys = roadAdjList.getVertices()
ndKeys = Set(ndKeys)
delVnum = 1
while (delVnum>0):
    roundNum += 1
    delVnum = 0
    delVertex = Set() 
    for u in ndKeys:
        nb = roadAdjList.vertList[u].getConnections()
        if len(nb)==2:
            vec1 = directionalVec(nb[0], u)  
            vec2 = directionalVec(nb[1], u)           
            prod = innerProduct(vec1, vec2)
            if abs(prod)>0.9:
                roadAdjList.removeMiddlePt(u)
            delVnum += 1
            delVertex.add(u)
    for u in delVertex:
        ndKeys.remove(u)
    totalDelN += delVnum
    print ('{} intermediate nodes removed in round {}').format(delVnum, roundNum)
print ('total number of intermediate nodes removed is {}'.format(totalDelN))
roadAdjList.recountVandE()

print 'road Adjacency List generated'
print 'total number of line segments:' +str(lineNum)
print 'with total number of vertices: '+str(roadAdjList.numVertices)
print 'with total number of edges: '+str(roadAdjList.numEdges)
pickle.dump(roadAdjList, open('CamBosRoadMapFT.p', 'wb'))

