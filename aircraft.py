from airport import LoadAirports, IsSchengenAirport
import matplotlib.pyplot as plt
import math
import os
import platform
import subprocess

#Vuelo que llega al aeropuerto
class Aircraft:
   def __init__(self, id, company, origin, landing_time, destination, departure_time):
       self.id = id
       self.company = company
       self.origin = origin
       self.landing_time = landing_time
       self.destination = destination
       self.departure_time = departure_time

#Carga los aviones desde un archivo y comprueba el formato horario
def LoadArrivals(filename):
    aircraftlist = [] # Inicializa una lista vacía de aviones
    archivo = open(filename, 'r')
    next(archivo)
    linea = archivo.readline()

    partes = linea.split(" ")
    i= 0
    if i < len(partes) != 4:
        i = i+1
    else:
        #Bucle de lectura
        while linea!= "":
            partes= linea.split(" ")
            id = partes[0]
            company = partes[3]
            origin = partes[1]
            landing_time = partes[2]

            #Valida el formato de tiempo
            timepart = landing_time.split(":")
            if len(timepart[0]) == 2 and len(timepart[1]) == 2:
                hora = int(timepart[0])
                minuto = int(timepart[1])
                #Comprueba los rangos reales
                if 0 <= hora <= 23 and 0 <= minuto <= 59:
                    aircraft = Aircraft(id,company,origin,landing_time, None, None)
                    aircraftlist.append(aircraft)
                else:
                    print("Hora inválida")
            else:
                print("Formato de datos incorreto")

            linea = archivo.readline()

        archivo.close()
        return aircraftlist # Devuelve la lista de aviones

#Muestra la cantidad de aviones por su hora de llegada en un plot
def PlotArrivals(aircrafts):
    if not aircrafts:
        print("Error: lista vacía")
        return

    horas = [0]*24
    i = 0
    while i < len(aircrafts):
        aircraft = aircrafts[i]
        hora = int(aircraft.landing_time[0:2]) #Se fija en la hora

        if 0 <= hora < 24:
            horas[hora] = horas[hora] + 1 #Incrementa el contador de esa hora
        else:
            print("Formato de datos incorreto")
        i = i + 1

    x = list(range(24))
    plt.bar(x, horas, color='pink')
    plt.xlabel("Hour")
    plt.ylabel("Arrivals")
    plt.title("Arrivals per hour")


#Exporta la lista de aeronaves a un archivo de texto
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
        landing_time = a.landing_time if a.landing_time != "" else 0

        linea = str(id) + " " + str(origin) + " " + str(landing_time) + " " + str(company)
        archivo.write(linea)
        i = i + 1

    archivo.close()
    return 0

#Contabiliza los vuelos de cada aerolínea en un plot
def PlotAirlines(aircrafts):
    if len(aircrafts) == 0:
        print("Error: lista vacía")
        return

    airlines = []
    counts = []
    i = 0

    #Busca los vuelos
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
            airlines.append(company) #Si es nueva la registra
            counts.append(1)
        i = i + 1

    # Gráfico
    plt.bar(airlines, counts, color="plum")
    plt.xlabel("Airlines")
    plt.ylabel("Flights")
    plt.title("Flights per airline")
    plt.xticks(rotation=45, fontsize=6)

#Determina por el ICAO si el vuelo proviene de un país Schengen
def IsSchengenFlight(aircraft):
    PaisSchengen = ['LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG',
                        'EH', 'LH', 'BI', 'LI', 'EV', 'EY', 'EL', 'LM', 'EN', 'EP',
                        'LP', 'LZ', 'LJ', 'LE', 'ES', 'LS']
    prefijo = aircraft.origin[0:2] # Se fija en las dos primeras letras del ICAO
    i = 0
    encontrado = False

    # Búsqueda del prefijo
    while i < len(PaisSchengen) and not encontrado:
        if PaisSchengen[i] == prefijo:
            encontrado = True
        else:
            i = i + 1
    return encontrado

