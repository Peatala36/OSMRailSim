###################################################
#Klassen zur Abbildung von Eisenbahn-Infrastruktur#
###################################################

import csv
import sys
import numpy as np

import pickle

class RailNetwork:
    def __init__(self):
        self.edges = dict()
        self.nodes = dict()

    def save(self, path):
        # Funktioniert noch nicht...
        f = open('dateiname.bin','wb')
        p = pickle.Pickler(f)
        p.dump(self.edges)
        f.close()

    def open(self, path):
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

        self._edge_1a = False
        self._edge_1b = False
        self._edge_2a = False
        self._edge_2b = False

        # Attribute für A*
        self.cameFrom = None
        self.g = 0.0
        self.f = 0.0
        self.explored = False
        self.known = False
        
    def setEdge(self, edge):
        if self._edge_1a == False and self._edge_1b == False and self._edge_2a == False and self._edge_2b == False:
            # Alle Plätze sind frei
            self._edge_1a = edge
            self.edges.append(edge)
            return
        else:
            # 1a ist bereits belegt, berechne Winkel und entscheide dann ob 1b oder 2a/b belegt wird:
            w = self._winkel(self._edge_1a, edge)
            print(w)
            # Ist der Winkel kleiner als 90° muss der neue Edge auf der gleichen Seite wie der bisherige liegen:
            if w < 90:
                # Wurde 1b schon belegt?
                if self._edge_1b == False:
                    self._edge_1b = edge
                    self.edges.append(edge)
                else:
                    # Fehlermeldung
                    print("Seite 1 vollständig belegt")
            else:
                # Ist 2a schon belegt?
                if self._edge_2a == False:
                    self._edge_2a = edge
                    self.edges.append(edge)
                # Ist 2b schon belegt?
                elif self._edge_2b == False:
                    self._edge_2b = edge
                    self.edges.append(edge)
                # Fehlermeldung:
                else:
                    print("Seite 2 vollständig belegt")
            return
        
    def getNeighbors(self):
        # Gibt eine Liste aller benachbarten Knoten zurück
        gn = list()
        # liegt self.cameFrom auf Seite 1 oder 2?
        if self.cameFrom == None:
            # self.cameFrom ist noch leer, weil A* gerade startet:
            for e in self.edges:
                gn.append(e.getNeighbor(self))
        elif self.cameFrom == self._edge_1a.getNeighbor(self) or self.cameFrom == self._edge_1b.getNeighbor(self):
            if self._edge_2a:
                gn.append(self._edge_2a.getNeighbor(self))
            if self._edge_2b:
                gn.append(self._edge_2b.getNeighbor(self))
        elif self.cameFrom == self._edge_2a.getNeighbor(self) or self.cameFrom == self._edge_2b.getNeighbor(self):
            if self._edge_1a:
                gn.append(self._edge_1a.getNeighbor(self))
            if self._edge_1b:
                gn.append(self._edge_1b.getNeighbor(self))
        return gn

    def _winkel(self, edge1, edge2):
        # Berechnet den Winkel zwischen zwei Edges, welche zwei Vektoren darstellen:
        print(edge1._node1.OSMId, edge1._node2.OSMId, edge2._node1.OSMId, edge2._node2.OSMId) 
        a = [(edge1._node1.x - edge1._node2.x), (edge1._node1.y - edge1._node2.y)]
        print(edge1._node1.x, edge1._node1.y, edge1._node2.x, edge1._node2.y)
        print(a)
        b = [(edge2._node1.x - edge2._node2.x), (edge2._node1.y - edge2._node2.y)]
        print(edge2._node1.x, edge2._node1.y, edge2._node2.x, edge2._node2.y)
        print(b)
        a_len = np.sqrt(np.dot(a, a))
        b_len = np.sqrt(np.dot(b, b))
        return abs(np.arccos(np.dot(a, b)/(a_len*b_len))*180/np.pi)


class Edge:
    def __init__(self):
        self._node1 = 0
        self._node2 = 0
        self._edgeID = 0
        self._maxspeed = 0
        self.length = 0.1
        self.radius = 0
        self.gradient = 0
        self.electrified  = False
        self.tunnel = False
        self.bridge = False

        self.itp_h = 0

    def createEdge(self, node1, node2):
        self._node1 = node1
        self._node2 = node2

        self._edgeID = nodesToEdgeID(node1, node2)
        self.itp_h = abs(node2.x - node1.x)

        self._node1.setEdge(self)
        self._node2.setEdge(self)
    
    def getNeighbor(self, origin):
        if self._node1 == origin:
            return self._node2
        elif self._node2 == origin:
            return self._node1
        else:
            return False
    def setSpeed(self, speed):
        self._maxspeed = speed
    def getSpeed(self):
        return self._maxspeed
    def _getGradient(self):
        return round((self._node1.ele - self._node2.ele) / self.length * 1000, 1)

