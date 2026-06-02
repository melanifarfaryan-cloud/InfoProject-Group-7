import os
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from tkinter import messagebox
from airport import IsSchengenAirport

class BarcelonaAP:
    def __init__(self, code):
        self.code = code
        self.terminals = []

class Terminal:
    def __init__(self, name):
        self.name = name
        self.boarding_areas = []
        self.icao_codes = []

class BoardingArea:
    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.gates = []


class Gate:
    def __init__(self, name, occupancy, aircraft_id ):
        self.name = name
        self.occupancy = occupancy
        self.aircraft_id = aircraft_id

# Genera y asigna un rango de puertas de embarque consecutivas a un área específica.
#     Parámetros:
#     - area: Objeto de tipo Área donde se guardarán las puertas.
#     - init_gate: Número de la puerta inicial (int).
#     - end_gate: Número de la puerta final (int).
#     - prefix: Texto identificador que irá antes del número de la puerta (str).
def SetGates(area, init_gate, end_gate, prefix):
    if end_gate < init_gate:
        return -1 # Error: El rango de puertas no es válido

    area.gates = [] # Inicializa la lista de puertas del área

    # Genera las puertas desde la inicial hasta la final
    for gate_num in range(init_gate, end_gate + 1):
        gate_name = f"{prefix}{gate_num}"
        new_gate = Gate(gate_name, False, "") # Crea objeto Gate (Nombre, ocupado=False, avion="")
        area.gates.append(new_gate)

    return 0 # Éxito

#Carga los códigos ICAO de las aerolíneas asociadas a una terminal desde un archivo de texto.
#   Parámetros:
#   - terminal: Objeto Terminal donde se registrarán las aerolíneas.
#   - t_name: Nombre de la terminal (ej. "T1" o "T2") que define el nombre del archivo.
def LoadAirlines(terminal, t_name):
    filename = f"{t_name}_Airlines.txt"
    if not os.path.exists(filename):
        print(f"Error: File {filename} not found.")
        return -1

    terminal.icao_codes = [] # Inicializa la lista de códigos de la terminal
    try:
        with open(filename, "r") as file:
            for line in file:
                # Limpia espacios y divide la línea por tabuladores
                partes = line.strip().split('\t')
                icao_code = partes[-1] # El código ICAO suele ser el último elemento
                terminal.icao_codes.append(icao_code)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return -1

# Lee un archivo de configuración para construir la infraestructura completa del aeropuerto (Terminales, Áreas y Puertas) y cargar sus aerolíneas.
def LoadAirportStructure(filename):
    if not os.path.exists(filename):
        print(f"Error: {filename} not found.")
        return -1 # Error: archivo no encontrado

    bcn_airport = None
    current_terminal = None

    try:
        with open(filename, "r") as file:
            for line in file:
                line = line.strip()
                if line != "": # Salta líneas vacías
                    partes = line.split()

                # Caso 1: Define el objeto principal del aeropuerto
                if "terminals" in line:

                    bcn_airport = BarcelonaAP(partes[0])

                # Caso 2: Detecta y crea una nueva Terminal
                elif line.startswith("Terminal"):
                    t_name = partes[1]
                    current_terminal = Terminal(t_name)
                    bcn_airport.terminals.append(current_terminal)
                    LoadAirlines(current_terminal, t_name) # Carga automática de aerolíneas asignadas

                # Caso 3: Detecta una nueva Área de Embarque dentro de la terminal actual
                elif line.startswith("Area"):
                    area_name = partes[1] # Ej: "A"
                    area_type = partes[2] # Ej: "Schengen"
                    init_g = int(partes[4]) # Número puerta inicial
                    end_g = int(partes[6]) # Número puerta final

                    new_area = BoardingArea(area_name, area_type)
                    current_terminal.boarding_areas.append(new_area)

                    # Construye el prefijo identificador para las puertas de esta área
                    prefix = f"{current_terminal.name}BA{area_name}G"
                    SetGates(new_area, init_g, end_g, prefix)

        return bcn_airport # Devuelve el objeto del aeropuerto construido
    except Exception as e:
        print(f"Error en LoadAirportStructure: {e}")
        return -1

