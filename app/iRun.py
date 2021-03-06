import sys
from json import loads as JSONLoad;
from os.path import exists as Exists;
from math import sin, cos, sqrt, atan2, acos, radians, exp
from random import randint, random, seed
from operator import itemgetter
from Queue import Queue
from sets import Set
from prioritydictionary import priorityDictionary
import psycopg2
###
#Constants
###
R = 6373000
maxVal = 99999.9
meterPerLat = 82190.6
meterPerLng = 111230

###
#Basic distance and direction Calculation function
###
def cor2ID(cor):
    #convert list to tuple to serve as node key
    tp = (cor[0], cor[1])
    return tp

def distanceCal4par(lon1, lat1, lon2, lat2):
    #compute the distance between (lon1, lat1) and (lon2, lat2)
    lon1 = radians(lon1)
    lat1 = radians(lat1)
    lon2 = radians(lon2)
    lat2 = radians(lat2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    return distance  

def distanceCal(cor1, cor2):
    return distanceCal4par(cor1[0], cor1[1], cor2[0], cor2[1])


def calPathDisSlow(linCor):
    #Calculate the tot dis of entire path from scratch
    pathLen = 0
    for idx in xrange(1,len(linCor)):
        delLen = distanceCal(linCor[idx], linCor[idx-1])
        #print delLen
        pathLen += delLen
    return pathLen;     

def lenCal(vec):
    #length of vector
    return  sqrt(vec[0]**2+vec[1]**2)

def directionalVec(u, v):
    #return the unit directional vetor from pt u to pt v
    vec = ((u[0]-v[0])*meterPerLng, (u[1]-v[1])*meterPerLat)
    vecLen = lenCal(vec)
    vec = (vec[0]/vecLen, vec[1]/vecLen)
    return vec

def innerProduct(u, v):
    #suppose u and v are already unit vector
    return u[0]*v[0]+u[1]*v[1]

###
#Scoring function
###    
def distScore(curDis, targetDis):
    #penalize on the difference between current
    #distance and target distance
    return (curDis-targetDis)**2/targetDis**2

#p is onePath <type list>
def turnScore(p):
    #penalize on turns
    score=0
    if (len(p)>=3):
        for i in xrange(0, (len(p) - 2)):
            u = directionalVec(p[i], p[i+1])
            v = directionalVec(p[i+1], p[i+2])
            prod = innerProduct(u, v)
            prod = min(1,max(prod,-1))
            angle = acos(prod)  #in radians
            score=score+angle            
    return score

#p is onePath <type list>
def repScore(p, curDis):
    #penalize on repetition of path
    score = 0
    edgeSet = Set()
    for idx in xrange(1, len(p)):
        key = (p[idx-1], p[idx])
        alterKey = (p[idx], p[idx-1])
        if key not in edgeSet:
            edgeSet.add(key)
        else:
            score += distanceCal(p[idx], p[idx-1])
        if alterKey not in edgeSet:
            edgeSet.add(alterKey)    
        else:
            score += distanceCal(p[idx], p[idx-1])
    return score/curDis


#p is onePath <type list>, curDis targDist double
def totScoreCal(path, curDis, targetDis):
    #total penalize score, ratios are chosen s.t. penalty 
    #coming from different sources have similar variance
    turnRatio = 0.02
    disRatio = 10
    repRatio = 10
    
    tScore = turnScore(path)
    dScore = distScore(curDis, targetDis)
    rScore = repScore(path, curDis)
    
    totScore = turnRatio*tScore + disRatio*dScore + repRatio*rScore      
    return totScore

###
#Classes
###

###
#Class Vertex
###
class Vertex:
    #cor is a tuple of (lon, lat)
    def __init__(self, cor):
        self.id = cor
        self.connectedTo = {}

    def addNeighbor(self, nbrID, dist=0, score=0):
        self.connectedTo[nbrID] = [dist, score]
      
    def __str__(self):
        #print overload 
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
    
###
#Class Graph
###
class Graph(Vertex):
    def __init__(self):
        self.vertList = {}
        self.numVertices = 0
        self.numEdges= 0

    def recountVandE(self):
        self.numVertices = 0
        self.numEdges = 0
        for u in self.getVertices():
            self.numVertices += 1
            self.numEdges += len(self.vertList[u].getConnections())
        
    def addVertex(self, v):
        self.numVertices += 1
        newVertex = Vertex(v)
        self.vertList[v] = newVertex
        return newVertex

    def getVertex(self,n):
        if n in self.vertList:
            return self.vertList[n]
        else:
            return None

    def __contains__(self,n):
        return n in self.vertList

    #note that f, t are tuples cor(lon, lat) here
    def addEdge(self, f, t, dist=0, score=0, oneWay=False):
        if f not in self.vertList:
            nv = self.addVertex(f)
        if t not in self.vertList[f].getConnections():
            self.numEdges += 1
            self.vertList[f].addNeighbor(t, dist, score)
        if not oneWay:
            if t not in self.vertList:
                nv = self.addVertex(t)
            if f not in self.vertList[t].getConnections():
                self.numEdges += 1
                self.vertList[t].addNeighbor(f, dist, score)

    def getVertices(self):
        return self.vertList.keys()
            
    def __str__(self):
        for v in self.vertList:
            print self.vertList[v]
        return ''

    def removeVertex(self, delVID):
        if delVID in self.vertList:
            self.numVertices -= 1
            self.numEdges -= len(self.vertList[delVID].getConnections())
            del self.vertList[delVID]

    #Note this only delete the edge from u to v, not vice versa
    def removeEdge(self, u, v):
        if u in self.vertList:
            if v in self.vertList[u].getConnections():
                self.numEdges -= 1
                [dis, score] = self.vertList[u].connectedTo[v]
                del self.vertList[u].connectedTo[v]
                return (dis, score)  
            else:
                return (-1, 0)
    
    #This function remove the middle point u and concatenate its
    #in and out edge
    def removeMiddlePt(self, u):
        twoNeighbors = self.vertList[u].getConnections()
        for v in twoNeighbors:
            self.removeEdge(v, u)
        self.addEdge(twoNeighbors[0], twoNeighbors[1])
        self.removeVertex(u)
                 
    #combine all nodes in the combineSet, return their COM combined newNode
    def combine(self, combineSet):
        x=0
        y=0
        for u in combineSet:
            x+=u[0]
            y+=u[1]
        newND = (x/len(combineSet), y/len(combineSet))
        self.addVertex(newND)
        for u in combineSet:
            for nb in self.vertList[u].getConnections(): 
                if nb not in combineSet:
                    self.removeEdge(nb, u)
                    self.addEdge(nb, newND)
                    self.addEdge(newND, nb)
            self.removeVertex(u)
        return newND   

    def calPathDis(self, path):
        #Calculate the tot dis of entire path from preCalDist
        pathLen = 0
        for idx in xrange(1,len(path)):
            fNode = path[idx-1]
            tNode = path[idx]
            pathLen += self.vertList[fNode].connectedTo[tNode][0]
        return pathLen; 

    def findNearestNode(self, lookUpNode, NNnode):
        #"find the closest node to the geocoded location in the roadAdjList" 
        minDist = maxVal #sys.float_info.max 
        for node in self.vertList:
            curDist = distanceCal(node, lookUpNode)
            #curDist = Vertex(node).dist2(lookUpNode)
            #curDist = distanceCalraw(node.getLat(), node.getLon(), lookUpLat, lookUpLon)
            if curDist < minDist:
                minDist = curDist
                NNnode[1] = node[1]
                NNnode[0] = node[0]
        return minDist

    def __iter__(self):
        return iter(self.vertList.values())   
    
    def ccBFS(self, startN, visited, conComponent):
        ###
        #This is to count the number of vertices inside each connected component
        #remove isolated islands
        ###
        visited.add(startN)
        conComponent['conND'].add(startN)
        conComponent['ct']+=1
        BFSqueue = Queue()
        BFSqueue.put(startN)
        while not BFSqueue.empty():
            nd = BFSqueue.get()        
            if nd in self.vertList:
                for conND in self.vertList[nd].getConnections():
                    if conND not in conComponent['conND']:
                        visited.add(conND)
                        conComponent['conND'].add(conND)
                        conComponent['ct']+=1
                        BFSqueue.put(conND)

    def Dijkstra(self, node_start, node_end=None):
        ###
        # Dijkstra's algorithm
        # only use part of the the graph, i.e. aGraph (in the approximity of startPt 
        # and endPt) to build Dict gDict in order to reduce complexity
        ###
        distances = {}      
        previous = {}       
        Q = priorityDictionary()
    
        for v in self.vertList:
            distances[v] = maxVal
            previous[v] = None
            Q[v] = maxVal
    
        distances[node_start] = 0
        Q[node_start] = 0
    
        for v in Q:
            if v == node_end: break

            for u in self.vertList[v].getConnections():
                cost_vu = distances[v] + self.vertList[v].connectedTo[u][0]            
                if u in self and cost_vu < distances[u]:
                    distances[u] = cost_vu
                    Q[u] = cost_vu
                    previous[u] = v

        if node_end:
            return {'dist': distances[node_end], 
                    'path': self.path(previous, node_start, node_end)}
        else:
            return (distances, previous)

    ## Finds a paths from a source to a sink using a supplied previous node list.
    # @param previous A list of node predecessors.
    # @param node_start The source node of the graph.
    # @param node_end The sink node of the graph.
    #
    # @retval [] Array of nodes if a path is found, an empty list if no path is 
    # found from the source to sink. 
    def path(self, previous, node_start, node_end):
        route = []

        node_curr = node_end    
        while True:
            route.append(node_curr)
            if previous[node_curr] == node_start:
                route.append(node_start)
                break
            elif previous[node_curr] == None:
                return []
        
            node_curr = previous[node_curr]
    
        route.reverse()
        return route

    def BestFirstSearch(self, endN, frontier, curPath, curDis):
        ###
        #This Greedy Search Algorithm always prioritize the path that get closer to endN
        #Right now doesn't consider the length of the path
	###
        pathHash = set()
        while curPath is not None:
            curNode = curPath.heappop()
            if curNode==endN:
                return;
            pathHash.add(curNode)
            for v in self.vertList[curNode].getConnections():
                if v not in pathHash and v not in curPath:
                    frontier.append(v)
                elif v in frontier:
                    incumbent = frontier[v]
        return            

    def MonteCarloBestPath(self, startN, endN, targetDis):
        if endN==startN:
            self.runLoop(startN, targetDis, successPath)####FIXME

        shortestPath = self.Dijkstra(startN, endN)
        print ('shortest Path dist between the points are {}').format(shortestPath['dist'])
        
        seed(3) 
        numStep=100
    
        bestPath = shortestPath['path']
        lastPath = shortestPath['path']
        bestScore = totScoreCal(lastPath, shortestPath['dist'], targetDis)        
        lastScore=bestScore
        bestDis = shortestPath['dist']

        if(shortestPath['dist'])>targetDis:
            print ('The shortest path dist {} is already shorter than targetDis').format(shortestPath['dist'])
            print ('current score is {}').format(bestScore)
            return {'path': bestPath, 'dist': bestDis, 'score': bestScore, 'tooShort': True}
  
        vKeys = self.getVertices()
        alpha = 1
        beta = 1
        for i in range(0, numStep):
            #if i%100==0:
            #    print ('iteration {}, current bestScore {}').format(i, bestScore)
            n = len(lastPath)
            r1 = randint(0, n-1)
            r2 = randint(0, n-2)
            if(r2 >= r1):
                r2 += 1
            n1=min(r1,r2)
            n2=max(r1,r2)   
            
            randIx = randint(0, self.numVertices-1)
            e = vKeys[randIx]
            while e==lastPath[n1] or e==lastPath[n2]:
                randIx = randint(0, self.numVertices-1)
                e = vKeys[randIx]
            nPath1 = self.Dijkstra(lastPath[n1], e)
            nPath2 = self.Dijkstra(e, lastPath[n2])
            if not nPath1['path'] or not nPath2['path']:
                continue
            newPath = lastPath[0:n1]+nPath1['path']+nPath2['path'][1:-1]+lastPath[n2:]
            newDis = self.calPathDis(lastPath[0:n1]) + nPath1['dist'] + \
                      nPath2['dist']+self.calPathDis(lastPath[n2:-1])
            totScore = totScoreCal(newPath, newDis, targetDis)            
            
            if (totScore<=lastScore):
                lastPath = newPath
                lastScore=totScore
                if(lastScore < bestScore):
                    bestDis = newDis
                    bestScore=lastScore
                    bestPath=lastPath
            else:
                prob=alpha*exp(beta*(lastScore - totScore))
                if(random()<prob):
                    lastPath = newPath
                    lastScore=totScore
        print ('bestScore is {}, dist is').format(bestScore, bestDis)  
        return {'path': bestPath, 'dist': bestDis,'score': bestScore, 'tooShort': False}
            

###
#Web Interaction
###   
def GeoCode(address):
    from urllib2 import urlopen as UrlOpen;
    from urllib import quote as Quote;
    ###
    # Encode query string into URL
    ###
    url = 'https://maps.googleapis.com/maps/api/geocode/json?address={}&sensor=false&key=AIzaSyBbynOzNqQIQXQGlDGH18A7LrW79D0BiWI'.format(Quote(address));
    ###
    # Call API and extract JSON
    ###
    print 'Calling Google Maps API for ' + address;
    #PrintNow('Calling Google Maps API for `{:s}` ... '.format(address), end = '');
    json = UrlOpen(url).read();
    json = JSONLoad(json.decode('utf-8'));
    ###
    # Extract longitude and latitude
    ###
    if json.get('status') == 'ZERO_RESULTS':
        latitude, longitude = None, None;
        ###
        print 'address is not found'
        #PrintNow('it was not found');
    else:
        latitude, longitude = (value for key, value in sorted(json.get('results')[0].get('geometry').get('location').items()));
        ###
        print('it is located at {:f}/{:f}'.format(longitude, latitude));
    ###
    return (longitude, latitude);

def GeoJsonify(geoItem):
    '''http://en.wikipedia.org/wiki/GeoJSON''';
    ###
    if isinstance(geoItem, list):
        geoJSON = {  
                 'type' : 'Feature',
                 'properties': {},
                 'geometry' :{
                    'type' : 'LineString',
                    'coordinates': geoItem,
                 }
            };
    ###
    elif isinstance(geoItem, tuple):   
        geoJSON = {
            'type' : 'Feature',
            'geometry' : {
                'type' : 'Point',
                'coordinates' : [geoItem[1], geoItem[0]],
            }
        };
    return geoJSON;

def inBounds(node, bounds):
    #bounds = [[minX, minY], [maxX, maxY]]
    flag1 = (node.getLat()<bounds[1][1] and node.getLat()>bounds[0][1])
    flag2 = (node.getLon()<bounds[1][0] and node.getLon()>bounds[0][0])
    if  flag1 and flag2:
        return True
    return False

def buildDict(vSet, gDict):
    ###
    # This is a auxiliary function for Dijkstra's shortest path algorithm,
    ### 
    for v in vSet:
        gDict[v.getID()] = {'Dist': maxVal, 'pred':None}
    return  


def createMiniWorld(miniGraph, startPt, endPt): 
    #define the boundary of the miniworld
    padding = 0.01
    minLng = min(startPt[0], endPt[0])-padding
    maxLng = max(startPt[0], endPt[0])+padding
    minLat = min(startPt[1], endPt[1])-padding
    maxLat = max(startPt[1], endPt[1])+padding
    try:
        conn = psycopg2.connect("host = 'localhost' port = '5432' dbname='cambosroad' user = 'postgres' password='haha'")
        #conn = psycopg2.connect("dbname='CamBosRoad' user = 'postgres' host = 'localhost' password='*******'")
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
        miniGraph.addEdge(fnode, tnode, edge[4], edge[5], True)
    return [[minLat, minLng],[maxLat, maxLng]]

    
def PathTestMashUp(startPt, endPt, runDis):
    targetDis = runDis*1000
   
    startCor = GeoCode(startPt);
    endCor = GeoCode(endPt)
    
    miniGraph = Graph()
    bounds = createMiniWorld(miniGraph, startCor, endCor)
    
    startNode = [0, 0]
    dist = miniGraph.findNearestNode(startCor, startNode)
    if dist == maxVal:
        print 'Invalid Starting Position'
        return None
    print 'the closest node found to startPt is '+ str(startNode) +', with dist '+str(dist)
    endNode = [0, 0]
    dist = miniGraph.findNearestNode(endCor, endNode)
    if dist == maxVal:
        print 'Invalid Ending Position'
        return None
    print 'the closest node found to endPt is '+str(endNode) +', with dist '+str(dist)
    
    startNode = cor2ID(startNode)
    endNode = cor2ID(endNode)
    myPath = miniGraph.MonteCarloBestPath(startNode, endNode, targetDis)
    
    pathLine = []
    for pt in myPath['path']:
        pathLine.append([pt[1], pt[0]])
    print 'The path found is:' 
    print pathLine
    print 'The actual path dis is '+ str(myPath['dist'])
    if myPath['tooShort'] is True:
        message = 'Your running goal is shorter than the shortest path distance between start and end point. You have to run at least {:.0f}m or take a bus in between'.format(myPath['dist'])
    else:
        message = 'The current path distance is {:.0f}m; and the current path penalty score is {:.4f}'.format(myPath['dist'], myPath['score'])
    json = {
            'bounds': bounds, 
            'startPt':GeoJsonify(startCor), 
            'endPt':GeoJsonify(endCor), 
            'dist': myPath['dist'],
            'path': GeoJsonify(pathLine),
            'score': myPath['score'],
	    'message':message,	    
            }
    return json

