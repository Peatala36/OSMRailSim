###################################################
#Klassen zur Abbildung von Eisenbahn-Infrastruktur#
###################################################


import xml.etree.ElementTree as ET
import copy
import math
import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate

#Allgemeine, abstrakte Klassen
#=============================

#Klasse für allgemeine Topologieelemente
class topologieElement:
    def __init__(self, bezeichnung):
        self.bezeichnung = bezeichnung

#Allgemeine Klasse für Geoinformationen
class geoinformation:
    def __init__(self, lon, lat, z):
        self.lon = lon
        self.lat = lat
        self.x = 0
        self.y = 0
        self.z = z

#Allgemeine Klasse für einen Datenstapel
class dataStack:
    def __init__(self):
        self._stack = list()
    def add(self, x):
        self._stack.append(x)
    def delLast(self):
        del self._stack[-1]


#Spezielle Klassen
#=================

#Klasse für Topologieknoten
class topoKnoten(topologieElement, geoinformation):
    def __init__(self):
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
class topoKante(topologieElement):
    def __init__(self, knoten1, knoten2):
        self.laenge = 0
        #Radius evtl durch 1/Radius ersetzen?
        self.radius = 1
        self.steigung = 0
        self.vmax = 0

        self.knoten1 = knoten1
        self.knoten2 = knoten2

#Klasse für Bahnstrecken
class bahnstrecke(dataStack):
    def importData(self):
        try:
            path = 'Test.gpx'
            tree = ET.parse(path)
            root = tree.getroot()
            #Gehe alle Wegpunkte in .gpx durch:
            for waypoint in root[0][1]:
                kn1a = topoKnoten()
                for a,b in waypoint.attrib.items():
                    if a == "lon":
                        kn1a.lon = b
                    elif a == "lat":
                        kn1a.lat = b
                    elif a == "ele":
                        kn1a.z = b
                kn1b = copy.copy(kn1a)
                #Setze den jeweils zugehörigen ZwillingsKnoten:
                kn1a.zwillingsKnoten = kn1b
                kn1b.zwillingsKnoten = kn1a
                #Füge beide Knoten dem DataStack der Bahnstrecke hinzu:
                self.add(kn1a)
                self.add(kn1b)
        except ValueError:
            print(ValueError)
    def railwayDataStackPreparation(self, stpAuf, deltaS):
        for i in range(0, len(self._stack)):
            a = self._stack[i]
            while a[0] < self._stack[i+1, 0]:
                stpAuf.add(topoKante(a.laenge, a.radius, a.steigung, a.vmax))
                a[0].laenge += deltaS
        return stpAuf

#Klasse für Fahrwege
class fahrweg(dataStack):
    def __init__(self, start, ziel):
        try:
            x = start
            i = 0
            self.add(start)
            while True:
                x = x.getNextKnoten
                self.add(x)
                i += 1
                if x == ziel:
                    break
                if i > 10000:
                    break
        except ValueError:
            print(ValueError)
    def getVmax(self):
        vmax = 0
        for i in self._stack:
            if vmax<int(i.vmax): vmax = int(i.vmax)
        return vmax
    def getVmin(self):
        vmin = 1000
        for i in self._stack:
            if vmin>int(i.vmax): vmin = int(i.vmin)
        return vmin
    def getLength(self):
        #Warum funktioniert self._stack[0].laenge nicht?
        return int(self._stack[-1].laenge) - int(self._stack[0].laenge)
    def getResistanceForce(self, deltaS):
        i = 0
        f = 0
        for line in self._stack:
            i += line.steigung * deltaS
            #Röckl
            if line.radius < 300:
                fk = 0.5 / (line.radius - 30)
            else:
                fk = 0.65 / (line.radius - 55)
            f += fk * deltaS
        return (i + f)/self.getLength()

#Klasse für Betriebsstellen
class betriebsstelle(topologieElement):
    def __init__(self):
        self.geoinformation = geoinformation

#Klasse für Hauptsignale
class hauptsignal(topoKnoten):
    def __init__(self):
        pass

#Klasse für Fahrwegelemente
class fahrwegelement(topologieElement):
    def __init__(self):
        self._stack = set()
        self._belegung = False
        self._sperre = False
    def add(self, x):
        self._stack.append(x)
    def setBelegung(self):
        self._belegung = True
    def clearBelegung(self):
        self._belegung = False
    def getBelegung(self):
        return self._belegung
    def setSperre(self):
        self._sperre = True
    def clearSperre(self):
        self._sperre = False
    def getSperre(self):
        return self._sperre

