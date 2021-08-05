#Import wichtige Bibliotheken
from OSMPythonTools.api import Api
from OSMPythonTools.overpass import overpassQueryBuilder
from OSMPythonTools.overpass import Overpass

import math
import srtm
import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate



overpass = Overpass()
api = Api()

# lon = geographische Länge  -- x -- München liegt auf 11°
# lat = geographische Breite -- y -- München liegt auf 48°

class RailNetwork:
    def __init__(self):
        self.edges = list()
        self.nodes = dict()

        self.earth_R = 6371001

    def bbxBuilder(self, startNodeID, endNodeID, a = 0.1):
        sn = self._getNode(startNodeID)
        en = self._getNode(endNodeID)

        if sn==False or en==False:
            return "Fehler bei den angegeben Nodes"

        # Zum Export der Daten aus OSM wird die Overpass Api benutzt
        # Dazu wird um die beiden Nodes eine Bounderybox gelegt
        # Diese ist so groß, dass sie die beide Punkte umfasst und
        # in jede Richtung um a*c erweitert ist. a ist dabei ein Faktor.
        # c ist der Koordinaten-Abstand der beiden Nodes
        c = math.sqrt((sn.lon()-en.lon())**2+(sn.lat()-en.lat())**2)

        # bbx = [lat_min, lon_min, lat_max, lon_max]
        bbx = []

        bbx.append(min(sn.lat(), en.lat()) - a*c)
        bbx.append(min(sn.lon(), en.lon()) - a*c)
        bbx.append(max(sn.lat(), en.lat()) + a*c)        
        bbx.append(max(sn.lon(), en.lon()) + a*c)
        
        return bbx

    def downloadBoundingBox(self, bbx):
        # bbx = [lat_min, lon_min, lat_max, lon_max]
        debug("Download Data with Bounding Box")
        
        # Erzeuge Query für Overpass Api
        query = overpassQueryBuilder(bbox=bbx, elementType='way', selector='"railway"="rail"', out='body')
        debug(query)
        
        # Führe die Datenabfrage mit der Overpass-Api durch
        try:
            debug("Führe Datenabfrage mit der Overpass Api durch...")
            bbx_rail = overpass.query(query)
            debug("Erfolgreich durchgeführt!")
        except:
            print("Fehler bei der Ausführung der Overpass-Abfrage")

        # Höhendaten
        try:
            debug("Lade Höhendaten...")
            ele_data = srtm.get_data()
            debug("Erfolgreich durchgeführt!")
        except:
            print("Fehler beim laden der Höhendaten")

        debug("Es wurden " + str(len(bbx_rail.ways())) + " Wege gefunden")

        for w in bbx_rail.ways():
            previousNode = None
            for n in w.nodes():
                if not n.id() in self.nodes:
                    # Erzeuge neue Instanz eines nodes()
                    nw = Node(n.id())
                    # Befülle diese mit Daten
                    nw.lon = n.lon()
                    nw.lat = n.lat()
                    nw.ele = ele_data.get_elevation(nw.lon, nw.lat)

                    nw.x, nw.y = self._lonlatInXY(bbx[1], bbx[0], nw.lon, nw.lat)

                    # Füge nw den RailNetwork hinzu:
                    self.nodes[nw.OSMId] = nw
                else:
                    nw = self.nodes[n.id()]

                if previousNode != None:
                    # Erzeuge eine Edge zwischen den aktuellen Node und dem vorherigen
                    e = Edge(nw, previousNode)
                    # Befülle ihn mit Daten aus dem übergeordneten Way
                    e.setSpeed(w.tag('maxspeed'))
                    if w.tag('bridge') == "yes":
                        e.bridge = True
                    if w.tag('tunnel') == "yes":
                        e.tunnel = True

                    # Füge den e den beiden Nodes hinzu
                    nw.edges.append(e)
                    previousNode.edges.append(e)

                    # Füge den e beim RailNetwork hinzu
                    self.edges.append(e)

                #for e in nw.edges:
                #    print(str(e.getNeighbor(nw).OSMId()))
                previousNode = nw

        debug("Es wurden " + str(len(self.nodes)) + " Nodes und " + str(len(self.edges)) + " Edges erstellt")
        
    def routing(self, waypoints):
        # waypoints ist eine Liste von Wegpunkten auf der Route
        # Prüfe ob jeder Node Teil des RailNetworks ist:
        for n in waypoints:
            if not n in self.nodes:
                print("Node " + str(n) + " ist nicht Teil des RailNetworks")

        # Neu Instanz einer Route
        r = Route()

        r.startNode = waypoints[0]
        r.endNode = waypoints[-1]
        
        # Führe nacheinander den AStern-Algorithmus durch und füge die einzelnen Teile aneinander
        for n in range(1, len(waypoints)):
            r.nodes += self._aStar(self.nodes[waypoints[n-1]], self.nodes[waypoints[n]])

        return r
            

    def _aStar(self, startNode, endNode, maxSteps = 1000):
        debug("Start A*")
        # Code copied from https://github.com/F6F/SimpleOsmRouter/blob/master/router/router.py and modified
        #exploredNodes = list() # in Wiki als closedList bezeichnet
        openlist = list() # in Wiki als openList bezeichnet
        #tmpNodes = list()

        currentNode = startNode
        openlist.append(currentNode)

        while ((currentNode != endNode) & (len(openlist) > 0) & (maxSteps > 0)):
            maxSteps -= 1
            currentNode = openlist[0]
            for i in openlist:
                debug(str(i.OSMId) + ": " + str(i.f))
                if currentNode.f > i.f:
                    currentNode = i
            
            debug("CurrentNode: " + str(currentNode.OSMId))
            openlist.remove(currentNode)
            if currentNode == endNode:
                # Wenn das Ziel gefunden ist, verlasse die Schleife
                debug("Ziel gefunden")
                break
            currentNode.explored = True
            for successor in currentNode.getNeighbors():
                if successor.explored:
                    continue
                tentative_g = currentNode.g + calcDistance(currentNode, i)
                debug("Nachbar: " + str(successor.OSMId) + " mit g=" + str(tentative_g))
                if successor in openlist and tentative_g >= successor.g:
                    continue
                successor.cameFrom = currentNode
                successor.g = tentative_g
                successor.f = tentative_g + calcDistance(successor, endNode)
                
                if not successor in openlist:
                    openlist.append(successor)

        debug(currentNode.OSMId)
        nowNode = endNode

        route = list()
        
        while nowNode.cameFrom != None:
            #print("https://www.openstreetmap.org/node/" + str(nowNode.OSMId))
            route.append(nowNode)
            nowNode = nowNode.cameFrom

        
        # Füge den startNode noch hinzu:
        route.append(startNode)

        # Reihenfolge der Liste umkehren, sodass der Start am Anfang steht
        route.reverse()

        return route

    def _getNode(self, nodeID):
        new = Node(nodeID)        
        try:
            n = api.query('node/' + str(nodeID))
            #print(n.tags())
            new.lon = n.lon
            new.lat = n.lat
            return new
        except:
            print("Fehler mit " + str(node))
            return False
    
    def _lonlatInXY(self, lon_min, lat_min, lon, lat):
        # Wandle die Punkte aus einem  in ein lokales X-Y-Koordinatensystem um
        xy = list()
        xy.append(math.sin((lon_min-lon)/180*math.pi)*math.cos(lat_min/180*math.pi)*self.earth_R)
        xy.append(math.sin((lat_min-lat)/180*math.pi)*self.earth_R)
        return xy


