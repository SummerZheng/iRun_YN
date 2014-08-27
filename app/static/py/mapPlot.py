#plot the road for visualization
import matplotlib.pyplot as plt 
dpi = 800
fig = plt.figure(figsize=(20, 20),dpi=dpi)
ax = fig.gca()

for linObj in road_list:
    if linObj['geometry']['type']=='LineString':
        linCor = linObj['geometry']['coordinates']
        x = [i for i,j in linCor]
        y = [j for i,j in linCor]
        ax.plot(x, y,'o-')
        #print len(linCor)
        pathLen = calPathDis(linCor) 
        #print linObj['properties']['osm_id']
        #print pathLen
        
    elif linObj['geometry']['type']=='MultiLineString':
        for i in range(len(linObj['geometry']['coordinates'])):
            linCor = linObj['geometry']['coordinates'][i]
            x = [i for i,j in linCor]
            y = [j for i,j in linCor]
            ax.plot(x, y,'o-')
            #print len(linCor)
            pathLen = calPathDis(linCor) 
            #print linObj['properties']['osm_id']
            #print pathLen
    else:
        print 'type '+ linObj['geometry']['type'] +' unspecified'    
ax.axis('scaled')