# Recorre todo el aeropuerto para conocer el estado de ocupación actual de cada puerta.
# Devuelve una lista de listas con formato: [nombre, estado, avion]
def GateOccupancy(bcn):
    lista_de_ocupacion = []
    total_terminales = len(bcn.terminals)
    cont_terminal = 0

    # Bucle para recorrer terminales
    while cont_terminal < total_terminales:
        terminal_actual = bcn.terminals[cont_terminal]
        total_areas = len(terminal_actual.boarding_areas)
        cont_area = 0

        # Bucle  para recorrer áreas de embarque
        while cont_area < total_areas:
            area_actual = terminal_actual.boarding_areas[cont_area]
            total_puertas = len(area_actual.gates)
            cont_puerta = 0

            # Bucle para recorrer las puertas de cada área
            while cont_puerta < total_puertas:
                puerta_actual = area_actual.gates[cont_puerta]
                nombre = puerta_actual.name

                # Traduce el booleano de ocupación a texto legible
                if puerta_actual.occupancy == True:
                    estado = "occupied"
                else:
                    estado = "free"
                avion = puerta_actual.aircraft_id
                info_puerta = [nombre, estado, avion]
                lista_de_ocupacion.append(info_puerta)

                cont_puerta = cont_puerta + 1
            cont_area = cont_area + 1
        cont_terminal = cont_terminal + 1

    return lista_de_ocupacion

# Comprueba si una aerolínea opera en una terminal específica a partir de su código ICAO
def IsAirlineInTerminal(terminal, name):
    if name == "" or name is None:
        return False
    if name in terminal.icao_codes:
        return True

    return False


# Busca una aerolínea con una estructura de datos de una lista simple de interfaz Tkinter.
# Muestra una ventana con el resultado.
def check_airline_sencillo(bcn, nombre_buscado):
    if nombre_buscado == "":
        messagebox.showerror("Error", "Escribe algo, que está vacío")
        return
    terminal_encontrada = ""
    i = 0
    # Recorre una lista simplificada que simula el aeropuerto
    while i < len(bcn):
        terminal_actual = bcn[i] # Formato: [nombre_terminal, [lista_aerolineas]]
        aerolineas = terminal_actual[1]
        j = 0
        while j < len(aerolineas):
            if aerolineas[j] == nombre_buscado:
                terminal_encontrada = terminal_actual[0]
            j += 1
        i += 1
    # Muestra el resultado al usuario
    if terminal_encontrada != "":
        messagebox.showinfo("Resultado", "Está en la " + terminal_encontrada)
    else:
        messagebox.showwarning("Resultado", "No se ha encontrado")

# Busca en todo el aeropuerto a qué terminal pertenece una aerolínea.
def SearchTerminal(bcn, name):
    for terminal in bcn.terminals:
        if IsAirlineInTerminal(terminal, name):
            return terminal.name # Devuelve la terminal correcta
    return ""

# Asigna la primera puerta libre que encuentra en todo el aeropuerto a un avión.
# Retorna 1 si tiene éxito, o -1 si no hay espacio disponible.
def AssignGate(bcn, aircraft):
    t = 0
    # Recorre las terminales del aeropuerto
    while t < len(bcn.terminals):
        terminal = bcn.terminals[t]
        a = 0
        while a < len(terminal.boarding_areas):
            area = terminal.boarding_areas[a]
            g = 0
            while g < len(area.gates):
                puerta = area.gates[g]

                # Si la puerta está libre, se le asigna el avión de inmediato
                if puerta.occupancy == False:
                    puerta.occupancy = True
                    puerta.aircraft_id = aircraft.id
                    return 1 # Éxito
                g = g + 1
            a = a + 1
        t = t + 1
    return -1 # Error: Aeropuerto lleno

