import os
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
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
    def __init__(self, name, occupancy, aircraft_id):
        self.name = name
        self.occupancy = occupancy
        self.aircraft_id = aircraft_id

# Genera y asigna un rango de puertas de embarque consecutivas a un área específica.
def SetGates(area, init_gate, end_gate, prefix):
    if end_gate < init_gate:
        return -1
    area.gates = []
    for gate_num in range(init_gate, end_gate + 1):
        gate_name = f"{prefix}{gate_num}"
        new_gate = Gate(gate_name, False, "")
        area.gates.append(new_gate)
    return 0

# Carga los códigos ICAO de las aerolíneas asociadas a una terminal desde un archivo de texto.
def LoadAirlines(terminal, t_name):
    filename = f"{t_name}_Airlines.txt"
    if not os.path.exists(filename):
        print(f"Error: File {filename} not found.")
        return -1
    terminal.icao_codes = []
    try:
        with open(filename, "r") as file:
            for line in file:
                partes = line.strip().split('\t')
                if len(partes) >= 1:
                    icao_code = partes[-1].strip()
                    if icao_code:
                        terminal.icao_codes.append(icao_code)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return -1

# Lee un archivo de configuración para construir la infraestructura completa del aeropuerto.
def LoadAirportStructure(filename):
    if not os.path.exists(filename):
        print(f"Error: {filename} not found.")
        return -1

    bcn_airport = None
    current_terminal = None

    try:
        with open(filename, "r") as file:
            for line in file:
                line = line.strip()
                if line != "":
                    partes = line.split()

                if "terminals" in line:
                    bcn_airport = BarcelonaAP(partes[0])
                elif line.startswith("Terminal"):
                    t_name = partes[1]
                    current_terminal = Terminal(t_name)
                    bcn_airport.terminals.append(current_terminal)
                    LoadAirlines(current_terminal, t_name)
                elif line.startswith("Area"):
                    area_name = partes[1]
                    area_type = partes[2]
                    init_g = int(partes[4])
                    end_g = int(partes[6])
                    new_area = BoardingArea(area_name, area_type)
                    current_terminal.boarding_areas.append(new_area)
                    prefix = f"{current_terminal.name}BA{area_name}G"
                    SetGates(new_area, init_g, end_g, prefix)

        return bcn_airport
    except Exception as e:
        print(f"Error en LoadAirportStructure: {e}")
        return -1

# Recorre todo el aeropuerto para conocer el estado de ocupación actual de cada puerta.
def GateOccupancy(bcn):
    lista_de_ocupacion = []
    for terminal in bcn.terminals:
        for area in terminal.boarding_areas:
            for puerta in area.gates:
                estado = "occupied" if puerta.occupancy else "free"
                lista_de_ocupacion.append([puerta.name, estado, puerta.aircraft_id])
    return lista_de_ocupacion

# Comprueba si una aerolínea opera en una terminal específica.
def IsAirlineInTerminal(terminal, name):
    if name == "" or name is None:
        return False
    return name in terminal.icao_codes

# Busca en todo el aeropuerto a qué terminal pertenece una aerolínea.
def SearchTerminal(bcn, name):
    for terminal in bcn.terminals:
        if IsAirlineInTerminal(terminal, name):
            return terminal.name
    return ""

# Determina si un origen (ICAO) es Schengen usando los prefijos de país.
def _is_schengen_origin(origin):
    if not origin:
        return True  # Si no hay origen, default Schengen
    schengen_prefixes = [
        'LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG',
        'EH', 'LH', 'BI', 'LI', 'EV', 'EY', 'EL', 'LM', 'EN', 'EP',
        'LP', 'LZ', 'LJ', 'LE', 'ES', 'LS'
    ]
    prefix = str(origin).strip().upper()[0:2]
    return prefix in schengen_prefixes