#Genera un plot según el tipo: Schengen o no Schengen
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

    # Gráfico
    nombres = ["Arrivals"]
    plt.bar(nombres, Sischengen, color="pink", label="Schengen")
    plt.bar(nombres, Noschengen, bottom=Sischengen, color="limegreen", label="Non-Schengen")
    plt.ylabel("Number of Flights")
    plt.title("Origin of Flights (Schengen vs Non-Schengen)")
    plt.legend()


#Genera un archivo kml que dibuja las trayectorias uniendo aeropuertos con LEBL
def MapFlights(aircrafts):
    lista_aeropuertos = LoadAirports("Airports.txt") #Carga los datos con LoadAirports
    archivo = open("aicraft_trayectorias.kml", "w")

    archivo.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    archivo.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    archivo.write('<Document>\n')

    #Coordenadas del destino LEBL
    longitude_lebl = "2.0833"
    latitude_lebl = "41.2969"

    for aircraft in aircrafts:
        latitude_origen = ""
        longitude_origen = ""
        aeropuerto_encontrado = ""

        # Busca las coordenadas del ICAO de origen
        for airport in lista_aeropuertos:
            if airport.icao == aircraft.origin:
                latitude_origen = airport.latitude
                longitude_origen = airport.longitude
                aeropuerto_encontrado = airport

        #Asignación de color
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

    #Abre el KML según el sistema operativo
    try:
        if platform.system() == "Windows":
            os.startfile("aircraft_trayectorias.kml")
        elif platform.system() == "Darwin":
            subprocess.run(["open", "aircraft_trayectorias.kml"])
        else:
            subprocess.run(["xdg-open", "aircraft_trayectorias.kml"])
    except Exception as e:
        print(f"No se pudo abrir Google Earth: {e}")

#Calcula la distancia (en curvatura terrestre) entre los puntos usando Haversine
def CalcDist(lat1, lon1, lat2, lon2):
    r = 6371  # Radio de la Tierra en km
    pi = 3.14159

    # Conversión a radianes
    phi1, phi2 = lat1 * (pi / 180), lat2 * (pi / 180)
    lam1, lam2 = lon1 * (pi / 180), lon2 * (pi / 180)

    dphi = phi2 - phi1
    dlam = lam2 - lam1

    # Fórmula de Haversine
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2

    # Asegura que 'a' no sea negativo por errores de precisión y no pase de 1
    a = max(0, min(1, a))

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c

# Extrae la longitud y la latitud de un ICAO
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

# Extrae de la lista de vuelos globales, aquellos cuya trayectoria hasta LEBL supera los 2000km y crea una nueva lista con ellos
def LongDistanceArrivals(aircrafts, airports):
    lista_final = []

    # Coordenadas de Barcelona convertidas directamente a radianes
    lat_barcelona = 41.2974
    lon_barcelona = 2.0833

    i = 0
    while i < len(aircrafts):
        avion = aircrafts[i]
        codigo_origen = avion.origin

        if codigo_origen != None:
            lat_org, lon_org, exito = CoordsOrg(codigo_origen, airports)

            if exito == True:
                d = CalcDist(lat_org, lon_org, lat_barcelona, lon_barcelona)
                if d > 2000:
                    lista_final.append(avion)
        i = i + 1

    return lista_final



# Lee el archivo departures y devuelve una lista de objetos Aircraft con información sobre su salida
def LoadDepartures(filename):
    departures_list = []
    try:
        archivo = open(filename, 'r')

        next(archivo)
        for linea in archivo:
            partes = linea.strip().split()
            if len(partes) == 4:
                id_aircraft = partes[0]
                destination = partes[1]
                departure_time = partes[2]
                company = partes[3]
                if len(departure_time) == 5 and ":" in departure_time:
                    try:
                        hora = int(departure_time[0:2])
                        minuto = int(departure_time[3:5])
                        if 0 <= hora <= 23 and 0 <= minuto <= 59:
                            nuevo_avion = Aircraft(
                                id=id_aircraft,
                                company=company,
                                origin=None,
                                landing_time=None,
                                destination=destination,
                                departure_time=departure_time
                            )
                            departures_list.append(nuevo_avion)
                        else:
                            print(f"Hora fuera de rango: {departure_time}")
                    except ValueError:
                        print(f"Error numérico en hora: {departure_time}")
                else:
                    print(f"Formato de hora incorrecto: {departure_time}")
            else:
                if len(linea.strip()) > 0:
                    print(f"Línea con columnas insuficientes: {linea.strip()}")

        archivo.close()
        return departures_list

    except FileNotFoundError:
        print(f"Error: El archivo {filename} no existe.")
        return
    except Exception as e:
        print(f"Error inesperado: {e}")
        return []