# Determina de manera rápida si una aerolínea pertenece a la T1 leyendo su archivo.
# Si no está en el archivo de la T1, asume que va a la T2.
def GetTerminalByAirline(airline_code):
    try:
        with open("T1_Airlines.txt", "r") as f:
            t1_list = f.read().splitlines()
        if airline_code in t1_list:
            return "T1"

    except FileNotFoundError:
        print("Aviso: T1_Airlines.txt no encontrado. Asignado a T2 por defecto.")

    return "T2"

# Asigna automáticamente a partir de la función AssignGate, todos los aviones que llegan
# Muestra un código de error si no hay puertas disponibles
# Parámetro exportado de LoadArrivals
# - aircraftlist: lista de aviones que llegan analizados desde Arrivals.txt
def AutomaticAssignGate (bcn, aircraftlist):
    # Recorre todos los aviones que están llegando
    for avion in aircraftlist:

        # Llama a AssignGate para assignarle una puerta
        resultado = AssignGate(bcn, avion)

        if resultado == -1:
            print(f"No hay puertas disponibles para {avion}")
        else:
            print(f"Asignación completada")

# Asigna puerta exclusivamente a los aviones destinados a pasar la noche
# Se identifican porque no tienen hora de llegada en el sistema de vuelos de día
def AssignNightGates(bcn, aircrafts):
    if not aircrafts:
        return -1 # Error

    for aircraft in aircrafts:
        # Busca dinámicamente la propiedad de hora de llegada
        arrival_time = getattr(aircraft, 'arrival_time', '') # Ajusta al nombre exacto de tu atributo

        # Si tiene hora de llegada, significa que NO es un avión de pernocta
        if arrival_time != '' and arrival_time is None:
            resultado = AssignGate(bcn, aircraft)
            if resultado == -1:
                print(f"Error: No se pudo asignar puerta al avión de pernocta {aircraft.aircraft_id} por falta de espacio.")
    return 0 # Éxito


# Libera la puerta asignada a un ID de avión específico, limpiando su estado.
def FreeGate(bcn, aircraft_id):
    """Libera la puerta asignada a un ID de avión específico."""
    for terminal in bcn.terminals:
        for area in terminal.boarding_areas:
            for gate in area.gates:
                # Si está ocupada por el avión buscado, la vacía
                if gate.occupancy and gate.aircraft_id == aircraft_id:
                    gate.occupancy = False
                    gate.aircraft_id = ""
                    return 0 # Éxito
    return -1 # El avión no fue encontrado en ninguna puerta

# Simula el estado del aeropuerto en un minuto concreto del día. Vacía las puertas y posiciona los aviones que se encuentran en los rangos horarios de la hora consultada.
# Devuelve el número de aviones que se quedaron sin puerta en ese minuto
def AssignGatesAtTime(bcn, aircrafts, time):
    # Convierte la hora actual (hh:mm) a un valor numérico total en minutos
    h_actual, m_actual = map(int, time.split(':'))
    minutos_actual = h_actual * 60 + m_actual

    # Limpia todas las puertas para calcular la ocupación real en este minuto
    for terminal in bcn.terminals:
        for area in terminal.boarding_areas:
            for gate in area.gates:
                gate.occupancy = False
                gate.aircraft_id = ""

    aviones_sin_puerta = 0

    # Evalúa qué aviones deben estar físicamente en pista/puerta
    for avion in aircrafts:
        # Determina el minuto de entrada (landing)
        if avion.landing_time:
            h_arr, m_arr = map(int, avion.landing_time.split(':'))
            t_entrada = h_arr * 60 + m_arr
        else:
            t_entrada = 0 # Avión de pernocta

        # Determina el minuto de salida (departure)
        if avion.departure_time:
            h_dep, m_dep = map(int, avion.departure_time.split(':'))
            t_salida = h_dep * 60 + m_dep
        else:
            t_salida = 1440 # 24:00 (vuelo que llega y no sale hoy)

        # Comproueba si la hora actual se encuentra dentro del rango de estancia del avión
        if t_entrada <= minutos_actual < t_salida:
            # Intentamos asignarle puerta
            resultado = AssignGate(bcn, avion)
            if resultado == -1:
                aviones_sin_puerta += 1 # Contador de aviones rechazados por falta de espacio

    return aviones_sin_puerta # Devuelve los aviones sin puerta

