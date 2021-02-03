#Import wichtige Bibliotheken
from OSMPythonTools.api import Api
from OSMPythonTools.overpass import overpassQueryBuilder
from OSMPythonTools.overpass import Overpass


overpass = Overpass()
api = Api()

#
class OSMRailExport():
    def __init__(self):
        pass
    def routing(self, startNodeID, endNodeID):
        sn = self._getNode(startNode)
        en = self._getNode(endNode)

        if sn==False or en==False:
            return "Fehler bei den angegeben Nodes"

        c = math.sqrt(self.x**2+self.y**2)
        
        bbx_x_min = min(sn.lon, en.lon)
        bbx_x_max = max(sn.lon, en.lon)
        bbx_y_min = min(sn.lat, en.lat)
        bbx_y_max = min(sn.lat, en.lat)
        
        
        
        query="node(%s)->.selectedNode;way(bn.selectedNode);(._;>;);out;" % startNode
        n = overpass.query(query)
        print(n)


    def _getNode(self, nodeID):
        new = node()        
        try:
            n = api.query('node/' + str(node))
            #print(n.tags())
            new.lon = n.lon
            new.lat = n.lat
            return new
        except:
            print("Fehler mit " + str(node))
            return False
    
    def latlonInXY(self, node):
        


class vector2d:
    #Ähnlich zu https://docs.godotengine.org/en/stable/classes/class_vector2.html
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
    def length(self):
        return math.sqrt(self.x**2+self.y**2)

class graph:
    def __init__(self):
        self._nodes = list()
        self._edges = dict()
    def add_node(self, node):
        self._nodes.append(node)
    def add_edges(self, x, y):
        self._edges(x)=y

class node:
    def __init__(self):
        self.lon = 0
        self.lat = 0
        self.ele = 0
        self.x = 0
        self.y = 0

class edge:
    def __init__(self, node1, node2):
        self.node1 = node1
        self.node2 = node2