def nodesToEdgeID(node1, node2):
    return str(min(node1.OSMId, node2.OSMId)) + "," + str(max(node1.OSMId, node2.OSMId))

def EdgeIdToNodes(edgeID):
    return edgeID.split(",")

#######################################################################################################################################################
#Klasse für Topologieknoten
class TopoKnoten():
    def __init__(self):
        self.x = 0
        self.name = ""
        self.halt = False
        self.kilometrierung = 0
        self.zwillingsKnoten = ""
        self.kante = ""
    def getNextKnoten(self):
        if not self.zwillingsKnoten.kante == "":
            if self.zwillingsKnoten.kante.knoten1 == self.zwillingsKnoten:
                return self.zwillingsKnoten.kante.knoten2
            else:
                return self.zwillingsKnoten.kante.knoten1

#Klasse für Topologiekanten
class TopoKante():
    def __init__(self, knoten1, knoten2):
        self.knoten1 = knoten1
        self.knoten2 = knoten2
        
        self.laenge = int(knoten2.x) - int(knoten1.x)
        #Radius evtl durch 1/Radius ersetzen?
        self.radius = 1
        self.steigung = 0
        self.vmax = 0    


# Abkürzungen für Schema:
# d: delimiter der csv-Datei
# x: x-Position des Fahrwegs
# v: Höchstgeschwindigkeit der Kante
# s: Steigung der Kante
# h: Ist der Knoten ein Halt?
# n: Name des Knoten
# k: Kilometrierung des Punktes

standardSchema={"d": ";", "x": 0, "v": 1, "s": 2, "h": 3, "n": 9}

#Klasse für Fahrwege
class Fahrweg():
    def __init__(self):
        self._kanten = list()

    def __iter__(self):
        return iter(self._kanten)

    def readDataFromFile(self, datei, schema=standardSchema):
        try:
            with open(datei) as csv_datei:
                csv_reader = csv.reader(csv_datei, delimiter=schema["d"])

        
                previous_row = ""
                for row in csv_reader:
                    # Erste Zeile überspringen:
                    if csv_reader.line_num == 1: continue

                    #print(row)
                    try:
                        # Eine Instanzen des TopoKnoten erzeugen:
                        knoten1 = TopoKnoten()
                        
                        knoten1.x = float(row[schema["x"]])
                    
                        if "k" in schema:
                            knoten1.kilometrierung = float(row[schema["k"]])
                        if "n" in schema:
                            knoten1.name = row[schema["n"]]
                        if "h" in schema:
                            knoten1.name = row[schema["h"]]
                    except:
                        print("Fehler beim erzeugen des TopoKnoten: ", sys.exc_info()[0])

                    try:     
                        if previous_row != "":
                            # Eine Instanz der TopoKante aus den zwei vorherigen Knoten erzeugen:
                            k = TopoKante(previous_knoten, knoten1)
                            if "r" in schema:
                                k.radius = previous_row[schema["r"]]
                            if "s" in schema:
                                k.steigung = float(previous_row[schema["s"]].replace(",", "."))
                            k.vmax = previous_row[schema["v"]]
                
                            self._kanten.append(k)
                    except:
                        print("Fehler beim erzeugen des TopoKante: ", sys.exc_info()[0])
            
                    previous_row = row
                    previous_knoten = knoten1

        except:
            print("Fehler bei readDataFromFile: ", sys.exc_info()[0])
        print("Es wurden ", len(self._kanten), " Kanten erzeugt!")
        
    def getVmax(self):
        vmax = 0
        for i in self._kanten:
            if vmax<int(i.vmax): vmax = int(i.vmax)
        return vmax
    def getVmin(self):
        vmin = 1000
        for i in self._kanten:
            if vmin>int(i.vmax): vmin = int(i.vmax)
        return vmin
    def getLength(self):
        #Warum funktioniert self._kanten[0].laenge nicht?
        return int(self._kanten[-1].knoten2.x) - int(self._kanten[0].knoten1.x)
    def getSpecificLineResistanceForce(self, x):
        i = 0
        f = 0

        anzahl_kanten = len(self._kanten)
        for kante in self._kanten:
            #print(str(kante.knoten1.x), ";", str(kante.knoten2.x))
            if kante.knoten1.x < x and kante.knoten2.x > x:
                #print("Kante gefunden! Kante Nr.: ", str(self._kanten.index(kante)))
                i = float(kante.steigung)
                #Röckl
                if kante.radius < 300:
                    f = 0.5 / (kante.radius - 30)
                else:
                    f = 0.65 / (kante.radius - 55)
                break
        return i + f