# Ejecuta una simulación de 24 horas para calcular la ocupación de las terminales y genera un gráfico de barras con los resultados y los vuelos rechazados.
def PlotDayOccupancy(bcn, aircrafts):
    horas_eje_x = []
    ocupacion_t1 = []
    ocupacion_t2 = []
    rechazados = []

    # Asegura que el aeropuerto empiece completamente vacío
    t_res = 0
    while t_res < len(bcn.terminals):
        term = bcn.terminals[t_res]
        a_res = 0
        while a_res < len(term.boarding_areas):
            area = term.boarding_areas[a_res]
            g_res = 0
            while g_res < len(area.gates):
                area.gates[g_res].occupancy = False
                area.gates[g_res].aircraft_id = ""
                g_res = g_res + 1
            a_res = a_res + 1
        t_res = t_res + 1

    # Simulación horaria de 0 a 23 horas
    h = 0
    while h < 24:
        # Formateo de hora para la función
        if h < 10:
            str_hora = "0" + str(h) + ":00"
        else:
            str_hora = str(h) + ":00"

        # Llama a la función AssignGates, que calcula el estado específico de ese minuto/hora
        sin_sitio = AssignGatesAtTime(bcn, aircrafts, str_hora)

        # Cuenta cuántas puertas terminaron ocupadas en cada terminal después de la asignación
        c_t1 = 0
        c_t2 = 0
        t_c = 0
        while t_c < len(bcn.terminals):
            terminal = bcn.terminals[t_c]
            ocupadas = 0
            a_c = 0
            while a_c < len(terminal.boarding_areas):
                area = terminal.boarding_areas[a_c]
                g_c = 0
                while g_c < len(area.gates):
                    if area.gates[g_c].occupancy == True:
                        ocupadas = ocupadas + 1
                    g_c = g_c + 1
                a_c = a_c + 1

            if terminal.name == "T1":
                c_t1 = ocupadas
            else:
                c_t2 = ocupadas
            t_c = t_c + 1

        # Debug por consola para ver si los números suben de 0
        print("DEBUG HORA " + str(h) + " -> T1: " + str(c_t1) + " T2: " + str(c_t2))

        horas_eje_x.append(h)
        ocupacion_t1.append(c_t1)
        ocupacion_t2.append(c_t2)
        rechazados.append(sin_sitio)
        h = h + 1

    # Gráfico
    plt.figure(figsize=(10, 6))
    # Barras base para la T1
    plt.bar(horas_eje_x, ocupacion_t1, color="blue", label="T1", alpha=0.6)
    # Barras de la T2 apiladas encima de la T1 usando el parámetro bottom
    plt.bar(horas_eje_x, ocupacion_t2, bottom=ocupacion_t1, color="green", label="T2", alpha=0.6)
    # Línea escalonada para detectar los aviones que se han quedado sin puerta
    plt.step(horas_eje_x, rechazados, color="red", where="mid", label="Sin Puerta")
    plt.legend()
    plt.show()

# Conversión del tiempo desde el formato hh:mm a a minutos totales del día
def TimeToMinutes(time_str):
    if not time_str or time_str == '-':
        return 0
    parts = time_str.split(':')
    return int(parts[0]) * 60 + int(parts[1])

# Convierte minutos totales del día de vuelta al formato 'hh:mm
def MinutesToTime(minutes):
    minutes = minutes % 1440 # Resetear si pasa de las 24h
    horas = minutes // 60
    mins = minutes % 60
    return f"{horas:02d}:{mins:02d}"


