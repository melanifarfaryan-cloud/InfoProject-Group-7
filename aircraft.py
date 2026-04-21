class Aircraft:
   def __init__(self, id, company, origin, time):
       self.id = id
       self.company = company
       self.origin = origin
       self.time = time
from airport import LoadAirports, IsSchengenAirport
import matplotlib.pyplot as plt
import math

def LoadArrivals(filename):
    aircraftlist = []
    archivo = open(filename, 'r')
    next(archivo)
    linea = archivo.readline()
    partes = linea.split(" ")
    i= 0
    if i < len(partes) != 4:
        i=i+1
    else:
        while linea!= "":
            partes= linea.split(" ")
            id = partes[0]
            company = partes[3]
            origin = partes[1]
            time = partes[2]
            timepart = time.split(":")
            if len(timepart[0]) == 2 and len(timepart[1]) == 2:
                hora = int(timepart[0])
                minuto = int(timepart[1])
                if 0 <= hora <= 23 and 0 <= minuto <= 59:
                    aircraft = Aircraft(id,company,origin,time)
                    aircraftlist.append(aircraft)
                else:
                    print("Hora inválida")
            else:
                print("Formato de datos incorreto")
            linea = archivo.readline()
        archivo.close()
        return aircraftlist

def PlotArrivals(aircrafts):
    if not aircrafts:
        print("Error: lista vacía")
        return
    horas = [0]*24
    i = 0
    while i < len(aircrafts):
        aircraft = aircrafts[i]
        hora = int(aircraft.time[0:2])
        if 0 <= hora < 24:
            horas[hora] = horas[hora] + 1
        else:
            print("Formato de datos incorreto")
        i = i + 1

    x = list(range(24))
    plt.bar(x, horas, color='pink')
    plt.xlabel("Hour")
    plt.ylabel("Arrivals")
    plt.title("Arrivals per hour")
    plt.show()

def SaveFlights(aircrafts, aircraftsNEW):
    if not aircrafts:
        print("Error: lista vacía")
        return -1
    archivo = open(aircraftsNEW, "w")
    i = 0
    while i < len(aircrafts):
        a = aircrafts[i]
        id = a.id if a.id != "" else "-"
        company = a.company if a.company != "" else "-"
        origin = a.origin if a.origin != "" else "-"
        time = a.time if a.time != "" else 0

        linea = str(id) + " " + str(origin) + " " + str(time) + " " + str(company)

        archivo.write(linea)
        i = i + 1
    archivo.close()
    return 0

def PlotAirlines(aircrafts):
    if len(aircrafts) == 0:
        print("Error: lista vacía")
        return
    airlines = []
    counts = []
    i = 0
    while i < len(aircrafts):
        company = aircrafts[i].company
        j = 0
        found = False
        while j < len(airlines) and not found:
            if airlines[j] == company:
                counts[j] = counts[j] + 1
                found = True
            else:
                j = j + 1
        if not found:
            airlines.append(company)
            counts.append(1)
        i = i + 1

    plt.bar(airlines, counts)
    plt.xlabel("Airlines")
    plt.ylabel("Flights")
    plt.title("Flights per airline")
    plt.xticks(rotation=45, fontsize=6)
    plt.show()

def IsSchengenFlight(aircraft):
    PaisSchengen = ['LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG',
                        'EH', 'LH', 'BI', 'LI', 'EV', 'EY', 'EL', 'LM', 'EN', 'EP',
                        'LP', 'LZ', 'LJ', 'LE', 'ES', 'LS']
    prefijo = aircraft.origin[0:2]
    i = 0
    encontrado = False
    while i < len(PaisSchengen) and not encontrado:
        if PaisSchengen[i] == prefijo:
            encontrado = True
        else:
            i = i + 1
    return encontrado


def PlotFlightsType(aircrafts):
    if len(aircrafts) == 0:
        print("No hay datos para mostrar")
        return
    Sischengen = 0
    Noschengen = 0
    i = 0
    while i < len(aircrafts):
        if IsSchengenFlight(aircrafts[i]):
            Sischengen = Sischengen + 1
        else:
            Noschengen = Noschengen + 1
        i = i + 1
    nombres = ["Arrivals"]
    plt.bar(nombres, Sischengen, color="pink", label="Schengen")
    plt.bar(nombres, Noschengen, bottom=Sischengen, color="limegreen", label="Non-Schengen")
    plt.ylabel("Number of Flights")
    plt.title("Origin of Flights (Schengen vs Non-Schengen)")
    plt.legend()
    plt.show()