class Route:
    def __init__(self):
        self._parentRailNetwork = ""
        self.startNode = ""
        self.endNode = ""

        self.nodes = list()
        self.b_spline = list()

        self.center = list()
        self.radius = 0
        

    def plotRoute(self, mode=1):
        if mode == 1:
            # XY-Darstellung
            x = list()
            y = list()
            for p in self.nodes:
                x.append(p.x)
                y.append(p.y)
            
            plt.figure()
            
            fig, ax = plt.subplots()
            ax.add_patch(plt.Circle(self.center, self.radius, fill=False))
            ax.plot()
            
            plt.plot(x, y, 'ro', self.b_spline[0], self.b_spline[1], 'b')
            plt.legend(['Points', 'Interpolated B-spline', 'True'],loc='best')
            plt.axis([min(x)-1, max(x)+1, min(y)-1, max(y)+1])
            plt.title('B-Spline interpolation')
            plt.show()

        elif mode == 2:
            # Höhendarstellung
            pass
    
    def bSpline(self):
        plist = list()
        l = (len(self.nodes)-1) * 3
        
        for n in self.nodes:
            plist.append((n.x, n.y))

        ctr=np.array(plist)
        x=ctr[:,0]
        y=ctr[:,1]

        tck,u = interpolate.splprep([x,y], k=3, s=0)
        u=np.linspace(0, 1, num=l, endpoint=True)
        self.b_spline = interpolate.splev(u, tck)

    def _uvInXYZ(self, u, v):
        x = 2*u/(u**2+v**2+1)
        y = 2*v/(u**2+v**2+1)
        z = (u**2+v**2-1)/(u**2+v**2+1)

        return x, y, z

    def _minimize_z_error(self, x, y, z):
        A = np.c_[x, y, np.ones(x.shape)]
        C, resid, rank, singular_values = np.linalg.lstsq(A, z, rcond=None)
        
        return C[0], C[1], -1., -C[2]

    def _points_2_radius(self, U, V):
        # Siehe https://stackoverflow.com/questions/35118419/wrong-result-for-best-fit-plane-to-set-of-points-with-scipy-linalg-lstsq
        x = list()
        y = list()
        z = list()

        for i in range(len(U)):
            xyz = self._uvInXYZ(U[i], V[i])
            x.append(xyz[0])
            y.append(xyz[1])
            z.append(xyz[2])

        x = np.array(x)
        y = np.array(y)
        z = np.array(z)

        A, B, C, D = self._minimize_z_error(x, y, z)

        radius = math.sqrt(A**2 +  B**2 + C**2 - D**2)/abs(C-D)

        return radius, [A/(D-C), B/(D-C)]

    def _dist_2_plane(self, x, y, z, a, b, c, d):
        """Berechnet den Abstand eines Punktes zu einer Ebene"""
        return abs(a*x + b*y + c*z - d) / np.sqrt(a**2 + b**2 + c**2)

    def _abstand(self, p1, p2):
        return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2 )
    
    def estimateCurveRadius(self):
        ab = 0
        n = 0
        m = 5
        break_flag = False
        while True:
            while True:   
                start_u = self.b_spline[0][n:m]
                start_v = self.b_spline[1][n:m]

                self.radius, self.center = self._points_2_radius(start_u, start_v)
                for i in range(n, m):
                    p = [self.b_spline[0][i], self.b_spline[1][i]]
                    ab = abs(self._abstand(p, self.center) - self.radius)
                
                    #print(ab)
                    if ab > 1:
                        break_flag = True
                        break

                if break_flag: break
                #print("---------------")
                m += 1
                if m > len(self.b_spline[0]): break

            #print("Von " + str(n) + " bis " + str(m))
            print("Radius= " + str(self.radius))
            #print(self.center)

            n = m
            m += 5
            break_flag = False

            if m > len(self.b_spline[0]): break
        #self.plotRoute()
        

        
    def exportCSV(self):
        pass


