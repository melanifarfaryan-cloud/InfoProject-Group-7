import ctypes
import os
import random
import tkinter as tk

import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from airport import Airport, LoadAirports, PlotAirports, MapAirports, AddAirport, RemoveAirport
from aircraft import (
    Aircraft, LoadArrivals, PlotArrivals, SaveFlights, PlotAirlines, PlotFlightsType,
    MapFlights, LongDistanceArrivals, LoadDepartures, MergeMovements, NightAircraft
)
from LEBL import (
    LoadAirportStructure, GateOccupancy, AssignGate, SearchTerminal,
    AssignGatesAtTime, PlotDayOccupancy
)


APP_TITLE = "AIRPORT MANAGEMENT"
CLICK_SOUND_PATH = r"C:\Users\Usuario\Downloads\pisseim-mund-online-audio-converter.mp3"
MUSIC_PATH = r"C:\Users\Usuario\Downloads\Mii Editor - Mii Maker (Wii U) Music (1).mp4"
FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "Daydream DEMO.otf")

COL_BG = "#b9e9ff"
COL_BG_2 = "#f8d6ec"
COL_PANEL = "#fff7bd"
COL_PANEL_2 = "#d8f3ff"
COL_TEXT = "#594062"
COL_WHITE = "#fffdf0"
COL_CYAN = "#78dff5"
COL_PINK = "#9cc8ff"
COL_GREEN = "#a7ef93"
COL_ORANGE = "#ffc36b"
COL_RED = "#ff7f91"
COL_INK = "#3b2d4a"
COL_SHADOW = "#8a6f94"


def load_daydream_font():
    return "Fixedsys"


FONT_FAMILY = load_daydream_font()
FONT_PIXEL = (FONT_FAMILY, 12)
FONT_PIXEL_SMALL = (FONT_FAMILY, 8)
FONT_TITLE = (FONT_FAMILY, 30)


def ObtenerTerminalAerolinea(id_aerolinea):
    try:
        if os.path.exists("T1_Airlines.txt"):
            with open("T1_Airlines.txt", "r") as f:
                if id_aerolinea.strip().upper() in f.read().upper():
                    return "T1"
    except Exception:
        pass
    return "T2"


def resetear_puertas_bcn():
    global bcn
    if not bcn or bcn == -1:
        return

    for term in bcn.terminals:
        for area in term.boarding_areas:
            for gate in area.gates:
                gate.occupancy = False
                gate.aircraft_id = ""


def init_click_sound():
    if not os.path.exists(CLICK_SOUND_PATH):
        return False
    try:
        ctypes.windll.winmm.mciSendStringW("close retroclick", None, 0, None)
        cmd = f'open "{CLICK_SOUND_PATH}" type mpegvideo alias retroclick'
        return ctypes.windll.winmm.mciSendStringW(cmd, None, 0, None) == 0
    except Exception:
        return False


def init_background_music():
    if not os.path.exists(MUSIC_PATH):
        return False
    try:
        with open(MUSIC_PATH, "rb") as f:
            header = f.read(64).lower()
        if header.startswith(b"<html") or b"410 gone" in header:
            return False
    except Exception:
        return False
    try:
        ctypes.windll.winmm.mciSendStringW("close bgmusic", None, 0, None)
        if ctypes.windll.winmm.mciSendStringW(f'open "{MUSIC_PATH}" alias bgmusic', None, 0, None) != 0:
            return False
        ctypes.windll.winmm.mciSendStringW("setaudio bgmusic volume to 140", None, 0, None)
        ctypes.windll.winmm.mciSendStringW("play bgmusic repeat", None, 0, None)
        return True
    except Exception:
        return False


def play_click_sound(event=None):
    if not sound_ready:
        return
    try:
        ctypes.windll.winmm.mciSendStringW("stop retroclick", None, 0, None)
        ctypes.windll.winmm.mciSendStringW("seek retroclick to start", None, 0, None)
        ctypes.windll.winmm.mciSendStringW("play retroclick", None, 0, None)
    except Exception:
        pass


class RetroButton(tk.Canvas):
    def __init__(self, parent, text, command, fill=COL_PANEL, accent=COL_CYAN,
                 width=170, height=58, font=FONT_PIXEL_SMALL):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=parent.cget("bg"),
            highlightthickness=0,
            bd=0
        )
        self.command = command
        self.text = text
        self.fill = fill
        self.accent = accent
        self.base_width = width
        self.base_height = height
        self.font = font
        self.hover = False
        self.draw()
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)

    def draw(self):
        self.delete("all")
        w = self.base_width
        h = self.base_height
        fill = self.accent if self.hover else self.fill
        text_col = COL_INK
        self.create_rectangle(6, 6, w, h, fill=COL_SHADOW, outline=COL_INK, width=2)
        self.create_rectangle(0, 0, w - 6, h - 6, fill=fill, outline=COL_INK, width=3)
        self.create_line(5, 5, w - 13, 5, fill=COL_WHITE, width=2)
        self.create_line(5, 5, 5, h - 13, fill=COL_WHITE, width=2)
        self.create_rectangle(10, h - 16, w - 18, h - 12, fill=COL_PANEL_2, outline="")
        self.create_text(
            (w - 6) // 2,
            (h - 6) // 2,
            text=self.text,
            fill=text_col,
            font=self.font,
            justify="center",
            width=w - 18
        )

    def on_enter(self, event=None):
        self.hover = True
        self.draw()

    def on_leave(self, event=None):
        self.hover = False
        self.draw()

    def on_click(self, event=None):
        if self.command:
            self.command()


def retro_label(parent, text, font=FONT_PIXEL, fg=COL_TEXT, bg=None):
    return tk.Label(parent, text=text, font=font, fg=fg, bg=bg or parent.cget("bg"))


def style_regular_button(btn, accent=COL_CYAN):
    btn.configure(
        bg=COL_PANEL,
        fg=COL_INK,
        activebackground=accent,
        activeforeground=COL_INK,
        font=FONT_PIXEL_SMALL,
        relief="solid",
        bd=3,
        padx=10,
        pady=7,
        cursor="hand2"
    )
    return btn



def mostrar_aviso_integrado(titulo, mensaje, color=None, btn_volver=True):
    """Muestra un aviso directamente en frame_display sin popup."""
    color = color or COL_ORANGE
    limpiar_display()
    frame_display.configure(bg=COL_BG)
    panel = tk.Frame(frame_display, bg=COL_PANEL, bd=4, relief="ridge", padx=30, pady=30)
    panel.place(relx=0.5, rely=0.5, anchor="center")
    retro_label(panel, titulo, font=(FONT_FAMILY, 13), fg=color, bg=COL_PANEL).pack(pady=(0, 10))
    retro_label(panel, mensaje, font=FONT_PIXEL_SMALL, fg=COL_INK, bg=COL_PANEL).pack(pady=5)
    if btn_volver:
        style_regular_button(tk.Button(panel, text="VOLVER", command=mostrar_imagen_original), COL_PINK).pack(pady=12)

def integrar_grafico_pixel(fig):
    fig.patch.set_facecolor(COL_WHITE)
    for ax in fig.axes:
        ax.set_facecolor(COL_WHITE)
        ax.tick_params(colors=COL_INK)
        ax.title.set_color(COL_TEXT)
        ax.xaxis.label.set_color(COL_INK)
        ax.yaxis.label.set_color(COL_INK)
        for spine in ax.spines.values():
            spine.set_color(COL_INK)
            spine.set_linewidth(1.5)


arrivals = []
departures = []
movements = []
airports = LoadAirports(filename="Airports.txt")
bcn = None

root = tk.Tk()
root.title(APP_TITLE)
root.state("zoomed")
root.configure(bg=COL_BG)

sound_ready = init_click_sound()
music_ready = init_background_music()
root.bind("<Button-1>", play_click_sound, add="+")

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=0)
root.rowconfigure(2, weight=0)

frame_display = tk.Frame(root, bg=COL_BG)
frame_display.grid(row=0, column=0, sticky="nsew")

menu_frame = tk.Frame(root, bg=COL_WHITE)
menu_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=0)

label_estado = tk.Label(root, text="Listo", font=FONT_PIXEL_SMALL, bg=COL_WHITE, fg=COL_TEXT)
label_estado.grid(row=2, column=0, sticky="ew", pady=(0, 8))

def limpiar_display():
    for widget in frame_display.winfo_children():
        widget.destroy()


def limpiar_menu():
    for widget in menu_frame.winfo_children():
        widget.destroy()


def draw_pixel_plane(canvas, x, y, scale=4):
    p = scale
    color = COL_WHITE
    shadow = COL_SHADOW
    pixels = [
        (5, 0), (6, 0), (7, 0),
        (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1),
        (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2), (9, 2), (10, 2), (11, 2),
        (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3),
        (5, 4), (6, 4), (7, 4),
        (4, 5), (5, 5), (7, 5), (8, 5)
    ]
    for px, py in pixels:
        canvas.create_rectangle(x + px * p + 2, y + py * p + 2, x + (px + 1) * p + 2, y + (py + 1) * p + 2, fill=shadow, outline=shadow)
        canvas.create_rectangle(x + px * p, y + py * p, x + (px + 1) * p, y + (py + 1) * p, fill=color, outline=color)