# Combina la lista de llegadas con la de salidas, si el ID y los tiempos son correctos se fusiona en una sola
def MergeMovements(arrivals, departures):
    # Si ambas listas están vacías, no hay nada que procesar
    if not arrivals and not departures:
        print("Aviso: No hay datos para fusionar.")
        return []

    merged_list = [] # Lista final con los vuelos fusionados e individuales
    ids_salidas_utilizadas = [] # Registra los IDs de salidas

    # Recorre todos los aviones que llegan para intentar emparejarlos
    for avion_arrival in arrivals:
        salida_encontrada = None

        # Busca en la lista de salidas si existe el mismo avión
        for avion_departure in departures:
            # Tiene en cuenta: Mismo ID, que la salida no haya sido usada ya, y que la llegada sea antes que la salida
            if avion_arrival.id == avion_departure.id and avion_departure not in ids_salidas_utilizadas:
                if avion_arrival.landing_time < avion_departure.departure_time:
                    salida_encontrada = avion_departure
                    break

        # Si encuentra su salida correspondiente, crea un objeto fusionado con todos los datos
        if salida_encontrada:
            nuevo_avion = Aircraft(
                id=avion_arrival.id,
                company=avion_arrival.company,
                origin=avion_arrival.origin,
                landing_time=avion_arrival.landing_time, # Datos de la llegada
                destination=salida_encontrada.destination,
                departure_time=salida_encontrada.departure_time # Datos de la salida
            )
            merged_list.append(nuevo_avion)
            ids_salidas_utilizadas.append(salida_encontrada) # Marca este ID de salida como utilizado
        else:
            merged_list.append(avion_arrival)

    # Identificar aviones que solo salen (vuelos que ya pasaron la noche en el aeropuerto)
    for avion_dep in departures:
        # Si el ID de la salida no se usó en la fusión anterior, es un vuelo independiente de salida
        if avion_dep not in ids_salidas_utilizadas:
            merged_list.append(avion_dep)

    return merged_list # Devuelve la lista completa de movimientos del día organizada

# Identifica los aviones que han pasado la noche en el aeropuerto (no tienen llegada pero sí salida)
def NightAircraft(aircrafts):
    # Valida que la lista está vacía
    if len(aircrafts) == 0:
        print("Error: La lista de aviones está vacía.")
        return [], -1

    night_list = [] # Inicializa una lista vacía

    #  Recorre todos los aviones de la lista
    for avion in aircrafts:
        # Si no tiene hora de llegada pero sí de salida, lo añade a la lista
        if avion.landing_time == None and avion.departure_time != None:
            night_list.append(avion)

    return night_list, 0

