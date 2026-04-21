from fontTools.ttLib.woff2 import woff2UnknownTagIndex
from fontTools.ufoLib import fontInfoWOFFMetadataDescriptionValidator
class Airport:
    def __init__(self, icao, latitude, longitude):
        self.icao = icao
        self.latitude = latitude
        self.longitude = longitude
        self.Schengen = False

def IsSchengenAirport(Airport):
    SchengenAirports= ['LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG', 'EH', 'LH', 'BI','LI', 'EV', 'EY', 'EL', 'LM', 'EN', 'EP', 'LP', 'LZ', 'LJ', 'LE', 'ES','LS']
    partes = Airport.icao[0:2]
    i= 0
    found= False
    while i < len(SchengenAirports) and not found:
        if SchengenAirports[i] == partes:
            found= True
        else:
            i= i+1
    if found:
        print("Es schengen")
        return  True
    else:
        print("No es schengen")
        return False

def SetSchengen(airport):
    if IsSchengenAirport(airport):
        print ("SI")
        airport.Schengen = True
    else:
        print ("No")
        airport.Schengen = False
    return airport


def PrintAirport(airport):
    print("ICAO:", airport.icao)
    print("Latitude:", airport.latitude)
    print("Longitude:", airport.longitude)



def LoadAirports(filename):
    lista = []
    archivo= open(filename,"r")
    next(archivo)
    linea = archivo.readline()
    while linea!= "":
        partes= linea.split(" ")
        icao = partes[0]
        latitude = (partes[1])
        letra = (latitude[0])
        grados= float(latitude[1:3])
        minutos= float(latitude[3:5])
        segundos= float(latitude[5:7])
        resultado = grados + (minutos/60) + (segundos/3600)
        if letra == "S":
            resultado= resultado * (-1)
        longitude = (partes[2])
        letra2= (longitude[0])
        grados2 = float(longitude[1:4])
        minutos2 = float(longitude[4:6])
        segundos2 = float(longitude[6:8])
        resultado2 = grados2 + (minutos2 / 60) + (segundos2 / 3600)
        if letra2 == "W":
            resultado2= resultado2 * (-1)
        airport = Airport (icao, resultado, resultado2)
        lista.append(airport)
        linea= archivo.readline()

    archivo.close()
    return lista



def SaveSchengenAirports(airports, filename):
    archivo = open(filename,"w")
    i=0
    while i < len(airports):
        airport= airports[i]
        if airport.Schengen == True:
            archivo.write (airport.icao + "\n")
        i = i+1

    archivo.close()

def AddAirport(airports, airport):
   encontrado = False
   i = 0
   while i < len(airports) and not encontrado:
       if airport == i:
           encontrado= True
       else:
           i= i+1
   if not encontrado:
       airports. append(airport)

def RemoveAirport(airports, Airport):
    i = 0
    found = False
    num = len(airports)


    while i < len(airports) and not found:
        if airports[i] == Airport:
            found = True
        else:
            i = i + 1

import matplotlib.pyplot as plt

def PlotAirports(airports):
    Sischengen= 0
    Noschengen= 0
    i=0
    while i < len(airports):
        if IsSchengenAirport(airports[i]):
            Sischengen = Sischengen + 1
        else:
            Noschengen = Noschengen + 1
        i= i+1
    nombres = ["Airports"]
    valores = [Sischengen, Noschengen]

    plt.bar(nombres, Sischengen, color=["pink"], label="Schengen")
    plt.bar(nombres, Noschengen, bottom=Sischengen, color=["limegreen"], label="NoSchengen")

    plt.ylabel("Count")
    plt.title("Schengen airports")
    plt.legend()
    plt.show()

import os
import platform
import subprocess

def MapAirports(airports):
    archivo = open("airports.kml", "w")

    archivo.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    archivo.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    archivo.write('<Document>\n')

    archivo.write('''
    <Style id="schengenStyle">
        <IconStyle>
            <color>ffcbc0ff</color>  
        </IconStyle>
    </Style>

    <Style id="noSchengenStyle">
        <IconStyle>
            <color>ff32cd32</color>
        </IconStyle>
    </Style>
    ''')

    for airport in airports:

        name = airport.icao
        longitude = airport.longitude
        latitude = airport.latitude

        if IsSchengenAirport(airport):
            style = "#schengenStyle"
        else:
            style = "#noSchengenStyle"

        archivo.write(f'''
        <Placemark>
            <name>{name}</name>
            <styleUrl>{style}</styleUrl>
            <Point>
                <coordinates>{longitude},{latitude}</coordinates>
            </Point>
        </Placemark>
        ''')

    archivo.write('</Document>\n')
    archivo.write('</kml>\n')

    archivo.close()

    try:
        if platform.system() == "Windows":
            os.startfile("airports.kml")
        elif platform.system() == "Darwin":
            subprocess.run(["open", "airports.kml"])
        else:
            subprocess.run(["xdg-open", "airports.kml"])
    except Exception as e:
        print(f"No se pudo abrir Google Earth: {e}")





