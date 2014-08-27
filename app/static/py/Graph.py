###
#Class Graph, 
#inherit Class Vertex
#represented as adjacency list
###
from Vertex import Vertex
from operator import itemgetter
from prioritydictionary import priorityDictionary
from distCal import distanceCal, calPathDis, totScoreCal
from Queue import Queue
from sets import Set
from random import randint, random, seed
from math import exp
from numpy import array, average, var, amin, amax, percentile

maxVal = 99999.9

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

    def addEdge_directional(self, f, t, dist=0, score=0):
        if f not in self.vertList:
            nv = self.addVertex(f)
        if t not in self.vertList[f].getConnections():
            self.numEdges += 1
            self.vertList[f].addNeighbor(t, dist, score)

    def getVertices(self):
        return self.vertList.keys()
            
    def __str__(self):
        for v in self.vertList:
            print self.vertList[v]
        return ''

    def deepCopyVertex(self, oriV):
        vID = oriV.getID()
        if vID not in self.vertList:
            nv = self.addVertex(vID)
            for u in oriV.getConnections():
                if u not in self.vertList[vID].getConnections():
                    #Note that in the miniWold copy
                    #The edges are not necessarily symmetric, 
                    #thus only do directional copy
                    self.numEdges += 1
                    dist = oriV.connectedTo[u][0]
                    score = oriV.connectedTo[u][1]
                    self.vertList[vID].addNeighbor(u, dist, score)

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
             
    
    #This function combine adj list of v into u
    #and delete node v
    def combineV(self, u, v):
        self.removeEdge(u, v)
        self.removeEdge(v, u)
        #Create a new Vertex as the avg of the two nodes
        nn = ((u[0]+v[0])/2, (u[1]+v[1])/2)
        self.addVertex(nn)
        uvNeighbor = Set()
        if u not in self.vertList:
            print ('vertex u {} not found').format(u)
        for uNeighbor in self.vertList[u].getConnections():
            self.removeEdge(uNeighbor, u)
            self.addEdge(uNeighbor, nn)
            if uNeighbor not in uvNeighbor:
                uvNeighbor.add(uNeighbor) 
        if v not in self.vertList:
            print ('vertex v {} not found').format(v)         
        for vNeighbor in self.vertList[v].getConnections():
            self.removeEdge(vNeighbor, v)
            self.addEdge(vNeighbor, nn)
            if vNeighbor not in uvNeighbor:
                uvNeighbor.add(vNeighbor)
        for nb in uvNeighbor:
            self.addEdge(nn, nb)
        self.removeVertex(u)
        self.removeVertex(v)
     
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

    def BFS(self, startN, endN, targetDis, curNode, curDis, curPath, curPathHash, successPath):
        '''
         #BFS use backtracing method to search all possible path exhaustively, 
         #and only abort if travel too long, but hasn't reached endN
         #take seconds to search ~1000m path, for path>2000m crash the computer
	'''
        if curDis > targetDis*5/4:
            return 
        if (curNode!=endN):
            for v in self.vertList[curNode].getConnections():
                if v not in curPathHash:
                    curPath.append(v)
                    curPathHash.add(v)
                    curDis += distCal.distanceCal(curNode, v)
                    self.BFS(startN, endN, targetDis, v, curDis, curPath, curPathHash, successPath)
		    #print curDis
               	    curPathHash.remove(v)
                    curPath.remove(v)
                    curDis -= distCal.distanceCal(curNode, v)
        elif abs(targetDis-curDis)<targetDis/4:
            #Note that python list a=list b just assign by reference
            #To assign by value do a=b[:]  
            successPath.append(curPath[:])
        else:
            return    
   
    ## @package YenKSP
    # Computes K-Shortest Paths using Yen's Algorithm.
    #
    # Yen's algorithm computes single-source K-shortest loopless paths for a graph 
    # with non-negative edge cost. The algorithm was published by Jin Y. Yen in 1971
    # and implores any shortest path algorithm to find the best path, then proceeds 
    # to find K-1 deviations of the best path.

    ## Computes K paths from a source to a sink in the supplied graph.
    #
    # @param graph A digraph of class Graph.
    # @param start The source node of the graph.
    # @param sink The sink node of the graph.
    # @param K The amount of paths being computed.
    #
    # @retval [] Array of paths, where [0] is the shortest, [1] is the next 
    # shortest, and so on.
    #
    def ksp_yen(self, node_start, node_end, max_k=2):
        distances, previous = self.Dijkstra(node_start)
        #Final output A, list
        A = [{'dist': distances[node_end], 
              'path': self.path(previous, node_start, node_end)}]
        #priority dictionary
        B = []
        #set, paths so far
        distSet = Set()

        if not A[0]['path']: return A
    
        for k in range(1, max_k):
            for i in range(0, len(A[-1]['path']) - 1):
                node_spur = A[-1]['path'][i]
                path_root = A[-1]['path'][:i+1]
            
                edges_removed = []
                nodes_removed = []
                for path_k in A:
                    curr_path = path_k['path']
                    if len(curr_path) > i and path_root == curr_path[:i+1]:
                        [cost, score]  = self.removeEdge(curr_path[i], curr_path[i+1])
                        if cost == -1:
                            continue
                        edges_removed.append([curr_path[i], curr_path[i+1], cost, score])
                
                ############# 
                #for node in path_root and node!=node_spur:
                #    self.removeVertex(self, delVID)
                #####################  
                path_spur = self.Dijkstra(node_spur, node_end)
            
                if path_spur['path']:
                    path_total = path_root[:-1] + path_spur['path']
                    dist_total = distances[node_spur] + path_spur['dist']
                    
                    if dist_total not in distSet:
                        distSet.add(dist_total)
                        potential_k = {'dist': dist_total, 'path': path_total}
                        B.append(potential_k)
            
                for edge in edges_removed:
                    self.addEdge(edge[0], edge[1], edge[2], edge[3])
        
            if len(B):
                B = sorted(B, key=itemgetter('dist'))
                A.append(B[0])
                B.pop(0)
            else:
                break
        while B:
            A.append(B[0])
            B.pop(0)    
        return A


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
    #
    # @param previous A list of node predecessors.
    # @param node_start The source node of the graph.
    # @param node_end The sink node of the graph.
    #
    # @retval [] Array of nodes if a path is found, an empty list if no path is 
    # found from the source to sink.
    #
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
        #does not always finds path, needs to refine backtracing in future
        #FIXME
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

     
    def findPath(self, startN, endN, targetDis, k=1):
        curPath =[]
        curDis = 0
        curPath.append(startN)
        pathHash = set(curPath)
        if endN==startN:
            self.runLoop(startN, targetDis, successPath)
        else:      
            #use curPath as a stack to record the trail
            #dis = self.BestFirstSearch(endN, frontier, curPath, curDis)
            #successPath.append(curPath)
            if k==1:
                pathDict = self.Dijkstra(startN, endN)
            else:
                pathDict = self.ksp_yen(startN, endN, k)
            return pathDict
            #self.BFS(startN, endN, targetDis, startN, curDis, curPath, pathHash, successPath)
            #print successPath



    def MonteCarloBestPath(self, startN, endN, targetDis):
        shortestPath = self.Dijkstra(startN, endN)
        print ('shortest Path dist between the points are {}').format(shortestPath['dist'])
        seed(1) 

        bestPath = shortestPath['path']
        lastPath = shortestPath['path']
        worstPath = shortestPath['path']   
        worstDis = 0
        bestScore = totScoreCal(lastPath, shortestPath['dist'], targetDis)        
        lastScore=bestScore
        worstScore = 2.0

        if(shortestPath['dist'])>targetDis:
            print ('The shortest path dist {} is already shorter than targetDis').format(shortestPath['dist'])
            print ('current score is {}').format(bestScore)
            return shortestPath
        numStep=5      

        tScoreArr = []
        dScoreArr = []
        rScoreArr = []
        totScoreArr = []

        vKeys = self.getVertices()
        alpha = 1
        beta = 1
        for i in range(0, numStep):
            if i%100==0:
                print ('iteration {}, current bestScore {}').format(i, bestScore)
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
            newDis = calPathDis(lastPath[0:n1]) + nPath1['dist'] + \
                      nPath2['dist']+calPathDis(lastPath[n2:-1])
            [tscore, dscore, rScore, totScore] = totScoreCal(newPath, newDis, targetDis)
            
            tScoreArr.append(tscore)
            dScoreArr.append(dscore)
            rScoreArr.append(rScore)
            totScoreArr.append(totScore)
            
            if (totScore<=lastScore):
                lastPath = newPath
                lastScore=totScore
                if(lastScore < bestScore):
                    bestScore=lastScore
                    bestPath=lastPath
            else:
                if(totScore>worstScore):
                    worstScore = totScore
                    worstDis = newDis
                    worstPath = newPath
                prob=alpha*exp(beta*(lastScore - totScore))
                if(random()<prob):
                    lastPath = newPath
                    lastScore=totScore
        '''
        print 'tSocre Arr is'
        print tScoreArr
        print 'dSocre Arr is'
        print dScoreArr
        print 'totSocre Arr is'
        print totScoreArr
        '''
        tScoreArr = array(tScoreArr)
        dScoreArr = array(dScoreArr)
        rScoreArr = array(rScoreArr)
        totScoreArr = array(totScoreArr)

        print ('variance for tScore {}, dScore {}, rScore {}, totScore {}').format(
               tScoreArr.var(), dScoreArr.var(), rScoreArr.var(), totScoreArr.var())
        print ('min for tScore {}, dScore {}, rScore {}, totScore {}').format(
               amin(tScoreArr), amin(dScoreArr), amin(rScoreArr), amin(totScoreArr))
        print ('max for tScore {}, dScore {}, rScore {}, totScore {}').format(
               amax(tScoreArr), amax(dScoreArr), amax(rScoreArr), amax(totScoreArr))
        print ('75 quantile for tScore{}, dScore {}, rScore{}, totScore {}').format(
               percentile(tScoreArr, 75),  percentile(dScoreArr, 75), percentile(rScoreArr, 75), percentile(totScoreArr, 75))
        print ('25 quantile for tScore{}, dScore {}, rScore {}, totScore {}').format(
               percentile(tScoreArr, 25),  percentile(dScoreArr, 25), percentile(rScoreArr, 25), percentile(totScoreArr, 25))
        print ('mean for tScore {}, dScore {}, rScore {}, totScore {}').format(
               average(tScoreArr), average(dScoreArr), average(rScoreArr), average(totScoreArr))
        return {'path': bestPath, 'dist': calPathDis(bestPath),'worstPath':worstPath, 'wscore': worstScore, 'wdis': worstDis}
            

