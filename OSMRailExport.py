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

# lon = geographische Länge -- x
# lat = geographische Breite -- y

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

        # bbx = [lon_min, lat_min, lon_max, lat_max]
        bbx = []

        bbx.append(min(sn.lat(), en.lat()) - a*c)
        bbx.append(min(sn.lon(), en.lon()) - a*c)
        bbx.append(max(sn.lat(), en.lat()) + a*c)        
        bbx.append(max(sn.lon(), en.lon()) + a*c)
        
        return bbx

    def downloadBoundingBox(self, bbx=[]):
        # bbx = [lon_min, lat_min, lon_max, lat_max]

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

                    nw.x, nw.y = self._lonlatInXY(bbx[0], bbx[1], nw.lon, nw.lat)

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
    def __init__(self, RailNetwork):
        self._r = RailNetwork

        self.nodes = list()

    def routing(self, nodes):
        # nodes ist eine Liste von Wegpunkten auf der Route
        # Prüfe ob jeder Node Teil des RailNetworks ist:
        for n in nodes:
            if not n in self._r.nodes:
                print("Node " + str(n) + " ist nicht Teil des RailNetworks")

        # Führe nacheinander den AStern-Algorithmus durch und füge die einzelnen Teile aneinander
        for n in range(1, len(nodes)):
            self.nodes += self._aStar(self._r.nodes[nodes[n-1]], self._r.nodes[nodes[n]])

            

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
        
        while nowNode.cameFrom != None:
            #print("https://www.openstreetmap.org/node/" + str(nowNode.OSMId))
            self.nodes.append(nowNode)
            nowNode = nowNode.cameFrom

        route = list()
        # Füge den startNode noch hinzu:
        route.append(startNode)

        # Reihenfolge der Liste umkehren, sodass der Start am Anfang steht
        route.reverse()

        return route
        

    def plotRoute(self, mode):
        if mode == 1:
            # XY-Darstellung
            x = list()
            y = list()
            for p in self.nodes:
                x.append(p.x)
                y.append(p.y)

            plt.plot(x, y)
            plt.show()

        elif mode == 2:
            # Höhendarstellung
            pass

    def interpolate(self):
        #Die folgende Funktion interpoliert aus dem Streckenzug einen kubischen Spline
        #Siehe https://de.wikipedia.org/wiki/Spline-Interpolation#Der_kubische_C%C2%B2-Spline
        
        s = len(self.nodes)
        #Koeffizientenmatrix a
        self.a = np.zeros((s,s))
        #Rechte Seite des Linearen Gleichungssystems b
        self.b = np.zeros((s,1))

        #Setze natürliche Randbedingungen
        self.a[0,0]=1
        self.a[s-1,s-1]=1

        print(self.nodes)
        
        #Befülle die Matrizen a und b
        for i in range(1, s-1):
            self.a[i, i-1] = self.edges[i-1].itp_h/6
            self.a[i, i] = (self.edges[i-1].itp_h+self.edges[i].itp_h)/3
            self.a[i, i+1] = self.edges[i].itp_h/6
           
            
            #self.b[i, 0] = (self.nodes[i+1].y-self.nodes[i].y)/self.edges[i].itp_h-(self.nodes[i].y-self.nodes[i-1].y)/self.edges[i-1].itp_h

        #Löse das Lineare Gleichungssystem
        self.m = np.linalg.solve(self.a,self.b)
    
        #self.m ist die Momentenmatrix
        return self.m
    
    def bSpline(self):
        plist = list()
        for key in self.nodes:
            plist.append((self.nodes[key].x, self.nodes[key].y))

        ctr=np.array(plist)
        x=ctr[:,0]
        y=ctr[:,1]

        tck,u = interpolate.splprep([x,y],k=3,s=0)
        u=np.linspace(0,1,num=1000,endpoint=True)
        out = interpolate.splev(u,tck)

        plt.figure()
        plt.plot(x, y, 'ro', out[0], out[1], 'b')
        plt.legend(['Points', 'Interpolated B-spline', 'True'],loc='best')
        plt.axis([min(x)-1, max(x)+1, min(y)-1, max(y)+1])
        plt.title('B-Spline interpolation')
        plt.show()


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
r.downloadBoundingBox(bbx)

f = Route(r)
route = f.routing([389926882, 602027313])
