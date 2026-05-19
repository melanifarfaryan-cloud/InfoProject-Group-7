import tkinter as tk
from tkinter import messagebox
import matplotlib
import os

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from airport import Airport, LoadAirports, PlotAirports, MapAirports, AddAirport, RemoveAirport
from aircraft import Aircraft, LoadArrivals, PlotArrivals, SaveFlights, PlotAirlines, PlotFlightsType, MapFlights, \
    LongDistanceArrivals
from LEBL import BarcelonaAP, Terminal, BoardingArea, Gate, LoadAirportStructure, GateOccupancy, AssignGate, \
    SearchTerminal

arrivals = []
airports = LoadAirports(filename="Airports.txt")
bcn = None

root = tk.Tk()
root.title("Airport Management")
root.state('zoomed')

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=0)
root.rowconfigure(2, weight=0)

frame_display = tk.Frame(root, bg="white")
frame_display.grid(row=0, column=0, sticky="nsew")

try:
    foto = tk.PhotoImage(file="avion.png")
except:
    foto = None
    print("Error: No se encontró avion.png")


def mostrar_imagen_original():
    for widget in frame_display.winfo_children():
        widget.destroy()
    if foto:
        label_foto = tk.Label(frame_display, image=foto, bg="white")
        label_foto.pack(expand=True, fill="both")
    else:
        tk.Label(frame_display, text="Imagen no encontrada", bg="white").pack(expand=True)




def mostrar_lista_vuelos(vuelos_filtrados):
    for widget in frame_display.winfo_children(): widget.destroy()
    if not vuelos_filtrados:
        tk.Label(frame_display, text="No hay vuelos de larga distancia (>2000km)", fg="red", bg="white",
                 font=("Arial", 12, "bold")).pack(pady=50)
        tk.Button(frame_display, text="Volver", command=mostrar_imagen_original).pack()
        return
    tk.Label(frame_display, text="VUELOS DE LARGA DISTANCIA (>2000 km)", font=("Arial", 14, "bold"), bg="white",
             pady=10).pack()
    list_container = tk.Frame(frame_display, bg="white")
    list_container.pack(expand=True, fill="both", padx=50, pady=20)
    scrollbar = tk.Scrollbar(list_container)
    scrollbar.pack(side="right", fill="y")
    lista_visual = tk.Listbox(list_container, font=("Courier New", 11), yscrollcommand=scrollbar.set, bd=2,
                              relief="groove")
    header = f"{'ID':<10} | {'COMPAÑÍA':<20} | {'ORIGEN':<10} | {'HORA':<8}"
    lista_visual.insert("end", header);
    lista_visual.insert("end", "-" * 60)
    for v in vuelos_filtrados:
        linea = f"{v.id:<10} | {v.company:<20} | {v.origin:<10} | {v.time:<8}"
        lista_visual.insert("end", linea)
    lista_visual.pack(side="left", expand=True, fill="both")
    scrollbar.config(command=lista_visual.yview)
    tk.Button(frame_display, text="Cerrar lista", command=mostrar_imagen_original, bg="#f8d7da").pack(pady=10)


def insertar_grafico(funcion_plot, datos, filtro=None):
    if not datos:
        messagebox.showwarning("Atención", "No hay datos cargados para graficar.")
        return
    for widget in frame_display.winfo_children(): widget.destroy()
    plt.close('all')
    frame_buscador = tk.Frame(frame_display, bg="white")
    frame_buscador.pack(side="top", anchor="ne", padx=20, pady=10)
    tk.Label(frame_buscador, text="Buscar:", bg="white", font=("Arial", 10, "bold")).pack(side="left")
    entry_filtro = tk.Entry(frame_buscador, width=15, font=("Arial", 10), bd=2)
    entry_filtro.pack(side="left", padx=5)
    if filtro: entry_filtro.insert(0, filtro)

    def ejecutar_filtro():
        valor = entry_filtro.get().strip().upper()
        insertar_grafico(funcion_plot, datos, filtro=valor if valor != "" else None)

    tk.Button(frame_buscador, text="Filtrar", command=ejecutar_filtro, bg="#e2e3e5").pack(side="left")
    entry_filtro.bind('<Return>', lambda e: ejecutar_filtro())
    try:
        datos_a_dibujar = datos
        if filtro:
            termino_busqueda = filtro.strip().upper()
            if funcion_plot == PlotAirlines:
                datos_a_dibujar = [d for d in datos if d.company.strip().upper() == termino_busqueda]
            elif funcion_plot == PlotAirports:
                datos_a_dibujar = [d for d in datos if d.icao.strip().upper() == termino_busqueda]
        if not datos_a_dibujar:
            tk.Label(frame_display, text=f"No se encontraron: '{filtro}'", fg="red", bg="white",
                     font=("Arial", 12, "bold")).pack(pady=50)
            tk.Button(frame_display, text="Mostrar todos", command=lambda: insertar_grafico(funcion_plot, datos)).pack()
            return
        funcion_plot(datos_a_dibujar)
        fig = plt.gcf();
        fig.set_tight_layout(True)
        canvas = FigureCanvasTkAgg(fig, master=frame_display)
        canvas.draw();
        canvas.get_tk_widget().pack(expand=True, fill="both")
    except Exception as e:
        messagebox.showerror("Error", f"Error al graficar: {e}");
        mostrar_imagen_original()