class Node:
    def __init__(self, ID):
        self.OSMId = ID
        self.lon = 0
        self.lat = 0
        self.ele = 0
        self.x = 0
        self.y = 0
        self.edges = list()

        # Attribute für A*
        self.cameFrom = None
        self.g = 0.0
        self.f = 0.0
        self.explored = False
        self.known = False
    def getNeighbors(self):
        # Gibt eine Liste aller benachbarten Knoten zurück
        gn = list()
        for e in self.edges:
            gn.append(e.getNeighbor(self))
        return gn


class Edge:
    def __init__(self, node1, node2):
        self._node1 = node1
        self._node2 = node2
        self._maxspeed = 0
        self._length = 0.1
        self.gradient = self._getGradient()
        self.electrified  = False
        self.tunnel = False
        self.bridge = False

        self.itp_h = abs(node2.x - node1.x)
    def getNeighbor(self, origin):
        if self._node1 == origin:
            return self._node2
        elif self._node2 == origin:
            return self._node1
        else:
            return False
    def setSpeed(self, speed):
        self._maxspeed = speed
    def getSpeed(self, speed):
        return self._maxspeed
    def _getGradient(self):
        return (self._node1.ele - self._node2.ele) / self._length

        
def calcDistance(node1, node2):
    return math.sqrt((node1.x - node2.x)**2 + (node1.y - node2.y)**2)

def debug(text):
    debugLevel = 1
    if debugLevel == 0:
        print(text)



      

r = RailNetwork()
bbx = r.bbxBuilder(389926882, 602027313)
#bbx = r.bbxBuilder(389903144, 1201319848)
r.downloadBoundingBox(bbx)

f = r.routing([389926882, 602027313])
#f = r.routing([389903144, 1201319848])
f.bSpline()
f.estimateCurveRadius()