#Klasse für Weichen
class weiche(fahrwegelement):
    def __init__(self, knSpitze, knGerade, knAbzw):
        self._knSpitze = knSpitze
        self._knGerade = knGerade
        self._knAbzw = knAbzw
        self._lage = 0
        self._verschluss = False
    def getLage(self):
        if self._lage == 0:
            return "right"
        if self._lage == 1:
            return "left"
    def umstellen(self):
        if self.getBelegung(self) and self._lage == 0:
            self._lage = 1
        if self.getBelegung(self) and self._lage == 1:
            self._lage = 0
    def setVerschluss(self):
        return False

class knot:
    def __init__(self):
        self.lon = 0
        self.lat = 0
        self.x = 0
        self.y = 0
        self.z = 0

class edge:
    def __init__(self, knot1, knot2):
        self.knot1 = knot1
        self.knot2 = knot2
        self.a = vector2d(0,0)
        self.b = vector2d(0,0)
        self.c = vector2d(0,0)
        self.d = vector2d(0,0)
        self.le = 0
        self.grade = 2+2
    def get_f(self, l):
        return vector2d(self.a.x+self.b.x*(l-self.le)+self.c.x*(l-self.le)**2+self.d.x*(l-self.le)**3,
                self.a.y+self.b.y*(l-self.le)+self.c.y*(l-self.le)**2+self.d.y*(l-self.le)**3)
    def get_f1(self, l):
        return vector2d(self.b.x+2*self.c.x*(l-self.le)+3*self.d.x*(l-self.le)**2,
                        self.b.y+2*self.c.y*(l-self.le)+3*self.d.y*(l-self.le)**2)
    def get_f2(self, l):
        return vector2d(2*self.c.x+6*self.d.x*(l-self.le),
                        2*self.c.y+6*self.d.y*(l-self.le))

class vector2d:
    #Ähnlich zu https://docs.godotengine.org/en/stable/classes/class_vector2.html
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
    def length(self):
        return math.sqrt(self.x**2+self.y**2)

class trackData():
    def __init__(self):
        self.knots = list()
        self.min_lat = 90
        self.max_lat = -90
        self.min_lon = 360
        self.max_lon = 0
        self.earth_R = 6371001
        self.x = list()
        self.y = list()
        self.edges = list()
    def test(self):
        self.path = 'Test.gpx'
        self.tree = ET.parse(self.path)
        self.root = self.tree.getroot()

        for waypoint in self.root[0][1]:
            kn = knot()
            for a,b in waypoint.attrib.items():
                if a == "lon":
                    kn.lon = float(b)
                    if self.min_lon>float(b): self.min_lon = float(b)
                    if self.max_lon<float(b): self.max_lon = float(b)
                elif a == "lat":
                    kn.lat = float(b)
                    if self.min_lat>float(b): self.min_lat = float(b)
                    if self.max_lat<float(b): self.max_lat = float(b)
                elif a == "ele":
                    kn.z = float(b) 
            self.knots.append(kn)

        for i in self.knots:
            i.x = math.sin((self.max_lon-i.lon)/180*math.pi)*math.cos(self.max_lat/180*math.pi)*self.earth_R
            i.y = math.sin((self.max_lat-i.lat)/180*math.pi)*self.earth_R
            self.x.append(i.x)
            self.y.append(i.y)

            #Bestimme den Index von i in self.knots
            i_index = self.knots.index(i)            
            if i_index > 0:
                #Lege ein neues edge-Element an
                e = edge(i, self.knots[i_index-1])                
                #Berechne den Abstand zwischen diesen knot und dem vorherigen
                e.le = self.abstand(self.knots[i_index], self.knots[i_index-1])
                #Füge das edge-Element der Liste hinzu:
                self.edges.append(e)

    def abstand(self, a, b):
        return math.sqrt((a.x-b.x)**2+(a.y-b.y)**2)

    def plot(self):
        plt.plot(self.x, self.y)
        plt.show()

    def interpolate(self):
        s = len(self.knots)
        #Koeffizientenmatrix a
        self.a = np.zeros((s,s))
        #Rechte Seite des Linearen Gleichungssystems b
        self.b = np.zeros((s,1))

        #Setze natürliche Randbedingungen
        self.a[0,0]=1
        self.a[s-1,s-1]=1

        #Befülle die Matrizen a und b
        for i in range(1, s-1):
            self.a[i, i-1] = self.edges[i-1].le/6
            self.a[i, i] = (self.edges[i-1].le+self.edges[i].le)/3
            self.a[i, i+1] = self.edges[i].le/6
            self.b[i, 0] = (self.knots[i+1].y-self.knots[i].y)/self.edges[i].le-(self.knots[i].y-self.knots[i-1].y)/self.edges[i-1].le

        #Löse das Lineare Gleichungssystem
        self.m = np.linalg.solve(self.a,self.b)