# ─────────────────────────────────────────────────────────────────────────────
# ASSIGN GATE: Lógica corregida con filtro Terminal + Schengen
# ─────────────────────────────────────────────────────────────────────────────
# El proceso es:
#   1. Determinar la terminal de la aerolínea (T1 o T2) leyendo sus icao_codes
#   2. Determinar si el vuelo es Schengen según el origen ICAO
#   3. Buscar la primera puerta libre en la terminal y área correctas
#   4. Si no hay sitio en la área correcta, intentar cualquier área libre de la terminal
#   5. Si la terminal está llena, intentar en la otra terminal (fallback de emergencia)
def AssignGate(bcn, aircraft):
    # 1. Determinar la terminal de la aerolínea
    airline_code = getattr(aircraft, 'company', '') or ''
    airline_code = str(airline_code).strip()

    # Buscar la terminal que tiene registrada esta aerolínea
    target_terminal = None
    for terminal in bcn.terminals:
        if IsAirlineInTerminal(terminal, airline_code):
            target_terminal = terminal
            break

    # 2. Determinar si el vuelo es Schengen
    origin = getattr(aircraft, 'origin', '') or ''
    is_schengen = _is_schengen_origin(origin)
    type_needed = "Schengen" if is_schengen else "non-Schengen"

    # Helper para buscar puerta libre en una terminal con filtro de tipo
    def _try_assign_in_terminal(terminal, required_type, fallback_any=False):
        # Primer intento: área del tipo requerido
        for area in terminal.boarding_areas:
            if area.type == required_type:
                for gate in area.gates:
                    if not gate.occupancy:
                        gate.occupancy = True
                        gate.aircraft_id = aircraft.id
                        return gate.name
        # Fallback: cualquier área libre de la terminal (si se permite)
        if fallback_any:
            for area in terminal.boarding_areas:
                for gate in area.gates:
                    if not gate.occupancy:
                        gate.occupancy = True
                        gate.aircraft_id = aircraft.id
                        return gate.name
        return None

    # 3. Intentar en la terminal correcta primero
    if target_terminal:
        result = _try_assign_in_terminal(target_terminal, type_needed, fallback_any=True)
        if result:
            return result

    # 4. Fallback: intentar en cualquier terminal (emergencia)
    for terminal in bcn.terminals:
        if terminal == target_terminal:
            continue
        result = _try_assign_in_terminal(terminal, type_needed, fallback_any=True)
        if result:
            return result

    # 5. Si la aerolínea no estaba en ninguna terminal (desconocida), probar en orden normal
    if not target_terminal:
        for terminal in bcn.terminals:
            result = _try_assign_in_terminal(terminal, type_needed, fallback_any=True)
            if result:
                return result

    return -1  # Aeropuerto lleno

# Libera la puerta asignada a un ID de avión específico.
def FreeGate(bcn, aircraft_id):
    for terminal in bcn.terminals:
        for area in terminal.boarding_areas:
            for gate in area.gates:
                if gate.occupancy and gate.aircraft_id == aircraft_id:
                    gate.occupancy = False
                    gate.aircraft_id = ""
                    return 0
    return -1

# ─────────────────────────────────────────────────────────────────────────────
# ASSIGN GATES AT TIME: Corregido para usar la nueva lógica de AssignGate
# ─────────────────────────────────────────────────────────────────────────────
# Simula el estado del aeropuerto en un minuto concreto del día.
# Vacía las puertas y posiciona los aviones que se encuentran en los rangos
# horarios de la hora consultada, respetando T1/T2 y Schengen/non-Schengen.
def AssignGatesAtTime(bcn, aircrafts, time):
    h_actual, m_actual = map(int, time.split(':'))
    minutos_actual = h_actual * 60 + m_actual

    # Limpia todas las puertas
    for terminal in bcn.terminals:
        for area in terminal.boarding_areas:
            for gate in area.gates:
                gate.occupancy = False
                gate.aircraft_id = ""

    aviones_sin_puerta = 0

    for avion in aircrafts:
        # Determina el minuto de entrada (landing)
        if avion.landing_time:
            h_arr, m_arr = map(int, avion.landing_time.split(':'))
            t_entrada = h_arr * 60 + m_arr
        else:
            t_entrada = 0  # Avión de pernocta

        # Determina el minuto de salida (departure)
        if avion.departure_time:
            h_dep, m_dep = map(int, avion.departure_time.split(':'))
            t_salida = h_dep * 60 + m_dep
        else:
            t_salida = 1440  # 24:00 — vuelo que llega y no sale hoy

        # Comprueba si la hora actual está dentro del rango de estancia del avión
        if t_entrada <= minutos_actual < t_salida:
            resultado = AssignGate(bcn, avion)
            if resultado == -1:
                aviones_sin_puerta += 1

    return aviones_sin_puerta