import random

# Función extra
# Simula situaciones meteorológicas adversas añadiendo retrasos aleatorios de 45/50 min al 50% de los vuelos, identificando conflictos de espacio.
def SimulateDelaysSimple(bcn, aircrafts):

    # Vacía el aeropuerto para la prueba
    for t in bcn.terminals:
        for area in t.boarding_areas:
            for gate in area.gates:
                gate.occupancy = False
                gate.aircraft_id = None

    conflictos = []

    print("\nSimulación de Tormenta")

    # Recorre los aviones uno a uno
    for ac in aircrafts:

        # Simula que el 50% de los aviones se retrasan por el clima
        if random.choice([True, False]):
            # Si llegaba a las "14:00", ahora llega a las "14:45"
            antigua_hora = ac.arrival_time
            ac.arrival_time = ac.arrival_time.replace(":00", ":45").replace(":15", ":50")
            print(f" Vuelo {ac.id} retrasado. De {antigua_hora} pasa a las {ac.arrival_time}")

        # Intenta asignarle puerta con AssignGate
        asignado = AssignGate(bcn, ac)

        if asignado != 0:  # Error: no hay puerta)
            mensaje = f" Conflicto: El vuelo {ac.id} de {ac.airline} no tiene puerta libre a las {ac.arrival_time}"
            conflictos.append(mensaje)

    print("Fin de la simulación")
    return conflictos

# Función extra: Simula la distancia en metros desde la puerta hasta el centro de la terminal (Hub/Control de pasaportes).
# Extrae el número de la puerta al final de su nombre.
def GetGateDistanceToHub(gate_name):

    try:
        # Si la puerta se llama T1BAaG12, extrae el '12'
        ultimo_fragmento = gate_name.split('G')[-1]
        num_part = ''.join(filter(lambda c: c.isdigit(), ultimo_fragmento))
        gate_num = int(num_part)
    except:
        gate_num = 10  # Valor por defecto

    # A mayor número de puerta, más lejos está del centro
    return gate_num * 50

# Asigna una puerta optimizando la comodidad del pasajero:
# Filtra por la terminal de la aerolínea, por la zona requerida y selecciona la puerta más cercana al Hub central
def OptimizeGateAllocation(bcn, aircraft):

    # Busca la terminal correcta usando tu función SearchTerminal
    t_name = SearchTerminal(bcn, aircraft.airline)
    if not t_name:
        return -1  # Error: Aerolínea no encontrada en las terminales

    # Encuentra el objeto Terminal dentro de bcn
    terminal_obj = None
    for t in bcn.terminals:
        if t.name == t_name:
            terminal_obj = t
            break

    if not terminal_obj:
        return -1

    # Determina si el vuelo es Schengen o No-Schengen
    is_schengen_flight = IsSchengenAirport(aircraft.origin)
    type_needed = "Schengen" if is_schengen_flight else "non-Schengen"

    best_gate = None
    min_distance = float('inf')  # Inicializa con un número infinito

    # Recorre las puertas buscando la óptima
    for area in terminal_obj.boarding_areas:
        if area.type == type_needed:
            for gate in area.gates:
                if not gate.occupied:  # Si la puerta está libre
                    # Calcula la distancia de esta puerta al centro
                    distance = GetGateDistanceToHub(gate.name)

                    # Si es la distancia más corta encontrada hasta ahora, la guardamos
                    if distance < min_distance:
                        min_distance = distance
                        best_gate = gate

    # Realiza la asignación si se encontró una puerta
    if best_gate:
        best_gate.occupied = True
        best_gate.aircraft_id = aircraft.id
        print(
            f"[OPTIMIZADOR] Avión {aircraft.id} asignado a {best_gate.name} (Distancia optimizada: {min_distance}m)")
        return 0  # Éxito
    else:
        print(f"[ALERTA] No hay puertas libres del tipo {type_needed} en la {t_name}")
        return -1  # No hay puertas disponibles