"""  
#Test            
g = Graph()
g.addEdge((0, 0),(0, 1),5, 3) 
g.addEdge((0, 0),(0, 5),2, 2)
g.addEdge((0, 1),(0, 2),4)
g.addEdge((0, 2),(0, 3),9)
g.addEdge((0, 3),(0, 4),7
    for w in v.getConnections():
        print("( %s , %s, %s, %s)" % (v.getID(), w, v.getLength(w), v.getScore(w)))

g.removeVertex((0, 1))
print 'vertex (0, 1) removed'
print g
[dis, score] = g.removeEdge((0, 0), (0, 5))

print 'edge (0, 0) -> (0, 5) removed'
print dis
print score
print g
newV = Vertex((0, 4))
newV.addNeighbor((1, 3), 7, 7)
print newV
g.deepCopyVertex(newV)
print 'new vertex added'
print g
"""
"""
        while (curNode!=endN):
            nextN = None
            minDis = maxVal
            for v in self.vertList[curNode].getConnections():
                if v not in pathHash:
                    dis2Des = distCal.distanceCal(endN, v)
                    if dis2Des<minDis:
                        nextN = v
                        minDis = dis2Des
            if nextN is not None:
                curPath.append(nextN)
                pathHash.add(nextN)
                curDis += distCal.distanceCal(curNode, v) 
                curNode = nextN
            else  
        return curDis



    def Dijkstra(self, start, end, path, gDict):
        ###
        # Dijkstra's algorithm
        # only use part of the the graph, i.e. aGraph (in the approximity of startPt 
        # and endPt) to build Dict gDict in order to reduce complexity
        ###
        pq = PriorityQueue()
        gDict[start]['Dist'] = 0
        pq.buildHeap([(maxVal, v) for v in gDict])
        while not pq.isEmpty():
            currentVert = pq.delMin()
            if(currentVert == end):
                break;
            for nextVert in self.vertList[currentVert].getConnections():
                if nextVert in gDict:
                    newDist = gDict[currentVert]['Dist'] + self.vertList[currentVert].connectedTo[nextVert][0]                
                    if newDist < gDict[nextVert]['Dist']:
                        gDict[nextVert]['Dist'] = newDist 
                        gDict[nextVert]['pred'] = currentVert
                        pq.decreaseKey(nextVert,newDist)
        v = end
        while((v!=start) and gDict[v]['pred']!=None):
            path.append(v)
            v = gDict[v]['pred']
        return gDict[end]['Dist']

"""