# ─────────────────────────────────────────────────────────────────────────────
# PLOT DAY OCCUPANCY: Corregido para usar AssignGatesAtTime correcto
# ─────────────────────────────────────────────────────────────────────────────
def PlotDayOccupancy(bcn, aircrafts):
    horas_eje_x = []
    ocupacion_t1 = []
    ocupacion_t2 = []
    rechazados = []

    # Reset completo al inicio
    for terminal in bcn.terminals:
        for area in terminal.boarding_areas:
            for gate in area.gates:
                gate.occupancy = False
                gate.aircraft_id = ""

    for h in range(24):
        str_hora = f"{h:02d}:00"

        sin_sitio = AssignGatesAtTime(bcn, aircrafts, str_hora)

        c_t1 = 0
        c_t2 = 0
        for terminal in bcn.terminals:
            ocupadas = sum(1 for area in terminal.boarding_areas for gate in area.gates if gate.occupancy)
            if terminal.name == "T1":
                c_t1 = ocupadas
            else:
                c_t2 = ocupadas

        print(f"DEBUG HORA {h:02d}:00 -> T1: {c_t1}  T2: {c_t2}  Sin puerta: {sin_sitio}")

        horas_eje_x.append(h)
        ocupacion_t1.append(c_t1)
        ocupacion_t2.append(c_t2)
        rechazados.append(sin_sitio)

    # Gráfico
    plt.figure(figsize=(12, 6))
    plt.bar(horas_eje_x, ocupacion_t1, color="#78dff5", label="T1", alpha=0.85, edgecolor="#3b2d4a", linewidth=0.5)
    plt.bar(horas_eje_x, ocupacion_t2, bottom=ocupacion_t1, color="#f8a4c8", label="T2", alpha=0.85, edgecolor="#3b2d4a", linewidth=0.5)
    plt.step(horas_eje_x, rechazados, color="#ff7f91", where="mid", label="Sin Puerta", linewidth=2)
    plt.xlabel("Hora del día")
    plt.ylabel("Puertas ocupadas")
    plt.title("Ocupación diaria de puertas LEBL (T1/T2 por terminal)")
    plt.xticks(range(24), [f"{h:02d}h" for h in range(24)], rotation=45, fontsize=8)
    plt.legend()
    plt.tight_layout()

# Conversión del tiempo desde el formato hh:mm a minutos totales del día
def TimeToMinutes(time_str):
    if not time_str or time_str == '-':
        return 0
    parts = time_str.split(':')
    return int(parts[0]) * 60 + int(parts[1])

# Convierte minutos totales del día de vuelta al formato 'hh:mm'
def MinutesToTime(minutes):
    minutes = minutes % 1440
    horas = minutes // 60
    mins = minutes % 60
    return f"{horas:02d}:{mins:02d}"

# Determina de manera rápida si una aerolínea pertenece a la T1 leyendo su archivo.
def GetTerminalByAirline(airline_code):
    try:
        with open("T1_Airlines.txt", "r") as f:
            for line in f:
                parts = line.strip().split('\t')
                if parts and parts[-1].strip() == airline_code:
                    return "T1"
    except FileNotFoundError:
        print("Aviso: T1_Airlines.txt no encontrado. Asignado a T2 por defecto.")
    return "T2"

