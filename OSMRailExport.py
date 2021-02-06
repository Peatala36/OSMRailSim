#Import wichtige Bibliotheken
from OSMPythonTools.api import Api
from OSMPythonTools.overpass import overpassQueryBuilder
from OSMPythonTools.overpass import Overpass

import math
import srtm


overpass = Overpass()
api = Api()

#
class OSMRailExport():
    def __init__(self):
        pass
    def routing(self, startNodeID, endNodeID):
        sn = self._getNode(startNodeID)
        en = self._getNode(endNodeID)

        if sn==False or en==False:
            return "Fehler bei den angegeben Nodes"

        # Zum Export der Daten aus OSM wird die Overpass Api benutz
        # Dazu wird um die beiden Nodes eine Bounderybox gelegt
        # Diese ist so groß, dass sie die beide Punkte umfasst und
        # in jede Richtung um r*c erweitert ist. r ist dabei ein Faktor
        # c ist der Koordinaten-Abstand der beiden Nodes
        c = math.sqrt((sn.lon()-en.lon())**2+(sn.lat()-en.lat())**2)
        
        r = 0.1
        
        bbx_x_min = min(sn.lat(), en.lat()) - r*c
        bbx_x_max = max(sn.lat(), en.lat()) + r*c
        bbx_y_min = min(sn.lon(), en.lon()) - r*c
        bbx_y_max = min(sn.lon(), en.lon()) + r*c
        
        query = overpassQueryBuilder(bbox=[bbx_x_min, bbx_y_min, bbx_x_max, bbx_y_max],
                                     elementType='way', selector='"railway"="rail"', out='body')
        #query = '[timeout:25][out:json];(way["railway"="rail"](bbx_x_min, bbx_y_min, bbx_x_max, bbx_y_max);); (._;>;); out body;'
        bbx_rail = overpass.query(query)

        # Neue Instanz eines railNetworks:
        r = railNetwork()

        # Höhendaten
        ele_data = srtm.get_data()

        
        for w in bbx_rail.ways():
            previousNode = None
            for n in w.nodes():
                # Erzeuge neue Instanz eines nodes()
                nw = node(n.id())
                # Befülle diese mit Daten
                nw.lon = n.lon()
                nw.lat = n.lat()
                nw.ele = ele_data.get_elevation(nw.lon, nw.lat)

                # Füge nw den RailNetwork hinzu:
                r.nodes[nw.OSMId] = nw

                if previousNode != None:
                    # Erzeuge eine Edge zwischen den aktuellen Node und dem vorherigen
                    e = edge(nw, previousNode)
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
                    r.edges.append(e)

                previousNode = nw
        
        return r


    def _getNode(self, nodeID):
        new = node(nodeID)        
        try:
            n = api.query('node/' + str(nodeID))
            #print(n.tags())
            new.lon = n.lon
            new.lat = n.lat
            return new
        except:
            print("Fehler mit " + str(node))
            return False
    
    def _latlonInXY(self, node):
        pass

    def _aStar(self, railNetwork, startNodeID, endNodeID):
        # Code copied from https://github.com/F6F/SimpleOsmRouter/blob/master/router/router.py#L291 and modified
        exploredNodes = list()
        knownNodes = list()
        tmpNodes = list()

        maxSteps = 100

        nowNode = startNodeID
        knownNodes.append(nowNode)

        while ((nowNode != endNode) & (len(knownNodes) > 0) & (maxSteps > 0)):
            maxSteps -= 1
            knownNodes.remove(nowNode)
            exploreNodes.append(nowNode)
            nowNode.explored = True
            tmpNodes.extend(nowNode.getNeighbors)
            for i in tmpNodes:
                i.known = True
                if (i.explored == False):
                    pass


class vector2d:
    #Ähnlich zu https://docs.godotengine.org/en/stable/classes/class_vector2.html
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
    def length(self):
        return math.sqrt(self.x**2+self.y**2)

class node:
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
        self.distanceToDest = 0.0
        self.distanceFromStart = 0.0
        self.explored = False
        self.known = False
    def getNeighbors(self):
        gn = list()
        for e in self.edges:
            gn.append(e.geneighbor(self))
        return gn
    def 


class edge:
    def __init__(self, node1, node2):
        self._node1 = node1
        self._node2 = node2
        self._maxspeed = 0
        self._length = 0.1
        self.gradient = self._getGradient()
        self.electrified  = False
        self.tunnel = False
        self.bridge = False
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

class railNetwork:
    def __init__(self):
        self.edges = list()
        self.nodes = dict()
    def add_edges(self, node):
        self.edges.append(node)
    def add_nodes(self, x, y):
        self.nodes[x] = y
        
        
def calcDistance(self, node1, node2):
    return math.sqrt((node1.x - node2.x)**2 + (node1.y - node2.y)**2)
      

d = OSMRailExport()
s = d.routing(389926882, 8046673725)
