import os
from tkinter import messagebox
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

#Genera puertas de embarque para cada área
def SetGates(area, init_gate, end_gate, prefix):
    if end_gate < init_gate: #si el número final es menor que el inicial, el rango es incorrecto
        return -1
    area.gates = [] #inicializa la lista de puertas del área
    for gate_num in range(init_gate, end_gate + 1): #bucle desde la primera hasta la última puerta
        gate_name = f"{prefix}{gate_num}"
        new_gate = Gate(gate_name, False, "")
        area.gates.append(new_gate)

    return 0

#Lee las aerolíneas operativas de una terminal desde un archivo y carga sus ICAO en el objecto terminal
def LoadAirlines(terminal, t_name):
    filename = f"{t_name}_Airlines.txt" #Crea el nuevo archivo
    if not os.path.exists(filename):
        print(f"Error: File {filename} not found.") #Comprueba si existe el archivo
        return -1

    terminal.icao_codes = [] #Inicializa la lista de ICAO de la terminal
    try:
        with open(filename, "r") as file:
            for line in file:
                partes = line.strip().split('\t') #Limpia espacios y separa los datos
                if len(partes) == 2:
                    airline_name = partes[0]
                    icao_code = partes[1]
                    terminal.icao_codes.append(icao_code) #Gurada el código en la terminal
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return -1

#Carga toda la estructura del aeropuerto
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
                if not line: continue #Salta líneas vacías
                partes = line.split()

                #Definición del aeropuerto principal
                if "terminals" in line:
                    bcn_airport = BarcelonaAP(partes[0])

                #Definición de una Terminal
                elif line.startswith("Terminal"):
                    t_name = partes[1]
                    current_terminal = Terminal(t_name)
                    bcn_airport.terminals.append(current_terminal)
                    LoadAirlines(current_terminal, t_name)

                #Definición del Área de embarque
                elif line.startswith("Area"):
                    area_name = partes[1]
                    area_type = partes[2]
                    init_g = int(partes[4])
                    end_g = int(partes[6])

                    new_area = BoardingArea(area_name, area_type)
                    current_terminal.boarding_areas.append(new_area)

                    #Genera el prefijo identificativo para las puertas de esa área
                    prefix = f"{current_terminal.name}BA{area_name}G"
                    SetGates(new_area, init_g, end_g, prefix)

        return bcn_airport
    except Exception as e:
        print(f"Error en LoadAirportStructure: {e}")
        return -1

#Recorre el aeropuerto para informar del estado de ocupación de todas las puertas
def GateOccupancy(bcn):
    lista_de_ocupacion = []
    total_terminales = len(bcn.terminals)
    cont_terminal = 0

    #Recorre las Terminales
    while cont_terminal < total_terminales:
        terminal_actual = bcn.terminals[cont_terminal]
        total_areas = len(terminal_actual.boarding_areas)
        cont_area = 0

        #Recorre las Áreas de cada Terminal
        while cont_area < total_areas:
            area_actual = terminal_actual.boarding_areas[cont_area]
            total_puertas = len(area_actual.gates)
            cont_puerta = 0

            #Recorre las Puertas de cada Área
            while cont_puerta < total_puertas:
                puerta_actual = area_actual.gates[cont_puerta]
                nombre = puerta_actual.name
                if puerta_actual.occupancy == True:
                    estado = "occupied"
                else:
                    estado = "free"
                avion = puerta_actual.aircraft_id

                #Junta los datos de la puerta y la añade a la lista general
                info_puerta = [nombre, estado, avion]
                lista_de_ocupacion.append(info_puerta)

                cont_puerta = cont_puerta + 1
            cont_area = cont_area + 1
        cont_terminal = cont_terminal + 1

    return lista_de_ocupacion

#Verifica si una aerolínea se encuentra en una terminal identificando su código en la terminal
def IsAirlineInTerminal(terminal, name):
    if name == "" or name is None:
        return False
    if name in terminal.icao_codes: #Busca el código en la lista de códigos
        return True

    return False

#Lee la aerolínea que introduce el usuario y busca la temrinal
def check_airline():
    global bcn
    global entry_nombre

    nombre_buscado = entry_nombre.get() #Obtiene el texto escrito por el usuario
    nombre_terminal = SearchTerminal(bcn, nombre_buscado) #Usa SearchTerminal para buscarla

    if nombre_buscado == "":
        messagebox.showerror("Error", "El nombre de la aerolínea no puede estar vacío")
    elif nombre_terminal != "":
        messagebox.showinfo("Resultado", f"La aerolínea {nombre_buscado} está en la {nombre_terminal}")
    else:
        messagebox.showwarning("Resultado", f"La aerolínea {nombre_buscado} NO se ha encontrado")

#Lee las terminales del aeropuerto e identifica en cual se encuentra la aerolínea buscada
def SearchTerminal(bcn, name):
    for terminal in bcn.terminals:
        if IsAirlineInTerminal(terminal, name): #Reutiliza IsAirlineInTerminal
            return terminal.name
    return ""

#Asigna una puerta de embarque libre a un avión teniendo en cuenta la terminal, el tipo de vuelo y el origen
def AssignGate(bcn, aircraft):
    resultado_operacion = -1

    nombre_terminal_asignada = SearchTerminal(bcn, aircraft.company) #Localiza la terminal de la aerolínea

    if nombre_terminal_asignada != "":
        t_totales = len(bcn.terminals)
        t_cont = 0
        encontrado = False

        #Bucle para encontrar el objecto terminal
        while t_cont < t_totales and encontrado == False:
            terminal_actual = bcn.terminals[t_cont]
            if terminal_actual.name == nombre_terminal_asignada:
                a_totales = len(terminal_actual.boarding_areas)
                a_cont = 0

                #Bucle para recorrer las áreas de esa terminal
                while a_cont < a_totales and encontrado == False:
                    area_actual = terminal_actual.boarding_areas[a_cont]
                    if area_actual.type == aircraft.origin:
                        p_totales = len(area_actual.gates)
                        p_cont = 0

                        #Bucle que busca una puerta vacía en el àrea correcta
                        while p_cont < p_totales and encontrado == False:
                            puerta_actual = area_actual.gates[p_cont]

                            #Comprueba si la puerta está libre y la asigna
                            if puerta_actual.occupancy == False:
                                puerta_actual.occupancy = True
                                puerta_actual.aircraft_id = aircraft.id
                                encontrado = True
                                resultado_operacion = puerta_actual.name

                            p_cont = p_cont + 1
                    a_cont = a_cont + 1
            t_cont = t_cont + 1
    return resultado_operacion

if __name__ == "__main__":
    bcn = LoadAirportStructure("Terminals.txt")

    if bcn == -1 or isinstance(bcn, int):
        print("Error")
    else:
        lista_puertas = GateOccupancy(bcn)

        print("\n--- ESTADO DE LAS PUERTAS ---")
        for puerta in lista_puertas:
            print(f"Puerta: {puerta[0]} | Estado: {puerta[1]} | Avión: {puerta[2]}")