# Asigna automáticamente todos los aviones de la lista de llegadas.
def AutomaticAssignGate(bcn, aircraftlist):
    for avion in aircraftlist:
        resultado = AssignGate(bcn, avion)
        if resultado == -1:
            print(f"No hay puertas disponibles para {avion.id}")
        else:
            print(f"Asignación completada: {avion.id} -> {resultado}")

# Asigna puerta exclusivamente a los aviones destinados a pasar la noche.
def AssignNightGates(bcn, aircrafts):
    if not aircrafts:
        return -1
    for aircraft in aircrafts:
        arrival_time = getattr(aircraft, 'arrival_time', '')
        if arrival_time != '' and arrival_time is None:
            resultado = AssignGate(bcn, aircraft)
            if resultado == -1:
                print(f"Error: No se pudo asignar puerta al avión de pernocta {aircraft.id}")
    return 0

# Simula distancia en metros desde la puerta hasta el centro de la terminal.
def GetGateDistanceToHub(gate_name):
    try:
        ultimo_fragmento = gate_name.split('G')[-1]
        num_part = ''.join(filter(lambda c: c.isdigit(), ultimo_fragmento))
        gate_num = int(num_part)
    except Exception:
        gate_num = 10
    return gate_num * 50

# Asigna una puerta optimizando la comodidad del pasajero.
def OptimizeGateAllocation(bcn, aircraft):
    t_name = SearchTerminal(bcn, aircraft.company)
    if not t_name:
        return -1

    terminal_obj = None
    for t in bcn.terminals:
        if t.name == t_name:
            terminal_obj = t
            break

    if not terminal_obj:
        return -1

    origin = getattr(aircraft, 'origin', '') or ''
    is_schengen_flight = _is_schengen_origin(origin)
    type_needed = "Schengen" if is_schengen_flight else "non-Schengen"

    best_gate = None
    min_distance = float('inf')

    for area in terminal_obj.boarding_areas:
        if area.type == type_needed:
            for gate in area.gates:
                if not gate.occupancy:
                    distance = GetGateDistanceToHub(gate.name)
                    if distance < min_distance:
                        min_distance = distance
                        best_gate = gate

    if best_gate:
        best_gate.occupancy = True
        best_gate.aircraft_id = aircraft.id
        print(f"[OPTIMIZADOR] Avión {aircraft.id} asignado a {best_gate.name} (Distancia: {min_distance}m)")
        return best_gate.name
    else:
        print(f"[ALERTA] No hay puertas libres del tipo {type_needed} en {t_name}")
        return -1

# Busca una aerolínea con estructura simple (compatibilidad con check_airline_sencillo).
def check_airline_sencillo(bcn, nombre_buscado):
    if nombre_buscado == "":
        return "Error: campo vacío"
    for terminal in bcn.terminals:
        if IsAirlineInTerminal(terminal, nombre_buscado):
            return f"Está en la {terminal.name}"
    return "No se ha encontrado"

import random

# Simula situaciones meteorológicas adversas añadiendo retrasos aleatorios.
def SimulateDelaysSimple(bcn, aircrafts):
    for t in bcn.terminals:
        for area in t.boarding_areas:
            for gate in area.gates:
                gate.occupancy = False
                gate.aircraft_id = None

    conflictos = []
    print("\nSimulación de Tormenta")

    for ac in aircrafts:
        if random.choice([True, False]):
            antigua_hora = getattr(ac, 'landing_time', '00:00') or '00:00'
            ac.landing_time = antigua_hora.replace(":00", ":45").replace(":15", ":50")
            print(f" Vuelo {ac.id} retrasado. De {antigua_hora} pasa a las {ac.landing_time}")

        asignado = AssignGate(bcn, ac)
        if asignado == -1:
            mensaje = f" Conflicto: El vuelo {ac.id} no tiene puerta libre"
            conflictos.append(mensaje)

    print("Fin de la simulación")
    return conflictos



