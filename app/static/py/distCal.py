from math import sin, cos, sqrt, atan2, acos, radians
from sets import Set
R = 6373000
meterPerLat = 82190.6
meterPerLng = 111230
#~0.3% error with mapbox calculation, need to refine in the future

def lonlat2ID(lon, lat):
    tp = (lon, lat)
    return tp

def cor2ID(cor):
    tp = (cor[0], cor[1])
    return tp

def distanceCal4par(lon1, lat1, lon2, lat2):
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
    lon1 = radians(cor1[0])
    lat1 = radians(cor1[1])
    lon2 = radians(cor2[0])
    lat2 = radians(cor2[1])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    return distance    
    
def distScore(curDis, targetDis):
    return (curDis-targetDis)**2/targetDis**2

#p is onePath <type list>
def turnScore(p):
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
    turnRatio = 0.02
    disRatio = 10
    repRatio = 10
    
    tScore = turnScore(path)
    dScore = distScore(curDis, targetDis)
    rScore = repScore(path, curDis)
    
    totScore = turnRatio*tScore + disRatio*dScore + repRatio*rScore      
    return (tScore, dScore, rScore, totScore)

def calPathDis(linCor):
    pathLen = 0
    for idx in xrange(1,len(linCor)):
        delLen = distanceCal(linCor[idx], linCor[idx-1])
        #print delLen
        pathLen += delLen
    return pathLen;     

def lenCal(vec):
    return  sqrt(vec[0]**2+vec[1]**2)

def directionalVec(u, v):
    vec = ((u[0]-v[0])*meterPerLng, (u[1]-v[1])*meterPerLat)
    vecLen = lenCal(vec)
    vec = (vec[0]/vecLen, vec[1]/vecLen)
    return vec

def innerProduct(u, v):
    #suppose u and v are already unit vector
    return u[0]*v[0]+u[1]*v[1]
    
