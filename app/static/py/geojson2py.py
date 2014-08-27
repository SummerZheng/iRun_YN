###
#preSQL, convert geojson data into adjacency list representation
#and pickle dump
###

import json
import sys
from pprint import pprint
from distCal import lonlat2ID, cor2ID, distanceCal, calPathDis, R
from Vertex import Vertex
from Graph import Graph
import pickle
import psycopg2


json_data = open('CamBosRoadFT.geojson')
road_data =json.load(json_data)
road_list_osm = road_data['features']
json_data.close()
print 'data imported'

lineNum = 0
roadAdjList = Graph()

def addPath2AdjList(linCor, roadAdjList):
    x = [i for i,j in linCor]
    y = [j for i,j in linCor]
    for idx in xrange(1,len(linCor)):
        cor1 = lonlat2ID(x[idx-1], y[idx-1])
        cor2 = lonlat2ID(x[idx], y[idx])
        roadAdjList.addEdge(cor1, cor2, distanceCal(linCor[idx-1], linCor[idx]),0)


for linObj in road_list_osm:
    if linObj['geometry']['type']=='LineString':
        linCor = linObj['geometry']['coordinates']
        lineNum += len(linCor)
        addPath2AdjList(linCor, roadAdjList)  
    elif linObj['geometry']['type']=='MultiLineString':
        for i in range(len(linObj['geometry']['coordinates'])):            
            linCor = linObj['geometry']['coordinates'][i]
            lineNum += len(linCor)
            addPath2AdjList(linCor, roadAdjList) 
    else:
        print 'type '+ linObj['geometry']['type'] +' unspecified'   


print 'road Adjacency List generated'
print 'total number of line segments:' +str(lineNum)
print 'with total number of vertices: '+str(roadAdjList.numVertices)
print 'with total number of edges: '+str(roadAdjList.numEdges)
pickle.dump(roadAdjList, open('CamBosRoadMapFT.p', 'wb'))

