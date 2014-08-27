# Load the dictionary back from the pickle file.
import pickle
from distCal import lonlat2ID, cor2ID, distanceCal, calPathDis, R
from Vertex import Vertex
from Graph import Graph

roadAdjList = pickle.load( open( "testRoadMap.p", "rb" ) )

startNode = [0, 0]

lookUpNode = Vertex((-71.0795, 42.3620))
dist = roadAdjList.findNearestNode(lookUpNode, startNode)
print dist
print startNode
startNode = cor2ID(startNode)
endNode = [0, 0]
lookUpNode = Vertex((-71.0841, 42.3627))
dist = roadAdjList.findNearestNode(lookUpNode, endNode)
print dist
print endNode
endNode = cor2ID(endNode)
v = (startNode[0], startNode[1])
print roadAdjList.getVertex(v)
print distanceCal(startNode, endNode) #~1000meters
targetDis = 400
#path = np.array
path = []
dis = roadAdjList.findPath(startNode, endNode, targetDis, path)
print dis
print path