def mostrar_form_add():
    for widget in frame_display.winfo_children(): widget.destroy()
    form = tk.Frame(frame_display, bg="#f8f9fa", bd=1, relief="solid", padx=30, pady=30)
    form.place(relx=0.5, rely=0.5, anchor="center")
    tk.Label(form, text="NUEVO AEROPUERTO", font=("Arial", 12, "bold"), bg="#f8f9fa").grid(row=0, columnspan=2, pady=10)
    tk.Label(form, text="ICAO:", bg="#f8f9fa").grid(row=1, column=0, sticky="e")
    e_icao = tk.Entry(form);
    e_icao.grid(row=1, column=1, pady=5, padx=5)
    tk.Label(form, text="Latitud:", bg="#f8f9fa").grid(row=2, column=0, sticky="e")
    e_lat = tk.Entry(form);
    e_lat.grid(row=2, column=1, pady=5, padx=5)
    tk.Label(form, text="Longitud:", bg="#f8f9fa").grid(row=3, column=0, sticky="e")
    e_lon = tk.Entry(form);
    e_lon.grid(row=3, column=1, pady=5, padx=5)

    def guardar():
        try:
            cod = e_icao.get().upper()
            if AddAirport(airports, Airport(cod, float(e_lat.get()), float(e_lon.get()))):
                label_estado.config(text=f"Añadido {cod}", fg="green");
                mostrar_imagen_original()
            else:
                label_estado.config(text="Error: Ya existe", fg="red")
        except:
            label_estado.config(text="Error en datos", fg="red")

    tk.Button(form, text="Aceptar", command=guardar, bg="#d1e7dd", width=10).grid(row=4, column=0, pady=15)
    tk.Button(form, text="Cancelar", command=mostrar_imagen_original, bg="#f8d7da", width=10).grid(row=4, column=1,
                                                                                                   pady=15)


def mostrar_form_remove():
    for widget in frame_display.winfo_children(): widget.destroy()
    form = tk.Frame(frame_display, bg="#f8f9fa", bd=1, relief="solid", padx=30, pady=30)
    form.place(relx=0.5, rely=0.5, anchor="center")
    tk.Label(form, text="BORRAR ICAO", font=("Arial", 12, "bold"), bg="#f8f9fa").pack()
    e = tk.Entry(form, font=("Arial", 12));
    e.pack(pady=10)

    def borrar():
        cod = e.get().upper()
        for a in airports:
            if a.icao == cod:
                RemoveAirport(airports, a);
                label_estado.config(text=f"Borrado {cod}", fg="red")
                mostrar_imagen_original();
                return
        label_estado.config(text="No encontrado", fg="orange")

    tk.Button(form, text="BORRAR", command=borrar, bg="#f8d7da").pack(side="left", padx=5)
    tk.Button(form, text="VOLVER", command=mostrar_imagen_original).pack(side="left", padx=5)


