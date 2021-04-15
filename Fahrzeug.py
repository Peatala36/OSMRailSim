#Klasse für die Simulation von Fahrzeugen

import json

#########
#Klassen#
#########
    
class Trains:
    def __init__(self):
        self.dictOfTrains = dict()
    def __iter__(self):
        return iter(self.dictOfTrains.values())
    def readVehicleDataFromFile(self, path):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except:
            print("Datei konnte nicht geladen werden")
            return

        try:
            for i in data["trains"]:
                t = Train(i['trainID'])
                for j in i['vehicles']:
                    v = Vehicle(j['name'])
                    for a in j:
                        if hasattr(v, a):
                            setattr(v, a, j[a])
                    t.vehicles.append(v)
                self.dictOfTrains[i['trainID']] = t
                    
        except:
            print("Fehler beim lesen der Datei")


#Klasse für einen Zug
class Train:
    def __init__(self, trainID):
        self.trainID = trainID
        self.vehicles = list()
    def __iter__(self):
        return iter(self.vehicles)
    def getMaxSpeed(self):
        speed = 0
        for i in self.vehicles:
            if speed<int(i.speed): speed = int(i.speed)
        return speed
    def getWeight(self):
        weight = 0
        for i in self.vehicles:
            weight += i.bruttoWeight()
        return weight
    def getLength(self):
        length = 0
        for line in self.vehicles:
            length += line.length
        return length
    def getTractiveForce(self, vakt, kraftschlussbeiwert):
        tE = 0
        for i in self.vehicles:
            tE += i.tractiveForce(vakt, kraftschlussbeiwert)
        return tE
    def getTrainResistanceForce(self, vakt, deltaV=0):
        FWZ = 0
        for i in self.vehicles:
            FWZ += i.resistanceForce(vakt, deltaV)
        return FWZ
    def getMassenfaktor(self):
        a = 0
        for i in self.vehicles:
            a += i.massenfaktor * i.bruttoWeight()
        return a / self.getWeight()

#Klasse für Fahrzeuge
class Vehicle:
    def __init__(self, name):
        self.name = name
        self.typ = ""   
        self.numberDrivenAxles = 0
        self.length = 0
        self.speed = 0
        self.nettoWeight = 0
        self.tareWeight = 0    
        self.resistanceFaktorA = 0
        self.resistanceFaktorB = 0
        self.resistanceFaktorC = 0
        self.massenfaktor = 1

        self.power = 0
        self.abregelung = 0
        self.max_tractiveForce = 0
    def resistanceForce(self, vakt, deltaV=0):
        return (self.resistanceFaktorA
                + self.resistanceFaktorB * vakt/100
                + self.resistanceFaktorC * ((vakt + deltaV)/100)**2)
    def bruttoWeight(self):
        return self.nettoWeight + self.tareWeight
    def tractiveForce(self, vakt, kraftschlussbeiwert):
        if vakt > 0:
            return min(self.bruttoWeight() * 9.81 * kraftschlussbeiwert
                       - vakt * self.abregelung,
                       self.power * 3.6 / vakt,
                       self.max_tractiveForce)
        elif vakt == 0:
            return self.max_tractiveForce
        else:
            return 0
