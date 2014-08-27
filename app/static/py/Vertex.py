###
# Class node
###

from math import sin, cos, sqrt, atan2, radians
R = 6373000
maxVal = 99999.9

class Vertex:
    #cor is a tuple of (lon, lat)
    def __init__(self, cor):
        self.id = cor
        self.connectedTo = {}

    def addNeighbor(self, nbrID, dist=0, score=0):
        self.connectedTo[nbrID] = [dist, score]

    #print overload    
    def __str__(self):
        s = str(self.id) + ' connectedTo: '
        for x in self.connectedTo:
            s += str(x) + ' d='+str(self.connectedTo[x][0])
            s += ', s=' + str(self.connectedTo[x][1])+'; '
        return s
    
    def getConnections(self):
        return self.connectedTo.keys()
    
    def neighborNumber(self):
        return len(self.connectedTo)
 
    def getID(self):
        return self.id
    
    def getLon(self):
        return self.id[0]
    
    def getLat(self):
        return self.id[1]
    
    def getLength(self,nbrID):
        return self.connectedTo[nbrID][0]
    
    def getScore(self, nbrID):
        return self.connectedTo[nbrID][1]
    
    def dist2(self, nbr):
        lon1 = radians(self.getLon())
        lat1 = radians(self.getLat())
        lon2 = radians(nbr.getLon())
        lat2 = radians(nbr.getLat())
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c
        return distance
'''
#Test
v = Vertex((-71.355, 42.400))
print v
'''
