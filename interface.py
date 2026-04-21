import tkinter as tk
from airport import LoadAirports, PlotAirports, MapAirports, AddAirport, RemoveAirport


airports = LoadAirports(filename="Airports.txt")

root = tk.Tk()
root.geometry("1000x1000")
root.title("Airport Management")


root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=0)


foto = tk.PhotoImage(file="avion.png")
label_foto = tk.Label(root, image=foto)
label_foto.grid(row=0, column=0, sticky="nsew")


button_pictures_frame = tk.Frame(root)
button_pictures_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")


for i in range(6):
    button_pictures_frame.columnconfigure(i, weight=1)


def ejecutar_carga():
    global airports
    airports = LoadAirports("Airports.txt")
    label_estado.config(text="Se ha cargado completamente")
    root.after(3000, lambda: label_estado.config(text=""))

btn_load = tk.Button(
    button_pictures_frame,
    text="Load Airports",
    command=ejecutar_carga,
    font=("Arial", 11, "bold"), padx=10, pady=10, bg="#d1e7dd"
)
btn_load.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

label_estado = tk.Label(button_pictures_frame, text="", font=("Arial", 10), fg="green")
label_estado.grid(row=2, column=0, columnspan=6, pady=10)



btn_add = tk.Button(
    button_pictures_frame,
    text="Add Airport",
    command=lambda: AddAirport(airports, airport),
    font=("Arial", 11, "bold"), padx=10, pady=10, bg="#d1e7dd"
)
btn_add.grid(row=0, column=2, columnspan=2, padx=5, pady=5, sticky="ew")


btn_remove = tk.Button(
    button_pictures_frame,
    text="Remove Airport",
    command=lambda: print("Aquí llamarías a RemoveAirport(airports, 'ICAO_A_BORRAR')"),
    font=("Arial", 11, "bold"), padx=10, pady=10, bg="#d1e7dd"
)
btn_remove.grid(row=0, column=4, columnspan=2, padx=5, pady=5, sticky="ew")




button1 = tk.Button(
    button_pictures_frame,
    text="Gráfico Schengen vs No Schengen",
    command=lambda: PlotAirports(airports),
    font=("Arial", 11, "bold"),
    padx=10, pady=10, bg="#f8d7da"
)
button1.grid(row=1, column=0, columnspan=3, padx=5, pady=10, sticky="ew")

button2 = tk.Button(
    button_pictures_frame,
    text="Google Earth",
    command=lambda: MapAirports(airports),
    font=("Arial", 11, "bold"),
    padx=10, pady=10, bg="#f8d7da"
)
button2.grid(row=1, column=3, columnspan=3, padx=5, pady=10, sticky="ew")
root.state('zoomed')
root.mainloop()