###################################################
#Klassen zur Abbildung von Eisenbahn-Infrastruktur#
###################################################

import csv
import sys

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