# Función extra
# Genera el archivo KML dinámico contra fallos de atributos.
def MapFlightsDynamic(aircrafts, airports_list, filename="flights_dynamic.kml"):

    # 1. Mapeo de aeropuertos
    ap_dict = {}
    for ap in airports_list:
        ap_dict[ap.icao] = (ap.latitude, ap.longitude)

    if "LEBL" in ap_dict:
        bcn_lat, bcn_lon = ap_dict["LEBL"]
    else:
        bcn_lat, bcn_lon = 41.2969, 2.0833

    kml_content = []
    kml_content.append('<?xml version="1.0" encoding="UTF-8"?>')
    kml_content.append('<kml xmlns="http://www.opengis.net/kml/2.2">')
    kml_content.append('<Document>')
    kml_content.append('  <name>Tráfico Dinámico Barcelona LEBL</name>')
    kml_content.append(
        '  <Style id="schengen_line"><LineStyle><color>ff32cd32</color><width>3</width></LineStyle></Style>')
    kml_content.append(
        '  <Style id="non_schengen_line"><LineStyle><color>ffc0cbff</color><width>3</width></LineStyle></Style>')

    # Contador manual para inventar horas
    fallback_hour = 6

    for ac in aircrafts:
        if ac.origin not in ap_dict:
            continue

        orig_lat, orig_lon = ap_dict[ac.origin]

        # Color según Schengen
        is_schengen = IsSchengenAirport(ac.origin)
        style_url = "#schengen_line" if is_schengen else "#non_schengen_line"

        # Intenta leer la salida
        hora_final = "00:00"
        if hasattr(ac, 'departure_time'):
            hora_final = ac.departure_time
        elif hasattr(ac, 'time'):
            hora_final = ac.time
        elif hasattr(ac, 'arrival_time'):
            hora_final = ac.arrival_time

        # Si sigue vacío , genera horas ficticias distribuidas para que veas el mapa lleno de golpe
        if not hora_final or hora_final == '-' or ':' not in str(hora_final):
            hora_final = f"{fallback_hour:02d}:00"
            fallback_hour = (fallback_hour + 1) if fallback_hour < 22 else 6

        time_dep = f"2026-05-30T{str(hora_final).strip()}:00Z"
        time_fin_dia = "2026-05-30T23:59:59Z"

        # 4. Escribir los datos del vuelo sin variables peligrosas
        kml_content.append('  <Placemark>')
        kml_content.append(f'    <name>{ac.id}</name>')
        kml_content.append(f'    <description>Origen: {ac.origin} -> LEBL</description>')
        kml_content.append(f'    <styleUrl>{style_url}</styleUrl>')

        kml_content.append('    <TimeSpan>')
        kml_content.append(f'      <begin>{time_dep}</begin>')
        kml_content.append(f'      <end>{time_fin_dia}</end>')
        kml_content.append('    </TimeSpan>')

        kml_content.append('    <LineString>')
        kml_content.append('      <altitudeMode>relativeToGround</altitudeMode>')
        kml_content.append('      <coordinates>')
        kml_content.append(f'        {orig_lon},{orig_lat},50000')
        kml_content.append(f'        {bcn_lon},{bcn_lat},0')
        kml_content.append('      </coordinates>')
        kml_content.append('    </LineString>')
        kml_content.append('  </Placemark>')

    kml_content.append('</Document>')
    kml_content.append('</kml>')

    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write("\n".join(kml_content))
        print(f" Creado con éxito sin: '{filename}'")
        return 0
    except Exception as e:
        print(f" Error al guardar: {e}")
        return -1

# test section
if __name__ == "__main__":
    aircraftlist = LoadArrivals("Arrivals.txt")
    airports = LoadAirports("Airports.txt")
    SaveFlights(aircraftlist, "aircraftsNEW.txt")
    vuelos_largos = LongDistanceArrivals(aircraftlist, airports)
    mis_aviones = LoadDepartures("Departures.txt")
    movimientos = MergeMovements(aircraftlist, mis_aviones)
    aviones_noche, error_noche = NightAircraft(movimientos)
    print("=== TESTING DYNAMIC KML GENERATION ===")

    # 1. Datos simulados de Aeropuertos (Versión 1)
    class MockAirport:
        def __init__(self, code, lat, lon):
            self.code = code
            self.lat = lat
            self.lon = lon

    # 2. Datos simulados de Aviones (Versión 4)
    class MockAircraft:
        def __init__(self, id, airline, origin, arrival_time, departure_time="-"):
            self.id = id
            self.airline = airline
            self.origin = origin
            self.arrival_time = arrival_time
            self.departure_time = departure_time

    # Función rápida simulada para el test
    def IsSchengenAirport(code):
        return code.startswith("LE") or code.startswith("LF")
    # 1. Carga los aeropuertos
    mis_aeropuertos = LoadAirports("Airports.txt")

    # 2. Carga los aviones usando LoadArrivals
    mis_aviones = LoadArrivals("Arrivals.txt")

    # 3. Forzamos un print para comprobar en la consola si ha leído aviones de verdad
    print(f"️ Número de aviones cargados con éxito para el mapa: {len(mis_aviones)}")

    # 4. Ejecuta la función corregida
    MapFlightsDynamic(mis_aviones, mis_aeropuertos, "todos_los_vuelos.kml")









