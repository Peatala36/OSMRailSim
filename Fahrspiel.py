# Simulator

import Fahrzeug
import infrastruktur
import math

f=infrastruktur.Fahrweg()
f.readDataFromFile("Streckendatei.csv")

t=Fahrzeug.Trains()
t.readVehicleDataFromFile("TrainsData.json")




def wegschrittverfahren(Fahrweg, Train, deltaS):
    x_zugspitze = 0

    kraftschlussbeiwert = 0.1

    v_i = 0
    train_masse = Train.getWeight()

    geschwindigkeitsprofil = list()
    
    while x_zugspitze < Fahrweg.getLength():
        # Gesamtzugkraft des Zuges berechnen:
        F_Z = Train.getTractiveForce(v_i, kraftschlussbeiwert)
        
        # Fahrzeugwiderstanskraft:
        F_WF = Train.getTrainResistanceForce(v_i, 0)
        
        # Streckenwiderstandskraft:
        x_veh = x_zugspitze
        F_WS = 0
        for veh in Train:
            F_WS += Fahrweg.getSpecificLineResistanceForce(x_veh)
            x_veh += veh.length

        # Aus der Summe der Kräfte die aktuelle Beschleunigung berechnen:
        a_akt = (F_Z - (F_WF + F_WS)) / train_masse

        #print("F_Z: ", F_Z, ", F_WF: ", F_WF, ", F_WS: ", F_WS, ", a_akt: ", a_akt)

        # Mittlere Geschwindigkeit berechnen:
        v_i1 = math.sqrt(v_i**2 + 2*a_akt*deltaS)
        v_i = v_i1
        v_m = (v_i + v_i1)/2

        #print("v_m: ", v_m)
        geschwindigkeitsprofil.append(v_m)

        # Zeitschritt berechnen:
        delta_t = deltaS / v_m

        
        
        x_zugspitze += deltaS

    return geschwindigkeitsprofil

    
g = wegschrittverfahren(f, t.dictOfTrains[1], 5)