def draw_pixel_ship(canvas, x, y, scale=5):
    p = scale
    pixels = {
        COL_CYAN: [(2, 0), (3, 0), (1, 1), (2, 1), (3, 1), (4, 1), (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (1, 3), (2, 3), (3, 3), (4, 3)],
        COL_WHITE: [(4, 0), (5, 1), (6, 2), (5, 3)],
        COL_GREEN: [(2, 2), (3, 2)],
        COL_ORANGE: [(-1, 1), (-1, 2)]
    }
    for color, coords in pixels.items():
        for px, py in coords:
            canvas.create_rectangle(x + px * p + 2, y + py * p + 2, x + (px + 1) * p + 2, y + (py + 1) * p + 2, fill=COL_SHADOW, outline=COL_SHADOW)
            canvas.create_rectangle(x + px * p, y + py * p, x + (px + 1) * p, y + (py + 1) * p, fill=color, outline=color)


def draw_pixel_star(canvas, x, y, scale=5, color=COL_ORANGE):
    p = scale
    pixels = [(1, 0), (0, 1), (1, 1), (2, 1), (1, 2)]
    for px, py in pixels:
        canvas.create_rectangle(x + px * p, y + py * p, x + (px + 1) * p, y + (py + 1) * p, fill=color, outline=color)


def draw_big_pixel_airplane(canvas, cx, cy, scale=10):
    art = [
        "..............................................",
        "....NN........................................",
        "...NCCN.......................................",
        "..NCCCCN...................NNNNNN.............",
        ".NCCCCCCN..............NNNNCCCCCCNN...........",
        ".NCCCCCCCN.........NNNNCCCCCCCCCCCCNN.........",
        "..NCCCCCCCN....NNNNCCCCCCCCCCCCCCCCCCNN.......",
        "...NCCCCCCCNNNNCCCCCCCCCCCCCCCCCCCCCCCCNN.....",
        "NNNNWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWNN...",
        "NWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWNN.",
        "NNNNWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWNN...",
        "...NCCCCCCCNNNNCCCCCCCCCCCCCCCCCCCCCCCCNN.....",
        "..NCCCCCCCN....NNNNCCCCCCCCCCCCCCCCCCNN.......",
        ".NCCCCCCCN.........NNNNCCCCCCCCCCCCNN.........",
        ".NCCCCCCN..............NNNNCCCCCCNN...........",
        "..NCCCCN...................NNNNNN.............",
        "...NOON.......................................",
        "....NN........................................",
    ]
    palette = {
        "W": COL_WHITE,
        "C": COL_CYAN,
        "N": COL_INK,
        "O": COL_ORANGE,
    }
    rows = len(art)
    cols = max(len(row) for row in art)
    start_x = cx - (cols * scale) // 2
    start_y = cy - (rows * scale) // 2
    for r, row in enumerate(art):
        for c, cell in enumerate(row):
            if cell == ".":
                continue
            x1 = start_x + c * scale
            y1 = start_y + r * scale
            if cell != "N":
                canvas.create_rectangle(x1 + 2, y1 + 2, x1 + scale + 2, y1 + scale + 2, fill=COL_SHADOW, outline=COL_SHADOW)
            canvas.create_rectangle(x1, y1, x1 + scale, y1 + scale, fill=palette[cell], outline=palette[cell])
    for c in range(14, 36, 3):
        x = start_x + c * scale
        y = start_y + 9 * scale
        canvas.create_rectangle(x, y, x + scale, y + scale, fill=COL_ORANGE, outline=COL_ORANGE)


def mostrar_imagen_original():
    limpiar_display()
    frame_display.configure(bg=COL_BG)
    canvas = tk.Canvas(frame_display, bg=COL_BG, highlightthickness=0)
    canvas.pack(expand=True, fill="both")

    def render(event=None):
        canvas.delete("all")
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        for i in range(0, w, 32):
            canvas.create_line(i, 0, i, h, fill="#aee0f7")
        for j in range(0, h, 32):
            canvas.create_line(0, j, w, j, fill="#aee0f7")
        canvas.create_rectangle(28, 28, w - 28, h - 28, outline=COL_INK, width=4)
        canvas.create_rectangle(40, 40, w - 40, h - 40, outline=COL_WHITE, width=3)
        cloud_y = max(130, h // 2 - 125)
        for x in range(86, w - 90, 190):
            canvas.create_rectangle(x, cloud_y, x + 64, cloud_y + 24, fill=COL_WHITE, outline=COL_INK, width=2)
            canvas.create_rectangle(x + 28, cloud_y - 28, x + 96, cloud_y + 24, fill=COL_WHITE, outline=COL_INK, width=2)
        scale = max(6, min(13, (w - 180) // 48, (h - 180) // 20))
        draw_big_pixel_airplane(canvas, w // 2, h // 2 + 12, scale)
        canvas.create_text(w // 2, 70, text="ELIGE UNA SECCION", fill=COL_TEXT, font=(FONT_FAMILY, 22))

    canvas.bind("<Configure>", render)


def mostrar_loading():
    limpiar_menu()
    limpiar_display()
    label_estado.config(text="Mini-juego de carga: manten ESPACIO para volar")
    canvas = tk.Canvas(frame_display, bg=COL_BG, highlightthickness=0)
    canvas.pack(expand=True, fill="both")
    root.focus_force()

    level_length = 3600
    level_speed = 12
    level = [
        (900, 205, 255), (1500, 290, 250), (2120, 170, 265),
        (2760, 320, 255), (3340, 230, 270)
    ]
    state = {
        "tick": 0,
        "ship_y": 250,
        "vy": 0,
        "distance": 0,
        "space": False,
        "attempts": 1,
        "lives": 3,
        "stars": [],
        "running": True,
        "message": ""
    }

    def press_space(event=None):
        state["space"] = True

    def release_space(event=None):
        state["space"] = False

    root.bind("<space>", press_space)
    root.bind("<KeyRelease-space>", release_space)

    def skip_game(event=None):
        if state["running"]:
            state["running"] = False
            root.unbind("<space>")
            root.unbind("<KeyRelease-space>")
            root.unbind("<Return>")
            label_estado.config(text="Mini-juego saltado")
            canvas.after(200, mostrar_start)

    root.bind("<Return>", skip_game)

    def finish_game():
        state["running"] = False
        root.unbind("<space>")
        root.unbind("<KeyRelease-space>")
        label_estado.config(text="Carga completada")
        canvas.after(650, mostrar_start)

    def restart_level():
        state["distance"] = 0
        state["ship_y"] = 250
        state["vy"] = 0
        state["space"] = False
        state["lives"] -= 1
        if state["lives"] <= 0:
            state["attempts"] += 1
            state["lives"] = 3
            state["message"] = "GAME OVER! INTENTO NUEVO"
        else:
            state["message"] = "CRASH! PIERDES UNA VIDA"

    def add_star(w, h):
        y = random.randrange(90, max(120, h - 110), 24)
        state["stars"].append({"x": w + 40, "y": y, "speed": random.choice([5, 6, 7])})

    def draw_pillar(x, gap_y, gap_h, h):
        top_end = gap_y
        bottom_start = gap_y + gap_h
        for y1, y2 in [(72, top_end), (bottom_start, h - 88)]:
            if y2 <= y1:
                continue
            canvas.create_rectangle(x + 5, y1 + 5, x + 69, y2 + 5, fill=COL_SHADOW, outline=COL_INK, width=2)
            canvas.create_rectangle(x, y1, x + 64, y2, fill=COL_GREEN, outline=COL_INK, width=3)
            for yy in range(int(y1 + 14), int(y2 - 10), 30):
                canvas.create_rectangle(x + 12, yy, x + 52, yy + 10, fill=COL_WHITE, outline="")

    def animate():
        if not state["running"]:
            return
        tick = state["tick"]
        canvas.delete("all")
        w = canvas.winfo_width()
        h = canvas.winfo_height()

        if state["ship_y"] == 0:
            state["ship_y"] = h // 2

        for y in range(0, h, 32):
            color = COL_BG if (y // 32) % 2 == 0 else "#c8f0ff"
            canvas.create_rectangle(0, y, w, y + 32, fill=color, outline="")
        for i in range(-80, w + 80, 96):
            x = i - (tick * 5) % 96
            canvas.create_rectangle(x, h - 86, x + 54, h - 62, fill=COL_PANEL_2, outline=COL_INK, width=2)
            canvas.create_rectangle(x + 24, h - 116, x + 74, h - 86, fill=COL_WHITE, outline=COL_INK, width=2)
        canvas.create_rectangle(24, 24, w - 24, h - 24, outline=COL_INK, width=4)
        canvas.create_rectangle(32, 32, w - 32, h - 32, outline=COL_WHITE, width=3)

        if tick % 10 == 0:
            add_star(w, h)

        for star in state["stars"]:
            star["x"] -= star["speed"]
            draw_pixel_star(canvas, star["x"], star["y"], 4, COL_ORANGE if tick % 2 else COL_WHITE)
        state["stars"] = [s for s in state["stars"] if s["x"] > -30]

        ship_x = 110
        state["vy"] += -0.82 if state["space"] else 0.52
        state["vy"] = max(-8, min(8, state["vy"]))
        state["ship_y"] += state["vy"]
        ship_box = (ship_x - 5, state["ship_y"] - 5, ship_x + 46, state["ship_y"] + 32)
        hit = False

        if state["ship_y"] < 50 or state["ship_y"] > h - 108:
            hit = True

        for ox, gap_y, gap_h in level:
            screen_x = ox - state["distance"] + 190
            if -90 < screen_x < w + 90:
                draw_pillar(screen_x, gap_y, gap_h, h)
            pillar_box_x = (screen_x, screen_x + 64)
            if ship_box[0] < pillar_box_x[1] and ship_box[2] > pillar_box_x[0]:
                if ship_box[1] < gap_y or ship_box[3] > gap_y + gap_h:
                    hit = True

        finish_x = level_length - state["distance"] + 190
        if -60 < finish_x < w + 80:
            canvas.create_rectangle(finish_x, 58, finish_x + 22, h - 76, fill=COL_ORANGE, outline=COL_INK, width=3)
            for yy in range(70, h - 95, 36):
                canvas.create_rectangle(finish_x + 4, yy, finish_x + 18, yy + 16, fill=COL_WHITE if (yy // 36) % 2 else COL_INK, outline="")

        draw_pixel_ship(canvas, ship_x, state["ship_y"], 6)

        if hit:
            restart_level()
        else:
            state["distance"] += level_speed
            if tick % 42 == 0:
                state["message"] = ""
            if state["distance"] >= level_length:
                canvas.create_text(w // 2, h // 2, text="NIVEL COMPLETADO!", fill=COL_GREEN, font=(FONT_FAMILY, 22))
                finish_game()
                return

        canvas.create_text(w // 2 + 4, 66 + 4, text="LOADING LEVEL", fill=COL_SHADOW, font=(FONT_FAMILY, 24))
        canvas.create_text(w // 2, 66, text="LOADING LEVEL", fill=COL_TEXT, font=(FONT_FAMILY, 24))
        canvas.create_text(w // 2, 105, text="MANTEN ESPACIO PARA SUBIR  |  ENTER para saltarlo", fill=COL_INK, font=FONT_PIXEL)

        bar_x = 90
        bar_y = h - 62
        bar_w = max(220, w - 180)
        progress = min(1, state["distance"] / level_length)
        canvas.create_rectangle(bar_x + 5, bar_y + 5, bar_x + bar_w + 5, bar_y + 25, fill=COL_SHADOW, outline=COL_INK, width=2)
        canvas.create_rectangle(bar_x, bar_y, bar_x + bar_w, bar_y + 20, fill=COL_WHITE, outline=COL_INK, width=3)
        fill_w = int((bar_w - 8) * progress)
        for bx in range(0, fill_w, 18):
            canvas.create_rectangle(bar_x + 4 + bx, bar_y + 4, min(bar_x + 4 + bx + 14, bar_x + 4 + fill_w), bar_y + 16, fill=COL_CYAN, outline="")
        canvas.create_text(bar_x + bar_w // 2, bar_y - 18, text=f"DISTANCIA {int(progress * 100)}%   VIDAS {state['lives']}   INTENTO {state['attempts']}", fill=COL_INK, font=FONT_PIXEL_SMALL)
        if state["message"]:
            canvas.create_text(w // 2, h // 2 - 95, text=state["message"], fill=COL_RED, font=(FONT_FAMILY, 15))

        state["tick"] += 1
        root.after(24, animate)

    animate()


def mostrar_start():
    limpiar_menu()
    limpiar_display()
    label_estado.config(text="Pulsa Enter para iniciar")
    canvas = tk.Canvas(frame_display, bg=COL_BG, highlightthickness=0)
    canvas.pack(expand=True, fill="both")
    blink = {"on": True}

    def enter_start(event=None):
        mostrar_menu_principal()

    root.bind("<Return>", enter_start)

    def render():
        if not canvas.winfo_exists():
            return
        canvas.delete("all")
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        for y in range(0, h, 28):
            canvas.create_rectangle(0, y, w, y + 28, fill=COL_BG if (y // 28) % 2 == 0 else "#c8f0ff", outline="")
        for i in range(0, w, 28):
            canvas.create_line(i, 0, i, h, fill="#aee0f7")
        for j in range(0, h, 28):
            canvas.create_line(0, j, w, j, fill="#aee0f7")
        canvas.create_rectangle(34, 34, w - 34, h - 34, outline=COL_INK, width=5)
        canvas.create_rectangle(50, 50, w - 50, h - 50, outline=COL_WHITE, width=3)
        title_y = 105
        canvas.create_text(w // 2 + 5, title_y + 5, text=APP_TITLE, fill=COL_SHADOW, font=FONT_TITLE)
        canvas.create_text(w // 2, title_y, text=APP_TITLE, fill=COL_TEXT, font=FONT_TITLE)
        canvas.create_text(w // 2, title_y + 50, text="PASTEL PIXEL AIRPORT EDITION", fill=COL_PINK, font=FONT_PIXEL)
        scale = max(6, min(12, (w - 180) // 48, (h - 245) // 20))
        draw_big_pixel_airplane(canvas, w // 2, h // 2 + 45, scale)
        if blink["on"]:
            canvas.create_rectangle(w // 2 - 240, h - 128, w // 2 + 240, h - 82, fill=COL_PANEL, outline=COL_INK, width=3)
            canvas.create_text(w // 2, h - 105, text="DALE AL ENTER PARA INICIAR", fill=COL_INK, font=(FONT_FAMILY, 18))
        canvas.create_text(w // 2, h - 62, text="click sound: ON" if sound_ready else "click sound: MP3 no encontrado", fill=COL_TEXT, font=FONT_PIXEL_SMALL)
        blink["on"] = not blink["on"]
        root.after(520, render)

    render()


def mostrar_menu_principal():
    root.unbind("<Return>")
    limpiar_menu()
    limpiar_display()
    label_estado.config(text="Menu principal")
    canvas = tk.Canvas(frame_display, bg=COL_BG, highlightthickness=0)
    canvas.pack(expand=True, fill="both")

    def draw_bg(event=None):
        canvas.delete("all")
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        for y in range(0, h, 32):
            canvas.create_rectangle(0, y, w, y + 32, fill=COL_BG if (y // 32) % 2 == 0 else "#c8f0ff", outline="")
        for i in range(0, w, 32):
            canvas.create_line(i, 0, i, h, fill="#aee0f7")
        for j in range(0, h, 32):
            canvas.create_line(0, j, w, j, fill="#aee0f7")
        canvas.create_rectangle(36, 36, w - 36, h - 36, fill="", outline=COL_INK, width=4)
        canvas.create_text(w // 2, 80, text="SELECCIONA MODULO", fill=COL_TEXT, font=(FONT_FAMILY, 23))
        scale = max(6, min(12, (w - 180) // 48, (h - 185) // 20))
        draw_big_pixel_airplane(canvas, w // 2, h // 2 + 25, scale)

    canvas.bind("<Configure>", draw_bg)
    panel = tk.Frame(menu_frame, bg=COL_WHITE)
    panel.pack(anchor="center", pady=18)
    sections = [
        ("AEROPUERTOS", lambda: ir_a_seccion("p1"), COL_GREEN),
        ("VUELOS", lambda: ir_a_seccion("p2"), COL_CYAN),
        ("BARCELONA LEBL", lambda: ir_a_seccion("p3"), COL_ORANGE),
    ]
    for i, (text, cmd, accent) in enumerate(sections):
        btn = RetroButton(panel, text, cmd, fill=COL_PANEL, accent=accent, width=280, height=82, font=(FONT_FAMILY, 12))
        btn.grid(row=0, column=i, padx=18, pady=8)


def crear_submenu(titulo, botones, accent):
    limpiar_menu()
    header = tk.Frame(menu_frame, bg=COL_WHITE)
    header.pack(fill="x", padx=36, pady=(12, 4))
    retro_label(header, titulo, font=(FONT_FAMILY, 15), fg=accent, bg=COL_WHITE).pack(side="left", padx=6)
    back = RetroButton(header, "MENU", mostrar_menu_principal, fill=COL_PANEL, accent=COL_PINK, width=110, height=42, font=FONT_PIXEL_SMALL)
    back.pack(side="right", padx=6)

    buttons_panel = tk.Frame(menu_frame, bg=COL_WHITE)
    buttons_panel.pack(anchor="center", pady=(0, 18))
    for row_start in range(0, len(botones), 4):
        row_frame = tk.Frame(buttons_panel, bg=COL_WHITE)
        row_frame.pack(anchor="center", pady=7)
        for text, cmd, color in botones[row_start:row_start + 4]:
            btn = RetroButton(row_frame, text, cmd, fill=COL_PANEL, accent=color or accent, width=170, height=64)
            btn.pack(side="left", padx=14)


def ir_a_seccion(seccion):
    mostrar_imagen_original()
    if seccion == "p1":
        label_estado.config(text="Modulo Aeropuertos")
        crear_submenu("AEROPUERTOS", botones_p1(), COL_GREEN)
    elif seccion == "p2":
        label_estado.config(text="Modulo Vuelos")
        crear_submenu("VUELOS / ARRIVALS", botones_p2(), COL_CYAN)
    elif seccion == "p3":
        label_estado.config(text="Modulo Barcelona LEBL")
        crear_submenu("BARCELONA LEBL", botones_p3(), COL_ORANGE)


def mostrar_lista_vuelos(vuelos_filtrados):
    limpiar_display()
    frame_display.configure(bg=COL_BG)

    if not vuelos_filtrados:
        retro_label(frame_display, "No hay vuelos de larga distancia (>2000km)", fg=COL_RED).pack(pady=50)
        style_regular_button(tk.Button(frame_display, text="VOLVER", command=mostrar_imagen_original), COL_PINK).pack()
        return

    retro_label(frame_display, "VUELOS DE LARGA DISTANCIA (>2000 km)", font=(FONT_FAMILY, 14)).pack(pady=16)

    list_container = tk.Frame(frame_display, bg=COL_BG, bd=3, relief="ridge")
    list_container.pack(expand=True, fill="both", padx=55, pady=20)

    scrollbar = tk.Scrollbar(list_container)
    scrollbar.pack(side="right", fill="y")

    lista_visual = tk.Listbox(
        list_container,
        font=("Courier New", 11, "bold"),
        bg=COL_WHITE,
        fg=COL_INK,
        selectbackground=COL_PINK,
        selectforeground=COL_WHITE,
        yscrollcommand=scrollbar.set,
        bd=0,
        relief="flat"
    )

    header = f"{'ID':<10} | {'COMPANIA':<20} | {'ORIGEN':<10} | {'HORA':<8}"
    lista_visual.insert("end", header)
    lista_visual.insert("end", "-" * 60)

    for v in vuelos_filtrados:
        hora_vuelo = v.landing_time if v.landing_time else "--:--"
        linea = f"{v.id:<10} | {v.company:<20} | {v.origin:<10} | {hora_vuelo:<8}"
        lista_visual.insert("end", linea)

    lista_visual.pack(side="left", expand=True, fill="both")
    scrollbar.config(command=lista_visual.yview)

    style_regular_button(tk.Button(frame_display, text="CERRAR LISTA", command=mostrar_imagen_original), COL_PINK).pack(pady=10)


def insertar_grafico(funcion_plot, datos, filtro=None):
    if not datos:
        label_estado.config(text="Sin datos para graficar.", fg=COL_ORANGE)
        mostrar_aviso_integrado("SIN DATOS", "No hay datos cargados para graficar.", COL_ORANGE)
        return

    limpiar_display()
    frame_display.configure(bg=COL_BG)
    plt.close("all")

    frame_buscador = tk.Frame(frame_display, bg=COL_BG)
    frame_buscador.pack(side="top", anchor="ne", padx=20, pady=10)

    retro_label(frame_buscador, "BUSCAR:", font=FONT_PIXEL_SMALL, fg=COL_CYAN).pack(side="left")

    entry_filtro = tk.Entry(frame_buscador, width=15, font=FONT_PIXEL_SMALL, bd=2, bg=COL_WHITE, fg=COL_INK, insertbackground=COL_INK)
    entry_filtro.pack(side="left", padx=5)

    if filtro:
        entry_filtro.insert(0, filtro)

    def ejecutar_filtro():
        valor = entry_filtro.get().strip().upper()
        insertar_grafico(funcion_plot, datos, filtro=valor if valor != "" else None)

    style_regular_button(tk.Button(frame_buscador, text="FILTRAR (separar codigos por espacios)", command=ejecutar_filtro), COL_GREEN).pack(
        side="left")
    entry_filtro.bind("<Return>", lambda e: ejecutar_filtro())

    try:
        datos_a_dibujar = datos

        if filtro:
            lista_filtros = [t.strip() for t in str(filtro).split() if t.strip() != ""]

            if funcion_plot == PlotAirlines:
                datos_a_dibujar = [d for d in datos if d.company.strip().upper() in lista_filtros]
            elif funcion_plot == PlotAirports:
                datos_a_dibujar = [d for d in datos if d.icao.strip().upper() in lista_filtros]

        if not datos_a_dibujar:
            retro_label(frame_display, f"No se encontraron: '{filtro}'", fg=COL_RED).pack(pady=50)
            style_regular_button(
                tk.Button(frame_display, text="MOSTRAR TODOS", command=lambda: insertar_grafico(funcion_plot, datos)),
                COL_GREEN).pack()
            return

        original_show = plt.show
        plt.show = lambda *args, **kwargs: None
        try:
            funcion_plot(datos_a_dibujar)
        finally:
            plt.show = original_show
        fig = plt.gcf()
        fig.set_tight_layout(True)
        integrar_grafico_pixel(fig)

        graph_shell = tk.Frame(frame_display, bg=COL_WHITE, bd=4, relief="solid")
        graph_shell.pack(expand=True, fill="both", padx=24, pady=10)
        canvas = FigureCanvasTkAgg(fig, master=graph_shell)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both", padx=20, pady=8)

        style_regular_button(tk.Button(frame_display, text="CERRAR GRAFICO", command=mostrar_imagen_original),
                             COL_PINK).pack(pady=8)

    except Exception as e:
        label_estado.config(text=f"Error al graficar: {e}", fg=COL_RED)
        mostrar_aviso_integrado("ERROR GRÁFICO", f"Error al graficar:\n{e}", COL_RED)


def _read_attr(obj, names):
    for name in names:
        if hasattr(obj, name):
            value = getattr(obj, name)
            if callable(value):
                try:
                    value = value()
                except Exception:
                    continue
            if value not in (None, ""):
                return value
    return None


def _airport_code(airport):
    value = _read_attr(airport, ["icao", "ICAO", "code", "Code", "id", "ID", "name", "Name"])
    return str(value).strip().upper() if value not in (None, "") else ""


def _airport_coords(airport):
    lat = _read_attr(airport, ["lat", "Lat", "latitude", "Latitude", "LAT", "y", "Y"])
    lon = _read_attr(airport, ["lon", "Lon", "lng", "Lng", "longitude", "Longitude", "LON", "x", "X"])

    if (lat is None or lon is None) and hasattr(airport, "__dict__"):
        data = airport.__dict__
        for key, value in data.items():
            low = key.lower()
            if lat is None and ("lat" in low or low == "y"):
                lat = value
            if lon is None and ("lon" in low or "lng" in low or low == "x"):
                lon = value

        if lat is None or lon is None:
            nums = []
            for value in data.values():
                try:
                    nums.append(float(value))
                except Exception:
                    pass
            if len(nums) >= 2:
                lat, lon = nums[0], nums[1]

    try:
        return float(lat), float(lon)
    except Exception:
        return None


def _ensure_airports_loaded():
    global airports
    if airports:
        return airports
    try:
        airports = LoadAirports("Airports.txt")
    except Exception:
        airports = []
    return airports or []


def _airport_lookup():
    lookup = {}
    for airport in _ensure_airports_loaded():
        code = _airport_code(airport)
        if code:
            lookup[code] = airport
    return lookup


def _make_map_figure(title, points, lines=None):
    fig, ax = plt.subplots(figsize=(11, 5.5))
    fig.patch.set_facecolor(COL_WHITE)
    ax.set_facecolor("#eefbff")
    ax.set_title(title, color=COL_TEXT, fontweight="bold")
    ax.set_xlabel("LONGITUD", color=COL_INK)
    ax.set_ylabel("LATITUD", color=COL_INK)
    ax.grid(True, color="#c7eaf5", linewidth=1)
    for spine in ax.spines.values():
        spine.set_color(COL_INK)
        spine.set_linewidth(2)

    if lines:
        for x1, y1, x2, y2 in lines:
            ax.plot([x1, x2], [y1, y2], color=COL_CYAN, linewidth=1.4, alpha=0.7)

    if points:
        xs = [p[1] for p in points]
        ys = [p[2] for p in points]
        ax.scatter(xs, ys, s=58, color=COL_ORANGE, edgecolors=COL_INK, linewidths=1.2, zorder=3)
        pad_x = max(1, (max(xs) - min(xs)) * 0.12)
        pad_y = max(1, (max(ys) - min(ys)) * 0.12)
        ax.set_xlim(min(xs) - pad_x, max(xs) + pad_x)
        ax.set_ylim(min(ys) - pad_y, max(ys) + pad_y)
        for label, x, y in points[:35]:
            ax.text(x, y, f" {label}", fontsize=8, color=COL_INK, va="center")
    else:
        ax.text(0.5, 0.5, "NO HAY COORDENADAS CARGADAS\nPULSA LOAD AIRPORTS O EJECUTA DESDE LA CARPETA DE DATOS", transform=ax.transAxes, ha="center", va="center", color=COL_RED)

    fig.tight_layout()
    return fig


def mostrar_mapa_integrado(title, fig, status_text):
    limpiar_display()
    frame_display.configure(bg=COL_BG)
    retro_label(frame_display, title, font=(FONT_FAMILY, 14), fg=COL_TEXT).pack(pady=10)
    shell = tk.Frame(frame_display, bg=COL_WHITE, bd=4, relief="solid")
    shell.pack(expand=True, fill="both", padx=24, pady=10)
    canvas = FigureCanvasTkAgg(fig, master=shell)
    canvas.draw()
    canvas.get_tk_widget().pack(expand=True, fill="both", padx=16, pady=10)
    retro_label(frame_display, status_text, font=FONT_PIXEL_SMALL, fg=COL_TEXT).pack(pady=(0, 8))
    style_regular_button(tk.Button(frame_display, text="CERRAR MAPA", command=mostrar_imagen_original), COL_PINK).pack(pady=(0, 10))


def ejecutar_google_earth_airports():
    loaded_airports = _ensure_airports_loaded()
    try:
        MapAirports(loaded_airports)
        status = "KML generado / Google Earth solicitado. Vista integrada abajo."
    except Exception as e:
        status = f"No se pudo abrir Google Earth: {e}"
    points = []
    for airport in loaded_airports:
        coords = _airport_coords(airport)
        code = _airport_code(airport)
        if coords and code:
            lat, lon = coords
            points.append((code, lon, lat))
    fig = _make_map_figure("PREVIEW GOOGLE EARTH - AIRPORTS", points)
    mostrar_mapa_integrado("GOOGLE EARTH / AIRPORTS", fig, status)

def mostrar_form_add():
    limpiar_display()
    frame_display.configure(bg=COL_BG)

    form = tk.Frame(frame_display, bg=COL_PANEL, bd=4, relief="ridge", padx=30, pady=30)
    form.place(relx=0.5, rely=0.5, anchor="center")

    retro_label(form, "NUEVO AEROPUERTO", font=(FONT_FAMILY, 12), fg=COL_GREEN, bg=COL_PANEL).grid(row=0, columnspan=2, pady=10)

    tk.Label(form, text="ICAO:", bg=COL_PANEL, fg=COL_INK, font=FONT_PIXEL_SMALL).grid(row=1, column=0, sticky="e")
    e_icao = tk.Entry(form, bg=COL_WHITE, fg=COL_INK, insertbackground=COL_INK, font=FONT_PIXEL_SMALL)
    e_icao.grid(row=1, column=1, pady=5, padx=5)

    tk.Label(form, text="Latitud:", bg=COL_PANEL, fg=COL_INK, font=FONT_PIXEL_SMALL).grid(row=2, column=0, sticky="e")
    e_lat = tk.Entry(form, bg=COL_WHITE, fg=COL_INK, insertbackground=COL_INK, font=FONT_PIXEL_SMALL)
    e_lat.grid(row=2, column=1, pady=5, padx=5)

    tk.Label(form, text="Longitud:", bg=COL_PANEL, fg=COL_INK, font=FONT_PIXEL_SMALL).grid(row=3, column=0, sticky="e")
    e_lon = tk.Entry(form, bg=COL_WHITE, fg=COL_INK, insertbackground=COL_INK, font=FONT_PIXEL_SMALL)
    e_lon.grid(row=3, column=1, pady=5, padx=5)

    def guardar():
        try:
            cod = e_icao.get().upper()
            if AddAirport(airports, Airport(cod, float(e_lat.get()), float(e_lon.get()))):
                label_estado.config(text=f"Anadido {cod}", fg=COL_GREEN)
                mostrar_imagen_original()
            else:
                label_estado.config(text="Error: Ya existe", fg=COL_RED)
        except Exception:
            label_estado.config(text="Error en datos", fg=COL_RED)

    style_regular_button(tk.Button(form, text="ACEPTAR", command=guardar), COL_GREEN).grid(row=4, column=0, pady=15, padx=5)
    style_regular_button(tk.Button(form, text="CANCELAR", command=mostrar_imagen_original), COL_PINK).grid(row=4, column=1, pady=15, padx=5)


def mostrar_form_remove():
    limpiar_display()
    frame_display.configure(bg=COL_BG)

    form = tk.Frame(frame_display, bg=COL_PANEL, bd=4, relief="ridge", padx=30, pady=30)
    form.place(relx=0.5, rely=0.5, anchor="center")

    retro_label(form, "BORRAR ICAO", font=(FONT_FAMILY, 12), fg=COL_RED, bg=COL_PANEL).pack()

    e = tk.Entry(form, font=FONT_PIXEL, bg=COL_WHITE, fg=COL_INK, insertbackground=COL_INK)
    e.pack(pady=10)

    def borrar():
        cod = e.get().upper()
        for a in airports:
            if a.icao == cod:
                RemoveAirport(airports, a)
                label_estado.config(text=f"Borrado {cod}", fg=COL_RED)
                mostrar_imagen_original()
                return

        label_estado.config(text="No encontrado", fg=COL_ORANGE)

    btns = tk.Frame(form, bg=COL_PANEL)
    btns.pack()
    style_regular_button(tk.Button(btns, text="BORRAR", command=borrar), COL_RED).pack(side="left", padx=5)
    style_regular_button(tk.Button(btns, text="VOLVER", command=mostrar_imagen_original), COL_CYAN).pack(side="left", padx=5)


def generar_esquema_visual(datos):
    plt.close("all")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 18))
    fig.patch.set_facecolor(COL_WHITE)

    estados = {}
    for item in datos:
        estados[item[0]] = item[1].lower()

    def dibujar_terminal(ax, titulo, configuracion):
        ax.set_facecolor(COL_WHITE)
        ax.set_title(titulo, fontweight="bold", fontsize=20, pad=50, color=COL_TEXT)
        ax.plot([5, 145], [50, 50], color="#78dff5", linewidth=8)

        areas = list(configuracion.keys())

        for idx, clave in enumerate(areas):
            info = configuracion[clave]

            if len(areas) > 1:
                x = 20 + (idx * (110 / (len(areas) - 1)))
            else:
                x = 75

            y_fin = 90 if idx % 2 == 0 else 10
            ax.plot([x, x], [50, y_fin], color="#d8f3ff", linewidth=6, alpha=0.85)

            color_txt = "#3b2d4a" if "Schengen" in info["tipo"] and "non" not in info["tipo"].lower() else "#ff5fbf"
            txt_y = y_fin + 5 if idx % 2 == 0 else y_fin - 12

            ax.text(x, txt_y, f"ZONA {clave}\n({info['tipo']})", ha="center", fontsize=11, fontweight="bold", color=color_txt)

            p = info["start"]
            while p < info["start"] + info["cant"]:
                nombre_p = f"{info['pre']}{p}"
                estado_actual = estados.get(nombre_p, "free")
                color_p = "#ff5a5f" if estado_actual == "occupied" else "#7cff6b"

                pos_relativa = p - info["start"]
                dist = (pos_relativa / info["cant"]) * 35
                y_p = 50 + dist if idx % 2 == 0 else 50 - dist

                ax.plot([x, x + 4], [y_p, y_p], color=color_p, linewidth=3)
                p += 1

        ax.set_xlim(0, 150)
        ax.set_ylim(0, 105)
        ax.axis("off")

    conf_t1 = {
        "A": {"pre": "T1BAAG", "start": 1, "cant": 11, "tipo": "Schengen"},
        "B": {"pre": "T1BABG", "start": 1, "cant": 57, "tipo": "Schengen"},
        "C": {"pre": "T1BACG", "start": 1, "cant": 11, "tipo": "Schengen"},
        "D": {"pre": "T1BADG", "start": 1, "cant": 11, "tipo": "non-Schengen"},
        "E": {"pre": "T1BAEG", "start": 1, "cant": 11, "tipo": "non-Schengen"}
    }

    conf_t2 = {
        "M": {"pre": "T2BAMG", "start": 1, "cant": 8, "tipo": "Schengen"},
        "R": {"pre": "T2BARG", "start": 9, "cant": 11, "tipo": "Schengen"},
        "S": {"pre": "T2BASG", "start": 20, "cant": 11, "tipo": "Schengen"},
        "U": {"pre": "T2BAUG", "start": 30, "cant": 10, "tipo": "Schengen"},
        "W": {"pre": "T2BAWG", "start": 40, "cant": 10, "tipo": "non-Schengen"},
        "Y": {"pre": "T2BAYG", "start": 50, "cant": 10, "tipo": "non-Schengen"}
    }

    dibujar_terminal(ax1, "TERMINAL 1", conf_t1)
    dibujar_terminal(ax2, "TERMINAL 2", conf_t2)

    plt.tight_layout()
    return fig


def crear_control_tiempo_integrado(parent):
    if not movements:
        return

    for child in parent.winfo_children():
        if getattr(child, "is_sim", False):
            child.lift()
            return

    panel = tk.Frame(parent, bg=COL_PANEL, bd=3, relief="ridge", padx=12, pady=8)
    panel.is_sim = True
    panel.place(relx=0.98, rely=0.02, anchor="ne")
    panel.lift()

    retro_label(panel, "SIMULADOR HORARIO", font=FONT_PIXEL_SMALL, fg=COL_ORANGE, bg=COL_PANEL).pack()
    lbl_hora = tk.Label(panel, text="Hora: 00:00", font=FONT_PIXEL, bg=COL_PANEL, fg=COL_CYAN)
    lbl_hora.pack()

    def actualizar_hora(val):
        str_hora = str(int(float(val))).zfill(2) + ":00"
        lbl_hora.config(text="Hora: " + str_hora)
        AssignGatesAtTime(bcn, movements, str_hora)
        refrescar_contenido_puertas(GateOccupancy(bcn), mantener_control=True)

    slider = tk.Scale(panel, from_=0, to_=23, orient="horizontal", length=200, command=actualizar_hora, bg=COL_PANEL, fg=COL_INK, troughcolor=COL_WHITE, highlightthickness=0)
    slider.pack()

    style_regular_button(tk.Button(panel, text="RESET", command=lambda: [resetear_puertas_bcn(), slider.set(0)]), COL_ORANGE).pack(pady=4)


def refrescar_contenido_puertas(datos, mantener_control=False):
    panel_sim = None
    for widget in frame_display.winfo_children():
        if getattr(widget, "is_sim", False):
            panel_sim = widget
        else:
            widget.destroy()

    frame_display.configure(bg=COL_WHITE)
    retro_label(frame_display, "ESTADO DE PUERTAS LEBL", font=(FONT_FAMILY, 14), fg=COL_TEXT, bg=COL_WHITE).pack(pady=10)

    split_frame = tk.Frame(frame_display, bg=COL_WHITE)
    split_frame.pack(expand=True, fill="both")

    list_container = tk.Frame(split_frame, bg=COL_WHITE, bd=3, relief="ridge")
    list_container.pack(side="left", fill="y", padx=10, pady=10)
    scrollbar_lista = tk.Scrollbar(list_container, orient="vertical")
    scrollbar_lista.pack(side="right", fill="y")
    lista_visual = tk.Listbox(list_container, font=("Courier New", 10, "bold"), width=35, yscrollcommand=scrollbar_lista.set, bg=COL_WHITE, fg=COL_INK, bd=0)
    lista_visual.pack(side="left", expand=True, fill="both")
    scrollbar_lista.config(command=lista_visual.yview)

    for item in datos:
        lista_visual.insert("end", f"{item[0]:<12} | {item[1]:<10}")
        lista_visual.itemconfig("end", fg=COL_RED if item[1] == "occupied" else COL_GREEN)

    graph_outer = tk.Frame(split_frame, bg=COL_WHITE)
    graph_outer.pack(side="right", expand=True, fill="both", padx=(0, 10), pady=10)
    canvas_scroll = tk.Canvas(graph_outer, bg=COL_WHITE, highlightthickness=0)
    scrollbar_v = tk.Scrollbar(graph_outer, orient="vertical", command=canvas_scroll.yview)
    scrollable_frame = tk.Frame(canvas_scroll, bg=COL_WHITE)
    scrollable_frame.bind("<Configure>", lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all")))
    canvas_scroll.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas_scroll.configure(yscrollcommand=scrollbar_v.set)

    figura = generar_esquema_visual(datos)
    canvas_matplot = FigureCanvasTkAgg(figura, master=scrollable_frame)
    canvas_matplot.draw()
    canvas_matplot.get_tk_widget().pack()
    plt.close(figura)

    canvas_scroll.pack(side="left", expand=True, fill="both")
    scrollbar_v.pack(side="right", fill="y")

    style_regular_button(tk.Button(frame_display, text="CERRAR", command=mostrar_imagen_original), COL_PINK).pack(pady=5)

    if mantener_control:
        if panel_sim:
            panel_sim.lift()
        else:
            crear_control_tiempo_integrado(frame_display)


def mostrar_lista_puertas(datos):
    if bcn is None or bcn == -1:
        mostrar_aviso_integrado("AVISO", "Carga LEBL primero (Botón 1)", COL_ORANGE)
        return

    refrescar_contenido_puertas(datos, mantener_control=True)


def mostrar_simulador_interactivo():
    if not bcn or not movements:
        mostrar_aviso_integrado("AVISO", "Carga los datos de LEBL primero (Botón 1)", COL_ORANGE)
        return

    resetear_puertas_bcn()
    mostrar_lista_puertas(GateOccupancy(bcn))


def mostrar_buscador_integrado():
    limpiar_display()
    frame_display.configure(bg=COL_BG)

    if bcn is None:
        retro_label(frame_display, "Error: Debes cargar LEBL primero (Boton 1)", fg=COL_RED).pack(pady=50)
        style_regular_button(tk.Button(frame_display, text="VOLVER", command=mostrar_imagen_original), COL_CYAN).pack()
        return

    cuadro_busqueda = tk.Frame(frame_display, bg=COL_PANEL, bd=4, relief="ridge", padx=24, pady=24)
    cuadro_busqueda.place(relx=0.5, rely=0.5, anchor="center")

    retro_label(cuadro_busqueda, "BUSCAR TERMINAL POR AEROLINEA", font=(FONT_FAMILY, 10), fg=COL_ORANGE, bg=COL_PANEL).pack(pady=10)
    tk.Label(cuadro_busqueda, text="Introduce nombre o codigo ICAO:", bg=COL_PANEL, fg=COL_INK, font=FONT_PIXEL_SMALL).pack()

    entrada_texto = tk.Entry(cuadro_busqueda, font=FONT_PIXEL, width=30, bg=COL_WHITE, fg=COL_INK, insertbackground=COL_INK)
    entrada_texto.pack(pady=10)
    entrada_texto.focus_set()

    label_resultado = tk.Label(cuadro_busqueda, text="", bg=COL_PANEL, fg=COL_TEXT, font=FONT_PIXEL_SMALL)
    label_resultado.pack(pady=5)

    def realizar_busqueda():
        nombre = entrada_texto.get().strip()

        if not nombre:
            label_resultado.config(text="Escribe algo...", fg=COL_RED)
            return

        resultado = SearchTerminal(bcn, nombre)

        if resultado:
            label_resultado.config(text=f"Resultado: {resultado}", fg=COL_GREEN)
        else:
            label_resultado.config(text="No encontrada", fg=COL_RED)

    style_regular_button(tk.Button(cuadro_busqueda, text="BUSCAR", command=realizar_busqueda), COL_GREEN).pack(pady=10)
    style_regular_button(tk.Button(frame_display, text="CERRAR BUSCADOR", command=mostrar_imagen_original), COL_PINK).pack(side="bottom", pady=20)


def mostrar_form_assign_gate():
    if not bcn:
        mostrar_aviso_integrado("AVISO", "Carga primero el aeropuerto (Load LEBL)", COL_ORANGE)
        return

    limpiar_display()
    frame_display.configure(bg=COL_BG)

    form = tk.Frame(frame_display, bg=COL_PANEL, bd=4, relief="ridge", padx=22, pady=22)
    form.place(relx=0.5, rely=0.5, anchor="center")

    retro_label(form, "ASIGNAR PUERTA", font=(FONT_FAMILY, 13), fg=COL_ORANGE, bg=COL_PANEL).grid(row=0, columnspan=2, pady=15)

    tk.Label(form, text="ID del Vuelo:", font=FONT_PIXEL_SMALL, bg=COL_PANEL, fg=COL_INK).grid(row=1, column=0, sticky="e", pady=5)
    e_id = tk.Entry(form, font=FONT_PIXEL_SMALL, bg=COL_WHITE, fg=COL_INK, insertbackground=COL_INK)
    e_id.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(form, text="Compania (ICAO):", font=FONT_PIXEL_SMALL, bg=COL_PANEL, fg=COL_INK).grid(row=2, column=0, sticky="e", pady=5)
    e_cia = tk.Entry(form, font=FONT_PIXEL_SMALL, bg=COL_WHITE, fg=COL_INK, insertbackground=COL_INK)
    e_cia.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(form, text="Tipo de Vuelo:", font=FONT_PIXEL_SMALL, bg=COL_PANEL, fg=COL_INK).grid(row=3, column=0, sticky="e", pady=5)

    var_origen = tk.StringVar(value="Schengen")
    radio_frame = tk.Frame(form, bg=COL_PANEL)
    radio_frame.grid(row=3, column=1, sticky="w", padx=10)

    tk.Radiobutton(radio_frame, text="Schengen", variable=var_origen, value="Schengen", bg=COL_PANEL, fg=COL_INK, selectcolor=COL_WHITE, font=FONT_PIXEL_SMALL).pack(side="left")
    tk.Radiobutton(radio_frame, text="No-Schengen", variable=var_origen, value="No-Schengen", bg=COL_PANEL, fg=COL_INK, selectcolor=COL_WHITE, font=FONT_PIXEL_SMALL).pack(side="left", padx=10)

    label_msg = tk.Label(form, text="", font=FONT_PIXEL_SMALL, bg=COL_PANEL, fg=COL_TEXT)
    label_msg.grid(row=4, columnspan=2, pady=15)

    def ejecutar_asignacion():
        v_id = e_id.get().strip()
        v_cia = e_cia.get().strip().upper()
        v_tipo = var_origen.get()

        if v_id == "" or v_cia == "":
            label_msg.config(text="Rellena todos los campos", fg=COL_ORANGE)
            return

        nuevo_avion = Aircraft(v_id, v_cia, v_tipo, "00:00", None, None)
        res = AssignGate(bcn, nuevo_avion)

        if res != -1:
            label_msg.config(text=f"EXITO: Puerta {res} asignada", fg=COL_GREEN)
            e_id.delete(0, tk.END)
            e_cia.delete(0, tk.END)
        else:
            label_msg.config(text="ERROR: No hay puertas libres\no compania no encontrada", fg=COL_RED)

    style_regular_button(tk.Button(form, text="ASIGNAR", command=ejecutar_asignacion), COL_GREEN).grid(row=5, column=0, pady=10, padx=5)
    style_regular_button(tk.Button(form, text="CERRAR", command=mostrar_imagen_original), COL_PINK).grid(row=5, column=1, pady=10, padx=5)


def cargar_v4_completo():
    global bcn, arrivals, departures, movements

    bcn = LoadAirportStructure("Terminals.txt")
    arrivals = LoadArrivals("Arrivals.txt")
    departures = LoadDepartures("Departures.txt")

    if bcn != -1 and isinstance(arrivals, list) and isinstance(departures, list):
        movements = MergeMovements(arrivals, departures)
        label_estado.config(text="V4: Datos cargados y fusionados", fg=COL_CYAN)
    else:
        label_estado.config(text="Error: Revisa el formato de los .txt", fg=COL_RED)
        mostrar_aviso_integrado("ERROR DE CARGA", "No se pudieron procesar los vuelos.\nRevisa los archivos .txt", COL_RED)


def mostrar_form_assign_time():
    if not bcn or not movements:
        mostrar_aviso_integrado("AVISO", "Debes cargar los datos LEBL (V4) primero.", COL_ORANGE)
        return

    limpiar_display()
    frame_display.configure(bg=COL_BG)

    cuadro_control = tk.Frame(frame_display, bg=COL_PANEL, bd=4, relief="ridge", padx=40, pady=30)
    cuadro_control.place(relx=0.5, rely=0.5, anchor="center")

    retro_label(cuadro_control, "CONTROL HORARIO (V4)", font=(FONT_FAMILY, 13), fg=COL_CYAN, bg=COL_PANEL).pack(pady=(0, 20))
    tk.Label(cuadro_control, text="Introduce hora (00:00 - 23:00):", bg=COL_PANEL, fg=COL_INK, font=FONT_PIXEL_SMALL).pack()

    e_hora = tk.Entry(cuadro_control, font=FONT_PIXEL, justify="center", width=12, bd=2, bg=COL_WHITE, fg=COL_INK, insertbackground=COL_INK)
    e_hora.pack(pady=15)
    e_hora.focus_set()

    label_status = tk.Label(cuadro_control, text="", bg=COL_PANEL, fg=COL_TEXT, font=FONT_PIXEL_SMALL)
    label_status.pack(pady=5)

    def procesar():
        hora_val = e_hora.get().strip()

        if len(hora_val) == 5 and ":" in hora_val:
            rechazados = AssignGatesAtTime(bcn, movements, hora_val)
            label_status.config(text=f"Procesado: {hora_val}\nRechazados: {rechazados}", fg=COL_GREEN)
            root.after(1500, lambda: mostrar_lista_puertas(GateOccupancy(bcn)))
        else:
            label_status.config(text="Formato invalido (ej: 12:30)", fg=COL_RED)

    btn_frame_inner = tk.Frame(cuadro_control, bg=COL_PANEL)
    btn_frame_inner.pack(pady=10)

    style_regular_button(tk.Button(btn_frame_inner, text="PROCESAR HORA", command=procesar), COL_GREEN).pack(side="left", padx=5)
    style_regular_button(tk.Button(btn_frame_inner, text="VOLVER", command=mostrar_imagen_original), COL_PINK).pack(side="left", padx=5)

    e_hora.bind("<Return>", lambda e: procesar())


def gestionar_pernocta():
    if not bcn or not movements:
        mostrar_aviso_integrado("AVISO", "Carga LEBL primero (Botón 1)", COL_ORANGE)
        return

    aviones_noche = NightAircraft(movements)

    if not aviones_noche:
        label_estado.config(text="No hay aviones de pernocta.")
        mostrar_aviso_integrado("INFO", "No hay aviones de pernocta en esta sesión.", COL_CYAN)
        return

    label_estado.config(text=f"Pernocta: {len(aviones_noche)} aviones posicionados.", fg=COL_GREEN)
    mostrar_lista_puertas(GateOccupancy(bcn))


def ejecutar_grafico_v4():
    if not bcn or not movements:
        mostrar_aviso_integrado("AVISO", "Carga primero los datos V4 (Botón 1)", COL_ORANGE)
        return

    limpiar_display()
    frame_display.configure(bg=COL_BG)
    plt.close("all")

    try:
        original_show = plt.show
        plt.show = lambda *args, **kwargs: None
        try:
            PlotDayOccupancy(bcn, movements)
        finally:
            plt.show = original_show

        fig = plt.gcf()
        fig.set_tight_layout(True)
        integrar_grafico_pixel(fig)

        retro_label(frame_display, "OCUPACION DIARIA DE PUERTAS LEBL", font=(FONT_FAMILY, 13), fg=COL_ORANGE).pack(pady=10)

        graph_shell = tk.Frame(frame_display, bg=COL_WHITE, bd=4, relief="solid")
        graph_shell.pack(expand=True, fill="both", padx=24, pady=10)
        canvas = FigureCanvasTkAgg(fig, master=graph_shell)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both", padx=16, pady=8)

        style_regular_button(tk.Button(frame_display, text="CERRAR GRAFICO", command=mostrar_imagen_original), COL_PINK).pack(pady=8)

    except Exception as e:
        label_estado.config(text=f"Error al graficar: {e}", fg=COL_RED)
        mostrar_aviso_integrado("ERROR GRÁFICO", f"Error al graficar:\n{e}", COL_RED)


def AutomaticAssignGateSimple():

    global bcn, arrivals

    # Validaciones previas para evitar caídas
    if not bcn or bcn == -1:
        mostrar_aviso_integrado("AVISO", "El mapa o estructura de Barcelona (bcn) no está cargado.", COL_ORANGE)
        return

    if not arrivals:
        mostrar_aviso_integrado("AVISO", "No hay aviones cargados en la lista de llegadas (Arrivals).", COL_ORANGE)
        return

    asignados = 0
    fallidos = 0
    lista_detalles_fallos = []

    # Recorre todos los aviones que están llegando
    for avion in arrivals:
        resultado = AssignGate(bcn, avion)

        if resultado == -1:
            fallidos += 1
            ac_id = avion.id if hasattr(avion, 'id') else "Desconocido"
            lista_detalles_fallos.append(ac_id)
        else:
            asignados += 1

    limpiar_display()
    frame_display.configure(bg=COL_BG)
    retro_label(frame_display, "ASIGNACIÓN AUTOMÁTICA DE PUERTAS", font=(FONT_FAMILY, 14)).pack(pady=16)

    panel_resumen = tk.Frame(frame_display, bg=COL_WHITE, bd=3, relief="solid", padx=20, pady=20)
    panel_resumen.pack(expand=True, padx=40, pady=10)

    retro_label(panel_resumen, f"Total aviones procesados: {len(arrivals)}", font=FONT_PIXEL, fg=COL_INK).pack(pady=6)
    retro_label(panel_resumen, f"Asignaciones completadas: {asignados}", font=FONT_PIXEL, fg=COL_GREEN).pack(pady=6)
    retro_label(panel_resumen, f"Fallidos (sin puerta libre): {fallidos}", font=FONT_PIXEL, fg=COL_RED).pack(pady=6)

    if fallidos > 0:
        retro_label(panel_resumen, "Aviones sin puerta:", font=FONT_PIXEL_SMALL, fg=COL_SHADOW).pack(pady=(10, 2))

        frame_scroll = tk.Frame(panel_resumen, bg=COL_WHITE)
        frame_scroll.pack(fill="both", expand=True)

        scr = tk.Scrollbar(frame_scroll)
        scr.pack(side="right", fill="y")

        lb = tk.Listbox(frame_scroll, font=("Courier New", 10, "bold"), bg=COL_WHITE, fg=COL_RED, height=4,
                        yscrollcommand=scr.set, bd=1, relief="solid")
        for f in lista_detalles_fallos:
            lb.insert("end", f" Avión: {f}")
        lb.pack(side="left", fill="both", expand=True)
        scr.config(command=lb.yview)

    style_regular_button(tk.Button(frame_display, text="VOLVER", command=mostrar_imagen_original), COL_PINK).pack(
        pady=15)
    label_estado.config(text=f"Proceso concluído. Éxitos: {asignados} | Fallos: {fallidos}")


#FUNCIONES EXTRA

def SimulateDelaysSimple():

    global movements, arrivals, departures
    import random

    todos_vuelos = movements if movements else (arrivals + departures)
    if not todos_vuelos:
        mostrar_aviso_integrado("AVISO", "No hay vuelos cargados para aplicar retrasos.", COL_ORANGE)
        return

    vuelos_afectados = 0
    conflictos = 0
    # Diccionario para rastrear cuántos aviones coinciden en la misma hora de operación
    tracker_tiempo = {}

    for v in todos_vuelos:
        # Decisión aleatoria del 50%
        if random.random() < 0.5:
            retraso = random.randint(45, 50)
            vuelos_afectados += 1

            # Intentar parsear y retrasar landing_time o departure_time según corresponda
            for attr in ["landing_time", "departure_time"]:
                if hasattr(v, attr) and getattr(v, attr):
                    try:
                        h_str, m_str = getattr(v, attr).split(":")
                        total_minutos = int(h_str) * 60 + int(m_str) + retraso
                        # Formatear de vuelta a HH:MM asegurando límite de 24 horas
                        nueva_hora = f"{(total_minutos // 60) % 24:02d}:{total_minutos % 60:02d}"
                        setattr(v, attr, nueva_hora)

                        # Comprobar conflicto de espacio en pista/puerta
                        tracker_tiempo[nueva_hora] = tracker_tiempo.get(nueva_hora, 0) + 1
                        if tracker_tiempo[nueva_hora] > 1:
                            conflictos += 1
                    except Exception:
                        pass

    limpiar_display()
    frame_display.configure(bg=COL_BG)
    retro_label(frame_display, "SIMULACIÓN METEOROLÓGICA", font=(FONT_FAMILY, 14)).pack(pady=16)

    panel_info = tk.Frame(frame_display, bg=COL_WHITE, bd=3, relief="solid", padx=20, pady=20)
    panel_info.pack(expand=True, padx=40, pady=20)

    retro_label(panel_info, f"Vuelos procesados: {len(todos_vuelos)}", font=FONT_PIXEL, fg=COL_INK).pack(pady=6)
    retro_label(panel_info, f"Vuelos retrasados (50% aprox): {vuelos_afectados}", font=FONT_PIXEL, fg=COL_TEXT).pack(
        pady=6)
    retro_label(panel_info, f"Conflictos de espacio detectados: {conflictos}", font=FONT_PIXEL, fg=COL_RED).pack(pady=6)

    style_regular_button(tk.Button(frame_display, text="VOLVER", command=mostrar_imagen_original), COL_PINK).pack(
        pady=20)
    label_estado.config(text="Simulación de clima completada.")


def GenerarReporteEficiencia():

    global arrivals
    if not arrivals:
        mostrar_aviso_integrado("AVISO", "Carga los vuelos de llegada (Arrivals) primero.", COL_ORANGE)
        return

    cuenta_t1 = 0
    cuenta_t2 = 0

    for v in arrivals:
        terminal = ObtenerTerminalAerolinea(v.company)
        if terminal == "T1":
            cuenta_t1 += 1
        else:
            cuenta_t2 += 1

    total = cuenta_t1 + cuenta_t2
    p_t1 = (cuenta_t1 / total * 100) if total > 0 else 0
    p_t2 = (cuenta_t2 / total * 100) if total > 0 else 0

    limpiar_display()
    frame_display.configure(bg=COL_BG)
    retro_label(frame_display, "REPORTE DE EFICIENCIA OPERATIVA", font=(FONT_FAMILY, 14)).pack(pady=16)

    fig, ax = plt.subplots(figsize=(6, 4))
    integrar_grafico_pixel(fig)

    # Gráfico de barras simple para comparar la distribución de flujos
    bars = ax.bar(["Terminal 1", "Terminal 2"], [cuenta_t1, cuenta_t2], color=[COL_CYAN, COL_PINK], edgecolor=COL_INK,
                  width=0.6)
    ax.set_ylabel("Número de Vuelos", color=COL_INK)
    ax.set_title("Distribución de Vuelos por Terminal", color=COL_TEXT)

    # Añadir etiquetas de porcentaje sobre las barras
    for bar, percent in zip(bars, [p_t1, p_t2]):
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, yval + (yval * 0.02), f"{percent:.1f}%", ha='center', va='bottom',
                fontname='Courier New', weight='bold')

    graph_shell = tk.Frame(frame_display, bg=COL_WHITE, bd=4, relief="solid")
    graph_shell.pack(expand=True, fill="both", padx=40, pady=10)
    canvas = FigureCanvasTkAgg(fig, master=graph_shell)
    canvas.draw()
    canvas.get_tk_widget().pack(expand=True, fill="both", padx=20, pady=8)

    style_regular_button(tk.Button(frame_display, text="CERRAR REPORTE", command=mostrar_imagen_original),
                         COL_PINK).pack(pady=10)
    label_estado.config(text="Reporte de eficiencia generado correctamente.")


def GuardarConfiguracionPersonalizada():

    global arrivals, departures, airports
    import csv
    from tkinter import filedialog

    filepath = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
        title="Guardar Resumen de Configuración"
    )
    if not filepath:
        return

    try:
        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["MÓDULO", "INDICADOR / VARIABLE", "VALOR ACTUAL"])
            writer.writerow(["General", "Título de la Aplicación", APP_TITLE])
            writer.writerow(["Aeropuertos", "Total Registrados", len(airports) if airports else 0])
            writer.writerow(["Vuelos", "Llegadas Cargadas (Arrivals)", len(arrivals)])
            writer.writerow(["Vuelos", "Salidas Cargadas (Departures)", len(departures)])

            # Listar códigos ICAO de aeropuertos activos en la sesión
            if airports:
                codigos = [str(_airport_code(a)) for a in airports[:10]]
                writer.writerow(["Aeropuertos", "Muestra de Códigos Activos", ", ".join(codigos)])

        label_estado.config(text=f"Configuración guardada en: {filepath}", fg=COL_GREEN)
        label_estado.config(text="Configuración guardada en CSV.")
    except Exception as e:
        label_estado.config(text=f"Error al guardar: {e}", fg=COL_RED)


import os


def MapFlightsDynamicSimple():

    global movements, arrivals, departures, airports

    # Consolidar los vuelos disponibles según lo cargado en memoria
    vuelos_actuales = movements if movements else (arrivals + departures)
    if not vuelos_actuales:
        mostrar_aviso_integrado("AVISO", "No hay vuelos cargados para mapear en Google Earth.", COL_ORANGE)
        return

    # Asegurar que la lista de aeropuertos está inicializada
    lista_aeropuertos = _ensure_airports_loaded()

    # 1. Mapeo de aeropuertos
    ap_dict = {}
    for ap in lista_aeropuertos:
        icao_code = _airport_code(ap)
        coords = _airport_coords(ap)
        if icao_code and coords:
            ap_dict[icao_code] = coords

    # Coordenadas base de Barcelona LEBL
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

    fallback_hour = 6
    vuelos_mapeados = 0

    for ac in vuelos_actuales:
        orig_code = str(ac.origin).strip().upper() if hasattr(ac, 'origin') else ""
        if orig_code not in ap_dict:
            continue

        orig_lat, orig_lon = ap_dict[orig_code]

        try:
            from LEBL import IsSchengenAirport
            is_schengen = IsSchengenAirport(orig_code)
        except Exception:
            is_schengen = True

        style_url = "#schengen_line" if is_schengen else "#non_schengen_line"

        hora_final = "00:00"
        for attr in ['departure_time', 'time', 'arrival_time', 'landing_time']:
            if hasattr(ac, attr) and getattr(ac, attr):
                hora_final = getattr(ac, attr)
                break

        if not hora_final or hora_final == '-' or ':' not in str(hora_final):
            hora_final = f"{fallback_hour:02d}:00"
            fallback_hour = (fallback_hour + 1) if fallback_hour < 22 else 6

        time_dep = f"2026-05-30T{str(hora_final).strip()}:00Z"
        time_fin_dia = "2026-05-30T23:59:59Z"

        ac_id = ac.id if hasattr(ac, 'id') else "UNK"
        kml_content.append('  <Placemark>')
        kml_content.append(f'    <name>{ac_id}</name>')
        kml_content.append(f'    <description>Origen: {orig_code} -&gt; LEBL</description>')
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
        vuelos_mapeados += 1

    kml_content.append('</Document>')
    kml_content.append('</kml>')

    filename = "flights_dynamic.kml"
    try:
        # Obtener la ruta absoluta del archivo
        full_path = os.path.abspath(filename)

        with open(full_path, "w", encoding="utf-8") as file:
            file.write("\n".join(kml_content))


        import platform
        import subprocess

        sistema = platform.system()

        if sistema == "Windows":
            os.startfile(full_path)
        elif sistema == "Darwin":
            subprocess.run(["open", full_path])
        else:  # Linux
            subprocess.run(["xdg-open", full_path])


        limpiar_display()
        frame_display.configure(bg=COL_BG)
        retro_label(frame_display, "GOOGLE EARTH DESKTOP", font=(FONT_FAMILY, 14)).pack(pady=20)

        panel_exito = tk.Frame(frame_display, bg=COL_WHITE, bd=3, relief="solid", padx=25, pady=25)
        panel_exito.pack(expand=True, padx=40, pady=20)

        retro_label(panel_exito, f"¡Archivo '{filename}' enviado!", font=FONT_PIXEL, fg=COL_GREEN).pack(pady=8)
        retro_label(panel_exito, f"Vuelos proyectados: {vuelos_mapeados}", font=FONT_PIXEL, fg=COL_INK).pack(pady=8)
        retro_label(panel_exito, "Abriendo Google Earth Pro en tu equipo...", font=FONT_PIXEL_SMALL, fg=COL_TEXT).pack(
            pady=4)

        style_regular_button(tk.Button(frame_display, text="VOLVER", command=mostrar_imagen_original), COL_PINK).pack(
            pady=20)
        label_estado.config(text="KML ejecutado en la aplicación de Google Earth.")

    except Exception as e:
        label_estado.config(text=f"Error Google Earth: {e}", fg=COL_RED)
        mostrar_aviso_integrado("ERROR", f"No se pudo ejecutar Google Earth Pro:\n{e}", COL_RED)

def ejecutar_google_earth_flights():
    _ensure_airports_loaded()
    try:
        MapFlights(arrivals)
        status = "KML generado / Google Earth solicitado. Vista integrada abajo."
    except Exception as e:
        status = f"No se pudo abrir Google Earth: {e}"
    lookup = _airport_lookup()
    bcn_airport = lookup.get("LEBL")
    lines = []
    seen = set()
    for flight in arrivals:
        origin = getattr(flight, "origin", "").strip().upper()
        airport = lookup.get(origin)
        if airport:
            seen.add(origin)
            if bcn_airport:
                airport_coords = _airport_coords(airport)
                bcn_coords = _airport_coords(bcn_airport)
                if airport_coords and bcn_coords:
                    lat1, lon1 = airport_coords
                    lat2, lon2 = bcn_coords
                    lines.append((lon1, lat1, lon2, lat2))
    points = []
    for icao in sorted(seen):
        coords = _airport_coords(lookup[icao])
        if coords:
            lat, lon = coords
            points.append((icao, lon, lat))
    if bcn_airport:
        coords = _airport_coords(bcn_airport)
        if coords:
            lat, lon = coords
            points.append((_airport_code(bcn_airport), lon, lat))
    fig = _make_map_figure("PREVIEW GOOGLE EARTH - FLIGHTS", points, lines[:80])
    mostrar_mapa_integrado("GOOGLE EARTH / FLIGHTS", fig, status)
#Función de la versión 2 que hemos hecho ahora al final
def ejecutar_google_earth_vuelos_largos():
    #Genera un archivo KML únicamente con los vuelos que superen los 2000 km hacia/desde LEBL
    global arrivals

    #Validar que existan vuelos cargados en el sistema
    if not arrivals:
        messagebox.showwarning("Atención",
                               "No hay vuelos cargados. Por favor, pulsa primero el botón '1 LOAD LEBL V3 DATA'.")
        return

    lista_aeropuertos = _ensure_airports_loaded()
    ap_dict = {}
    for ap in lista_aeropuertos:
        icao_code = _airport_code(ap)
        coords = _airport_coords(ap)
        if icao_code and coords:
            ap_dict[icao_code.upper()] = coords

    #Obtener coordenadas base de Barcelona (LEBL)
    if "LEBL" in ap_dict:
        bcn_lat, bcn_lon = ap_dict["LEBL"]
    else:
        bcn_lat, bcn_lon = 41.2969, 2.0833

    #Filtrar rutas que superen los 2000 km
    kml_content = []
    kml_content.append('<?xml version="1.0" encoding="UTF-8"?>')
    kml_content.append('<kml xmlns="http://www.opengis.net/kml/2.2">')
    kml_content.append('<Document>')
    kml_content.append('  <name>Vuelos Larga Distancia (>2000 km)</name>')
    kml_content.append(
        '  <Style id="ruta_larga"><LineStyle><color>ff0000ff</color><width>4</width></LineStyle></Style>')

    vuelos_encontrados = 0

    for flight in arrivals:
        origin = getattr(flight, "origin", "").strip().upper()
        if origin in ap_dict:
            orig_lat, orig_lon = ap_dict[origin]

            # Calcular distancia real
            distancia = calcular_distancia(bcn_lat, bcn_lon, orig_lat, orig_lon)

            # Filtrar vuelos de más de 2000 km
            if distancia > 2000:
                vuelos_encontrados += 1
                flight_id = getattr(flight, "id", "Desconocido")
                company = getattr(flight, "company", "Aerolínea")

                # Crear marca de posición y línea geométrica KML
                kml_content.append('  <Placemark>')
                kml_content.append(f'    <name>Vuelo {flight_id} ({company})</name>')
                kml_content.append(f'    <description>Origen: {origin} | Distancia: {int(distancia)} km</description>')
                kml_content.append('    <styleUrl>#ruta_larga</styleUrl>')
                kml_content.append('    <LineString>')
                kml_content.append('      <tessellate>1</tessellate>')
                kml_content.append(f'      <coordinates>{orig_lon},{orig_lat},0 {bcn_lon},{bcn_lat},0</coordinates>')
                kml_content.append('    </LineString>')
                kml_content.append('  </Placemark>')

    kml_content.append('</Document>')
    kml_content.append('</kml>')

    if vuelos_encontrados == 0:
        messagebox.showinfo("Información", "No se encontraron vuelos entrantes con una distancia superior a 2000 km.")
        return

    #Escribir archivo KML y ejecutar Google Earth
    kml_path = "vuelos_larga_distancia.kml"
    try:
        with open(kml_path, "w", encoding="utf-8") as f:
            f.write("\n".join(kml_content))

        import platform
        import subprocess
        if platform.system() == "Windows":
            os.startfile(kml_path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", kml_path])
        else:
            subprocess.run(["xdg-open", kml_path])

        label_estado.config(text=f"Mapa con {vuelos_encontrados} vuelos largos enviado a Google Earth", fg=COL_GREEN)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo proyectar en Google Earth: {e}")



def botones_p1():
    return [
        ("LOAD\nAIRPORTS", lambda: [globals().update(airports=LoadAirports("Airports.txt")), label_estado.config(text="Airports Loaded", fg=COL_GREEN)], COL_GREEN),
        ("ADD\nAIRPORT", mostrar_form_add, COL_GREEN),
        ("REMOVE\nAIRPORT", mostrar_form_remove, COL_RED),
        ("GRAFICO\nSCHENGEN", lambda: insertar_grafico(PlotAirports, airports), COL_PINK),
        ("GOOGLE\nEARTH", ejecutar_google_earth_airports, COL_CYAN),
    ]


def botones_p2():
    return [
        ("LOAD\nARRIVALS", lambda: [globals().update(arrivals=LoadArrivals("Arrivals.txt")),
                                    label_estado.config(text="Arrivals Loaded", fg=COL_GREEN)], COL_GREEN),
        ("PLOT\nHOURS", lambda: insertar_grafico(PlotArrivals, arrivals), COL_CYAN),
        ("SAVE\nFLIGHTS", lambda: [SaveFlights(arrivals, "Saved.txt"), label_estado.config(text="Saved", fg=COL_GREEN)],
         COL_GREEN),
        ("PLOT\nAIRLINES", lambda: insertar_grafico(PlotAirlines, arrivals), COL_PINK),
        ("PLOT\nSCHENGEN", lambda: insertar_grafico(PlotFlightsType, arrivals), COL_ORANGE),
        ("MAP LONG\nDIST", ejecutar_google_earth_vuelos_largos, COL_CYAN),
        ("MAP\nKML", lambda: ejecutar_google_earth_flights(), COL_CYAN),
        ("LONG\nDIST", lambda: [
            # 1. Si la lista global de aeropuertos está vacía, la cargamos automáticamente
            globals().update(airports=LoadAirports("Airports.txt")) if not airports else None,

            # 2. Enviamos los vuelos filtrados a la pantalla
            mostrar_lista_vuelos(LongDistanceArrivals(arrivals, airports))
        ], COL_PINK),

        # Funciones extra
        ("SIMUL CLIMA", lambda: SimulateDelaysSimple(), COL_GREEN),
        ("EFICIENCIA", lambda: GenerarReporteEficiencia(), COL_CYAN),
        ("GUARDAR CONF", lambda: GuardarConfiguracionPersonalizada(), COL_PINK),
        ("GOOGLE EARTH", lambda: MapFlightsDynamicSimple(), COL_ORANGE)
    ]


def botones_p3():
    return [
        ("1 LOAD LEBL\nV4 DATA", cargar_v4_completo, COL_GREEN),
        ("2 GATE\nOCCUPANCY", lambda: mostrar_lista_puertas(GateOccupancy(bcn)), COL_ORANGE),
        ("3 SEARCH\nTERMINAL", mostrar_buscador_integrado, COL_CYAN),
        ("4 ASSIGN\nGATE", mostrar_form_assign_gate, COL_GREEN),
        ("5 ASSIGN AT\nTIME", mostrar_form_assign_time, COL_CYAN),
        ("6 PLOT DAY\nOCCUPANCY", ejecutar_grafico_v4, COL_PINK),
        ("7 NIGHT\nAIRCRAFTS", gestionar_pernocta, COL_ORANGE),
        ("8 TIME\nSIMULATOR", mostrar_simulador_interactivo, COL_GREEN),
        ("ASIGNACIÓN AUTOMÁTICA", lambda: AutomaticAssignGateSimple(), COL_ORANGE)
    ]


mostrar_loading()
root.mainloop()