def generar_esquema_visual(datos):
    plt.close('all')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 8))
    fig.patch.set_facecolor('#ffffff')
    estados = {item[0]: item[1].lower() for item in datos}

    def dibujar(ax, titulo, conf):
        ax.set_title(titulo, fontweight='bold')
        ax.plot([10, 90], [50, 50], color='black', linewidth=5)  # Pasillo
        x_p = [20, 35, 50, 65, 80, 95]
        for i, (area, info) in enumerate(conf.items()):
            x = x_p[i]
            ax.plot([x, x], [30, 70], color='black', linewidth=3)  # Brazo
            ax.text(x, 75, area, ha='center', fontsize=7)
            for p in range(1, info['count'] + 1):
                color = 'red' if estados.get(f"{info['prefix']}{p}") == 'occupied' else 'green'
                y = 32 + (p * 3) if p <= 12 else 68
                ax.plot([x, x + (2 if p % 2 == 0 else -2)], [y, y], color=color, linewidth=2)
        ax.set_xlim(0, 110);
        ax.set_ylim(0, 100);
        ax.axis('off')

    dibujar(ax1, "T1", {"A": {'prefix': 'T1BAAG', 'count': 11}, "B": {'prefix': 'T1BABG', 'count': 57},
                        "C": {'prefix': 'T1BACG', 'count': 11}})
    dibujar(ax2, "T2", {"M": {'prefix': 'T2BAMG', 'count': 8}, "R": {'prefix': 'T2BARG', 'count': 11},
                        "S": {'prefix': 'T2BASG', 'count': 11}})
    plt.tight_layout()
    return fig



def mostrar_lista_puertas(datos):
    for widget in frame_display.winfo_children(): widget.destroy()
    if bcn is None: messagebox.showwarning("Atención", "Carga LEBL primero"); return

    tk.Label(frame_display, text="ESTADO DE PUERTAS LEBL", font=("Arial", 14, "bold"), bg="white", pady=10).pack()


    split_frame = tk.Frame(frame_display, bg="white")
    split_frame.pack(expand=True, fill="both")


    list_container = tk.Frame(split_frame, bg="white")
    list_container.pack(side="left", fill="y", padx=20)
    scrollbar = tk.Scrollbar(list_container)
    scrollbar.pack(side="right", fill="y")
    lista_visual = tk.Listbox(list_container, font=("Courier New", 11), yscrollcommand=scrollbar.set, bd=2, width=40)
    lista_visual.insert("end", f"{'PUERTA':<15} | {'ESTADO':<15} | {'AVIÓN':<15}")
    lista_visual.insert("end", "-" * 50)
    if datos:
        for item in datos:
            linea = f"{str(item[0]):<15} | {str(item[1]):<15} | {str(item[2]):<15}"
            lista_visual.insert("end", linea)
            if str(item[1]).lower() == 'occupied': lista_visual.itemconfig("end", fg="red")
    lista_visual.pack(side="left", expand=True, fill="both")
    scrollbar.config(command=lista_visual.yview)


    graph_container = tk.Frame(split_frame, bg="white")
    graph_container.pack(side="right", expand=True, fill="both")
    canvas = FigureCanvasTkAgg(generar_esquema_visual(datos), master=graph_container)
    canvas.draw()
    canvas.get_tk_widget().pack(expand=True, fill="both")

    tk.Button(frame_display, text="Cerrar", command=mostrar_imagen_original, bg="#f8d7da").pack(pady=10)

def mostrar_buscador_integrado():
    for widget in frame_display.winfo_children(): widget.destroy()
    if bcn is None:
        tk.Label(frame_display, text="Error: Debes cargar LEBL primero (Botón 1)", fg="red", bg="white",
                 font=("Arial", 12, "bold")).pack(pady=50)
        tk.Button(frame_display, text="Volver", command=mostrar_imagen_original).pack();
        return
    cuadro_busqueda = tk.Frame(frame_display, bg="#fff3cd", bd=2, relief="solid", padx=20, pady=20)
    cuadro_busqueda.place(relx=0.5, rely=0.5, anchor="center")
    tk.Label(cuadro_busqueda, text="BUSCAR TERMINAL POR AEROLÍNEA", bg="#fff3cd", font=("Arial", 11, "bold")).pack(
        pady=10)
    tk.Label(cuadro_busqueda, text="Introduce nombre o código ICAO:", bg="#fff3cd").pack()
    entrada_texto = tk.Entry(cuadro_busqueda, font=("Arial", 12), width=30);
    entrada_texto.pack(pady=10);
    entrada_texto.focus_set()
    label_resultado = tk.Label(cuadro_busqueda, text="", bg="#fff3cd", font=("Arial", 10, "italic"));
    label_resultado.pack(pady=5)

    def realizar_busqueda():
        nombre = entrada_texto.get().strip()
        if not nombre: label_resultado.config(text="Escribe algo...", fg="red"); return
        resultado = SearchTerminal(bcn, nombre)
        if resultado:
            label_resultado.config(text=f"Resultado: {resultado}", fg="green")
        else:
            label_resultado.config(text="No encontrada", fg="red")

    tk.Button(cuadro_busqueda, text="BUSCAR", command=realizar_busqueda, bg="#d1e7dd", font=("Arial", 10, "bold"),
              width=15).pack(pady=10)
    tk.Button(frame_display, text="Cerrar buscador", command=mostrar_imagen_original, bg="#f8d7da").pack(side="bottom",
                                                                                                         pady=20)



