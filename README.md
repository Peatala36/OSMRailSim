# OSMRailSim
## Zielsetzung
Ziel ist eine Software zu entwickeln, mit deren Hilfe man einfache Fahrsimulationen von Schienenfahrzeugen durchführen kann. Die Datenbasis hierfür soll die Openstreetmap (OSM) liefern. Die Fahrsimulation errechnet folgende Ergebnisse:
* Fahrzeiten für die angegebene Strecke
* Energieverbrauch

## Prinzipieller Ablauf
* Export von Rohdaten aus OSM
* Verarbeitung der Rohdaten zu einer Streckendatei
* Mithilfe der Streckenliste und aller weiteren notwendigen Daten kann eine Fahrsimulation durchgeführt werden

## Rohdaten
Aus OSM werden die Ways der gewählten Bahnstrecke geladen. Dazu wird die Overpass-Api benutzt. Die Ways bestehen einerseits aus den einzelen Wegpunkten (Nodes) und aus deren Eigenschaften (tags). Die Höhe der NN der einzelnen Nodes wird mithilfe von SRRM-Daten bestimmt. 

Der Benutzer muss zusätzlich weitere Strecken-Daten eingeben:
* Maximale Streckenneigung
* Referenz-Kilometrierung einiger Nodes

Daneben muss der Benutzer auch die Fahrzeugdaten eingeben. Diese sind:
* Masse
* Zuschlag rotierende Massen
* Laufwiderstand
* Länge
* Zugkraft-Geschwindigkeits-Kennlinie
* Wirkungsgrad

## Verarbeitung der Rohdaten
Im nächsten Schritt wird aus dem Spline die Streckendatei erzeugt, in welcher die einzelnen Abschnitte (Gerade, Bogen, etc.) und deren Eigenschaften aufgeführt sind. Dazu wird aus den Koordinaten der Nodes mithilfe einer cubischen Spline-Interpolation der Streckenverlauf modelliert.

Die Streckendatei enhält folgede Spalten:
* laufende Zeilennummer
* Name der Betriebsstelle
* Kürzel der Betriebsstelle
* Haltestellenmuster (0: keine Hst, 1: Hst mit höchster Priorität, 2....6: Hst mit geringster Priorität)
* laufende Wegkoordinate der Strecke (x=0 bis x=x_max)
* reale Kilometrierung
* Höchstgeschwindigkeit (streckenseitig zulässig)
* Bogenradius
* Streckenlängsneigung

## Fahrsimulation
Für den Zug wird die Kräftebilanz als mathematische Gleichung aufgestellt. Die Beschleunigung ergibt sich aus den Angaben zu Masse und Massenzuschlag unter Einwirkung der Summe aller Kräfte (Zugkraft, Laufwiderstand, Streckenwiderstand). Mithilfe des Geschwindigkeitsschritt-Verfahrens wird diese Differenzialgleichung  schrittweise nummerisch integriert. Dabei werden die Grenzwerte (zulässige Höchstgeschwindigkeit, etc.) beachtet.

## Benötigte Module
* OSMPythonTools https://github.com/mocnik-science/osm-python-tools/tree/master/docs
* SRTM

