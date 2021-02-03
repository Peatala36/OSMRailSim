import xml.etree.ElementTree as ET

import infrastruktur

#########
#Klassen#
#########

#Klasse für Berechnungsergebnisse
class resultDataRow:
    #Hier werden die berechneten Zuglaufdaten gespeichert
    def __init__(self, laenge, time, v, f):
        self.laenge = laenge
        self.time = time
        self.v = v
        self.f = f

#Klasse für Datenstapel
class DataStack:
    def __init__(self):
        self._stack = set()
    def add(self, x):
        self._stack.append(x)
    def delLast(self):
        del self._stack[-1]

class TrackStack(DataStack):
    def getVmax(self):
        vmax = 0
        for i in self._stack:
            if vmax<int(i.vmax): vmax = int(i.vmax)
        return vmax
    def getVmin(self):
        vmin = 0
        for i in self._stack:
            if vmin>int(i.vmax): vmin = int(i.vmin)
        return vmin
    def getLength(self):
        #Warum funktioniert self._stack[0].laenge nicht?
        return int(self._stack[-1].laenge) - int(self._stack[0].laenge)
    def railwayResistanceForce(self, deltaS):    
        for line in self._stack:
            i += line.steigung * deltaS
            #Röckl
            if line.radius < 300:
                fk = 0.5 / (line.radius - 30)
            else:
                fk = 0.65 / (line.radius - 55)
            f += fk * deltaS
        return (i + f)/self.getLength()
    

#Klasse für Züge
class Train(DataStack):
    def __init__(self, trainID):
        self.trainID = trainID
    def getMaxSpeed(self):
        speed = 0
        for i in self._stack:
            if speed<int(i.speed): speed = int(i.speed)
        return speed
    def getWeight(self):
        weight = 0
        for i in self._stack:
            weight += i.bruttoWeight
        return weight
    def getLength(self):
        length = 0
        for line in self._stack:
            length += line.length
        return length
    def getTractiveForce(self, vakt, kraftschlussbeiwert):
        tE = 0
        for i in self._stack:
            if isinstance(i, Engine):
                tE += i.tractiveForce(vakt, kraftschlussbeiwert)
        return tE
    def getTrainResistanceForce(self, vakt, deltaV=0):
        FWZ = 0
        for i in self._stack:
            FWZ += i.resistanceForce(vakt, deltaV)
        return FWZ
    def getMassenfaktor(self):
        a = 0
        for i in self._stack:
            a += i.massenfaktor * i.bruttoWeight
        return a / self.getWeight

#Klasse für Fahrzeuge
class Vehicle:
    def __init__(self, name):
        self.name = name
        self.category = ""   
        self.numberDrivenAxles = 0
        self.length = 0
        self.speed = 0
        self.nettoWeight = 0
        self.tareWeight = 0    
        self.resistanceFaktorA = 0
        self.resistanceFaktorB = 0
        self.resistanceFaktorC = 0
        self.massenfaktor = 1
    def resistanceForce(vakt, deltaV=0):
        return (self.resistanceFaktorA
                + self.resistanceFaktorB * vakt/100
                + self.resistanceFaktorC * ((vakt + deltaV)/100)^2)
    def bruttoWeight(self):
        return self.nettoWeight + self.tareWeight

#Klasse für angetriebene Fahrzeuge
class Engine(Vehicle):
    def __init__(self, power):
        self.power = power
        self.abregelung = 0
    def tractiveForce(vakt, kraftschlussbeiwert):
        return min(self.bruttoWeight * 9.81 * kraftschlussbeiwert
                   - vakt * self.abregelung,
                   self.power * 3.6 / (vakt + 0.000001))

############
#Funktionen#
############

def readTrackData(txt, stp):
    with open(txt, 'r') as f:
        for line in f:
            data = line.split(';')
            #Höhe; Haltestellenname; Position; Geschwindigkeit; Steigung; Bogenradius
            stp.add(topoKante(data[0], data[1], data[2], data[3]))

def railwayDataStackPreparation(stpRoh, deltaS):
    stpAuf = TrackStack()
    for i in range(0, len(stpRoh._stack)):
        a = stpRoh._stack[i]
        while a[0] < stpRoh._stack[i+1, 0]:
            stpAuf.add(topoKante(a.laenge, a.radius, a.steigung, a.vmax))
            a[0].laenge += deltaS
    return stpAuf

def getBremsentfernung(stpBr, vakt, bremsWeg, deltaS):
    for x in range(0, bremsWeg+1, deltaS):
        if stpBr._stack[x].vmax < vakt:
            aBrems = (vakt^2 - stpBr._stack[i].vmax^2)/(2 * x)
            if aBrems > aKritisch: return x
    return False

def mainLoop(stp, train):
    vakt=0
    aakt=0
    t=0
    s=0
    deltaS = 1

    fahrStp = TrackStack()
    fahrStp._stack = stp._stack[0:9]

    erg = TrackStack()    
    for i in range(10, len(stp._stack)-1):
        FT = train.getTractiveForce(vakt, 0.42)
        FWZ = train.getTrainResistanceForce(vakt)
        FWS = fahrStp.railwayResistanceForce(deltaS)
        aakt = (FT - FWZ - FWS)/(train.getWeight * train.getMassenfaktor)

        vmax = fahrStp.getVmax()
        
        if True:
            #Wegschrittverfahren
            v = (vakt^2 + 2*aakt*deltaS)^0.5
            if v > vmax: v = vmax
            deltaT = 2 * deltaS / (vakt+v)
            vakt = v
            t += deltaT
            s += deltaS
            erg.add(resultDataRow(s, t, v))

        fahrStp.add(stp[i+1])
        fahrStp.delLast()


    with open('ergebnis.csv', 'w') as f:
        for line in erg._stack:
            f.write(line.laenge & ";" & line.time & ";" & line.vmax)

def inputData():
    tree = ET.parse('C:/Users/z0034zza/railml_vehicle.xml')
    root = tree.getroot()
    tr01 = Train(1)
    for vehicle in root[0][0]:
        v = Vehicle("Zug1")
        for a,b in vehicle.attrib.items():
            if a == "name":
                v.name = b
        tr01.add(v)
            
                
            
    
    #streckenrohdaten = TrackStack()
    #readTrackData(input("Geben Sie den Pfad der Streckendatei an: "), streckenrohdaten)
    #mainLoop(streckenrohdaten)
    input()

inputData()