def mostrar_form_assign_gate():
    if not bcn:
        messagebox.showwarning("Atención", "Carga LEBL primero")
        return
    for widget in frame_display.winfo_children(): widget.destroy()

    form = tk.Frame(frame_display, bg="#fff3cd", bd=1, relief="solid", padx=20, pady=20)
    form.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(form, text="ASIGNAR PUERTA", font=("Arial", 12, "bold"), bg="#fff3cd").grid(row=0, columnspan=2, pady=10)


    tk.Label(form, text="ID Avión:", bg="#fff3cd").grid(row=1, column=0, sticky="e", pady=5)
    e_id = tk.Entry(form);
    e_id.grid(row=1, column=1, padx=5)

    tk.Label(form, text="Compañía:", bg="#fff3cd").grid(row=2, column=0, sticky="e", pady=5)
    e_cia = tk.Entry(form);
    e_cia.grid(row=2, column=1, padx=5)


    tk.Label(form, text="Origen:", bg="#fff3cd").grid(row=3, column=0, sticky="e", pady=5)

    var_origen = tk.StringVar(value="Schengen")
    frame_radios = tk.Frame(form, bg="#fff3cd")
    frame_radios.grid(row=3, column=1, sticky="w")

    tk.Radiobutton(frame_radios, text="Schengen", variable=var_origen, value="Schengen", bg="#fff3cd",
                   activebackground="#fff3cd").pack(side="left")
    tk.Radiobutton(frame_radios, text="No-Schengen", variable=var_origen, value="No-Schengen", bg="#fff3cd",
                   activebackground="#fff3cd").pack(side="left", padx=5)

    label_msg = tk.Label(form, text="", font=("Arial", 10, "bold"), bg="#fff3cd")
    label_msg.grid(row=4, columnspan=2, pady=10)

    def ejecutar():
        if not e_id.get() or not e_cia.get():
            label_msg.config(text="Faltan datos (ID/Compañía)", fg="orange")
            return


        nuevo_avion = Aircraft(e_id.get().strip(), e_cia.get().strip(), var_origen.get(), "00:00")
        res = AssignGate(bcn, nuevo_avion)

        if res != -1:
            label_msg.config(text=f"OK: Puerta {res}", fg="green")
            e_id.delete(0, tk.END);
            e_cia.delete(0, tk.END)
        else:
            label_msg.config(text="ERROR: No hay puertas libres", fg="red")

    tk.Button(form, text="Asignar", command=ejecutar, bg="#d1e7dd", width=12, font=("Arial", 10, "bold")).grid(row=5,
                                                                                                               column=0,
                                                                                                               pady=10)
    tk.Button(form, text="Cerrar", command=mostrar_imagen_original, width=12).grid(row=5, column=1, pady=10)



btn_frame = tk.Frame(root);
btn_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
frame_p1 = tk.Frame(btn_frame);
frame_p2 = tk.Frame(btn_frame);
frame_p3 = tk.Frame(btn_frame)


def ir_a_p1():
    frame_p2.pack_forget();
    frame_p3.pack_forget();
    frame_p1.pack(fill="x", expand=True)
    mostrar_imagen_original();
    btn_nav.config(text="Otras funciones (Pág 2)", command=ir_a_p2)


def ir_a_p2():
    frame_p1.pack_forget();
    frame_p3.pack_forget();
    frame_p2.pack(fill="x", expand=True)
    mostrar_imagen_original();
    btn_nav.config(text="Gestión Barcelona (Pág 3)", command=ir_a_p3)


def ir_a_p3():
    frame_p1.pack_forget();
    frame_p2.pack_forget();
    frame_p3.pack(fill="x", expand=True)
    mostrar_imagen_original();
    btn_nav.config(text="Volver a Aeropuertos (Pág 1)", command=ir_a_p1)


