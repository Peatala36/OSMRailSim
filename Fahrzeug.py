#Klasse für die Simulation von Fahrzeugen

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