import os
import platform
import subprocess


def MapFlights(aircrafts):
    lista_aeropuertos = LoadAirports("Airports.txt")
    archivo = open("aicraft_trayectorias.kml", "w")

    archivo.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    archivo.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    archivo.write('<Document>\n')

    longitude_lebl = "2.0833"
    latitude_lebl = "41.2969"

    for aircraft in aircrafts:
        latitude_origen = ""
        longitude_origen = ""
        aeropuerto_encontrado = ""

        for airport in lista_aeropuertos:
            if airport.icao == aircraft.origin:
                latitude_origen = airport.latitude
                longitude_origen = airport.longitude
                aeropuerto_encontrado = airport

        if IsSchengenAirport(aeropuerto_encontrado):
            color_linea="ffcbc0ff"
        else:
            color_linea="ff32cd32"
        if latitude_origen != "" and longitude_origen != "":
            archivo.write('  <Placemark>\n')
            archivo.write(f'    <name>{aircraft.id}</name>\n')
            archivo.write('    <Style>\n')
            archivo.write('      <LineStyle>\n')
            archivo.write(f'        <color>{color_linea}</color>\n')
            archivo.write('        <width>2</width>\n')
            archivo.write('      </LineStyle>\n')
            archivo.write('    </Style>\n')
            archivo.write('    <LineString>\n')
            archivo.write('      <coordinates>\n')
            archivo.write(f'        {longitude_origen},{latitude_origen},0\n')
            archivo.write(f'        {longitude_lebl},{latitude_lebl},0\n')
            archivo.write('      </coordinates>\n')
            archivo.write('    </LineString>\n')
            archivo.write('  </Placemark>\n')
            print("Mostrando trayectoria")
        else:
            print("Origen no encontrado")

    archivo.write('</Document>\n')
    archivo.write('</kml>\n')
    archivo.close()

    try:
        if platform.system() == "Windows":
            os.startfile("aircraft_trayectorias.kml")
        elif platform.system() == "Darwin":
            subprocess.run(["open", "aircraft_trayectorias.kml"])
        else:
            subprocess.run(["xdg-open", "aircraft_trayectorias.kml"])
    except Exception as e:
        print(f"No se pudo abrir Google Earth: {e}")

def CalcDist(lat1, lon1, lat2, lon2):
    r = 6371
    pi = 3.14159
    phi1 = lat1 * (pi / 180)
    phi2 = lat2 * (pi / 180)
    lam1 = lon1 * (pi / 180)
    lam2 = lon2 * (pi / 180)
    dphi = phi2 - phi1
    dlam = lam2 - lam1
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distancia = r * c
    return distancia

def CoordsOrg(icao_buscado, lista_aeropuertos):
    lat = 0.0
    lon = 0.0
    i = 0
    encontrado = False

    while i < len(lista_aeropuertos):
        aeropuerto_actual = lista_aeropuertos[i]
        if aeropuerto_actual.icao.strip() == icao_buscado.strip():
            lat = aeropuerto_actual.latitude
            lon = aeropuerto_actual.longitude
            encontrado = True

        i = i + 1

    return lat, lon, encontrado

def LongDistanceArrivals(aircrafts, airports):
    lista_final = []
    lat_barcelona = 41.2974
    lon_barcelona = 2.0833
    i = 0
    while i < len(aircrafts):
        avion = aircrafts[i]
        codigo_origen = avion.origin
        lat_org, lon_org, exito = CoordsOrg(codigo_origen, airports)
        if exito == True:
            d = CalcDist(lat_org, lon_org, lat_barcelona, lon_barcelona)
            if d > 2000:
                lista_final.append(avion)
        i = i + 1

    return lista_final


# test section
if __name__ == "__main__":
    aircraftlist = LoadArrivals("Arrivals.txt")
    airports = LoadAirports("Airports.txt")
    SaveFlights(aircraftlist, "aircraftsNEW.txt")
    vuelos_largos = LongDistanceArrivals(aircraftlist, airports)
