for i in range(6): frame_p1.columnconfigure(i, weight=1)
tk.Button(frame_p1, text="Load Airports", bg="#d1e7dd", font=("Arial", 10, "bold"), pady=10,
          command=lambda: [globals().update(airports=LoadAirports("Airports.txt")),
                           label_estado.config(text="Airports Loaded")]).grid(row=0, column=0, columnspan=2,
                                                                              sticky="ew", padx=2)
tk.Button(frame_p1, text="Add Airport", bg="#d1e7dd", font=("Arial", 10, "bold"), pady=10,
          command=mostrar_form_add).grid(row=0, column=2, columnspan=2, sticky="ew", padx=2)
tk.Button(frame_p1, text="Remove Airport", bg="#d1e7dd", font=("Arial", 10, "bold"), pady=10,
          command=mostrar_form_remove).grid(row=0, column=4, columnspan=2, sticky="ew", padx=2)
tk.Button(frame_p1, text="Gráfico Schengen", bg="#f8d7da", font=("Arial", 10, "bold"), pady=10,
          command=lambda: insertar_grafico(PlotAirports, airports)).grid(row=1, column=0, columnspan=3, sticky="ew",
                                                                         pady=10, padx=2)
tk.Button(frame_p1, text="Google Earth", bg="#f8d7da", font=("Arial", 10, "bold"), pady=10,
          command=lambda: [MapAirports(airports), mostrar_imagen_original()]).grid(row=1, column=3, columnspan=3,
                                                                                   sticky="ew", pady=10, padx=2)

for i in range(7): frame_p2.columnconfigure(i, weight=1)
labels_p2 = ["Load\nArrivals", "Plot\nHours", "Save\nFlights", "Plot\nAirlines", "Plot\nSchengen", "Map\nKML",
             "Long\nDist"]
cmds_p2 = [
    lambda: [globals().update(arrivals=LoadArrivals("Arrivals.txt")), label_estado.config(text="Arrivals Loaded")],
    lambda: insertar_grafico(PlotArrivals, arrivals),
    lambda: [SaveFlights(arrivals, "Saved.txt"), label_estado.config(text="Saved")],
    lambda: insertar_grafico(PlotAirlines, arrivals),
    lambda: insertar_grafico(PlotFlightsType, arrivals),
    lambda: [MapFlights(arrivals), mostrar_imagen_original()],
    lambda: mostrar_lista_vuelos(LongDistanceArrivals(arrivals, airports))
]
for i in range(7): tk.Button(frame_p2, text=labels_p2[i], bg="#cfe2ff", font=("Arial", 8, "bold"), pady=10,
                             command=cmds_p2[i]).grid(row=0, column=i, sticky="ew", padx=1)

for i in range(4): frame_p3.columnconfigure(i, weight=1)


def cargar_v3():
    global bcn
    bcn = LoadAirportStructure("Terminals.txt")
    label_estado.config(text="LEBL Cargado" if bcn != -1 else "Error LEBL")


tk.Button(frame_p3, text="1. Load LEBL\nStructure", bg="#fff3cd", font=("Arial", 9, "bold"), pady=10,
          command=cargar_v3).grid(row=0, column=0, sticky="ew", padx=2)
tk.Button(frame_p3, text="2. Gate\nOccupancy", bg="#fff3cd", font=("Arial", 9, "bold"), pady=10,
          command=lambda: mostrar_lista_puertas(GateOccupancy(bcn))).grid(row=0, column=1, sticky="ew", padx=2)
tk.Button(frame_p3, text="3. Search\nTerminal", bg="#fff3cd", font=("Arial", 9, "bold"), pady=10,
          command=mostrar_buscador_integrado).grid(row=0, column=2, sticky="ew", padx=2)
tk.Button(frame_p3, text="4. Assign\nGate", bg="#fff3cd", font=("Arial", 9, "bold"), pady=10,
          command=mostrar_form_assign_gate).grid(row=0, column=3, sticky="ew", padx=2)

label_estado = tk.Label(root, text="Listo", font=("Arial", 10));
label_estado.grid(row=3, column=0)
btn_nav = tk.Button(root, text="Otras funciones (Pág 2)", font=("Arial", 11, "bold"), bg="#e2e3e5", padx=20,
                    command=ir_a_p2);
btn_nav.grid(row=2, column=0, pady=20)

ir_a_p1();
root.mainloop()