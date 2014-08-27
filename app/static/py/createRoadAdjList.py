def addPath2AdjList(linCor, roadAdjList):
    #linCor = array(linCor).squeeze()
    x = [i for i,j in linCor]
    y = [j for i,j in linCor]
    for idx in xrange(1,len(linCor)):
        cor1 = lonlat2ID(x[idx-1], y[idx-1])
        cor2 = lonlat2ID(x[idx], y[idx])
        roadAdjList.addEdge(cor1, cor2, distanceCal(linCor[idx-1], linCor[idx]),0)


roadAdjList = Graph()
for linObj in road_list:
    if linObj['geometry']['type']=='LineString':
        linCor = linObj['geometry']['coordinates']
        addPath2AdjList(linCor, roadAdjList)  
    elif linObj['geometry']['type']=='MultiLineString':
        for i in range(len(linObj['geometry']['coordinates'])):
            linCor = linObj['geometry']['coordinates'][i]
            addPath2AdjList(linCor, roadAdjList) 
    else:
        print 'type '+ linObj['geometry']['type'] +' unspecified'   

print roadAdjList.numVertices
print roadAdjList.numEdges

'''
for v in roadAdjList:
    for w in v.getConnections():
        print("( (%s , %s), (%.7f , %.7f),  %7.4f, %s)" % 
              (v.getLon(), v.getLat(), w.getId()[0],w.getId()[1], v.getLength(w), v.getScore(w)))
'''
