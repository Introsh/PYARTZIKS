import tkinter as tk
import ttkbootstrap as ttk
from PIL import Image, ImageTk, ImageEnhance
import pygame
import os
import random
import subprocess

pygame.mixer.init()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(SCRIPT_DIR, "logo.ico")

root = ttk.Window(themename="superhero")
root.title("🎶 PYARTZIKS 🎶")
root.geometry("800x600")
root.configure(bg="#111111")

GLITCH_CHARACTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_-+=<>?/"
FINAL_TEXT = "🎵 PYARTZIKS 🎵"

if os.path.exists(ICON_PATH):
    root.iconbitmap(ICON_PATH)

glitch_label = ttk.Label(root, text="", font=("Helvetica", 32, "bold"), foreground="white", background="#111111")
glitch_label.place(relx=0.5, rely=0.4, anchor="center")

logo_path = os.path.join(SCRIPT_DIR, "logo.png")
logo_image = None
if os.path.exists(logo_path):
    original_logo = Image.open(logo_path).convert("RGBA")
    logo_size = (120, 120)
    logo_image = original_logo.resize(logo_size, Image.Resampling.LANCZOS)

logo_label = ttk.Label(root, background="#111111")
logo_label.place_forget()

transition_label = ttk.Label(root, text="▼", font=("Helvetica", 24), foreground="white", background="#111111")
transition_label.place_forget()

def generate_glitch_text(step=0):
    if step < len(FINAL_TEXT):
        glitch_text = "".join(
            FINAL_TEXT[i] if i < step else random.choice(GLITCH_CHARACTERS)
            for i in range(len(FINAL_TEXT))
        )
        glitch_label.config(text=glitch_text)
        root.after(80, lambda: generate_glitch_text(step + 1))
    else:
        glitch_label.config(text=FINAL_TEXT)
        root.after(500, show_transition_arrow)

def show_transition_arrow(opacity=0.0):
    transition_label.place(relx=0.5, rely=0.5, anchor="center")
    if opacity < 1.0:
        alpha = int(opacity * 255)
        transition_label.config(foreground=f"#{alpha:02X}{alpha:02X}{alpha:02X}")
        root.after(50, lambda: show_transition_arrow(opacity + 0.05))
    else:
        root.after(1000, show_logo)

def show_logo(opacity=0.0):
    if logo_image:
        faded_logo = logo_image.copy()
        faded_logo.putalpha(int(opacity * 255))
        logo_photo = ImageTk.PhotoImage(faded_logo)
        logo_label.config(image=logo_photo)
        logo_label.image = logo_photo
        logo_label.place(relx=0.5, rely=0.75, anchor="center")
        if opacity < 1.0:
            root.after(50, lambda: show_logo(opacity + 0.05))
        else:
            root.after(2500, fade_out_logo)

def fade_out_logo(opacity=1.0):
    if opacity > 0:
        faded_logo = logo_image.copy()
        faded_logo.putalpha(int(opacity * 255))
        logo_photo = ImageTk.PhotoImage(faded_logo)
        logo_label.config(image=logo_photo)
        logo_label.image = logo_photo
        root.after(50, lambda: fade_out_logo(opacity - 0.05))
    else:
        logo_label.place_forget()
        root.after(500, fade_out_arrow)

def fade_out_arrow(opacity=1.0):
    if opacity > 0:
        alpha = int(opacity * 255)
        transition_label.config(foreground=f"#{alpha:02X}{alpha:02X}{alpha:02X}")
        root.after(50, lambda: fade_out_arrow(opacity - 0.05))
    else:
        transition_label.place_forget()
        root.after(500, fade_out_text)

def fade_out_text(opacity=1.0):
    if opacity > 0:
        alpha = int(opacity * 255)
        glitch_label.config(foreground=f"#{alpha:02X}{alpha:02X}{alpha:02X}")
        root.after(50, lambda: fade_out_text(opacity - 0.05))
    else:
        glitch_label.place_forget()
        create_main_menu()

def clear_frame():
    for widget in frame.winfo_children():
        widget.destroy()

def create_main_menu():
    clear_frame()
    frame.pack(expand=True)
    ttk.Label(frame, text="🎶 Bienvenue sur PYARTZIKS 🎶", font=("Helvetica", 18, "bold")).pack(pady=10)
    ttk.Button(frame, text="🎵 Bac à sable", command=sandbox, bootstyle="primary").pack(pady=5, fill="x")
    ttk.Button(frame, text="🥁 Challenge", command=challenge, bootstyle="success").pack(pady=5, fill="x")
    ttk.Button(frame, text="⚙ Paramètres", command=parametre, bootstyle="warning").pack(pady=5, fill="x")

def sandbox():
    clear_frame()
    ttk.Label(frame, text="Mode Bac à Sable", font=("Helvetica", 16, "bold")).pack(pady=10)
    ttk.Button(frame, text="Batterie", command=zikB1).pack(pady=5, fill="x")
    ttk.Button(frame, text="Piano", command=zikP1).pack(pady=5, fill="x")
    ttk.Button(frame, text="Retour", command=create_main_menu, bootstyle="danger").pack(pady=5, fill="x")

def challenge():
    clear_frame()
    ttk.Label(frame, text="Musik'Défis", font=("Helvetica", 16, "bold")).pack(pady=10)
    ttk.Button(frame, text="Zik 1", command=zik1).pack(pady=5, fill="x")
    ttk.Button(frame, text="Zik 2", command=zik2).pack(pady=5, fill="x")
    ttk.Button(frame, text="Zik 3", command=zik3).pack(pady=5, fill="x")
    ttk.Button(frame, text="Retour", command=create_main_menu, bootstyle="danger").pack(pady=5, fill="x")

def parametre():
    clear_frame()
    ttk.Label(frame, text="Paramètres", font=("Helvetica", 16, "bold")).pack(pady=10)
    ttk.Button(frame, text="Volume +", command=volP).pack(pady=5, fill="x")
    ttk.Button(frame, text="Volume -", command=volM).pack(pady=5, fill="x")
    ttk.Button(frame, text="Crédit", command=credit).pack(pady=5, fill="x")
    ttk.Button(frame, text="Retour", command=create_main_menu, bootstyle="danger").pack(pady=5, fill="x")

def zikB1():
    print("Lancement de PYARTZIKS DRUM...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pyartziks_path = os.path.join(script_dir, "PYARTZIKS DRUM.py")
    subprocess.Popen(["py", pyartziks_path], shell=True)  
def zikP1():
    print("zikP1")

def zik1():
    print("zik1")

def zik2():
    print("zik2")

def zik3():
    print("zik3")

def volP():
    print("Volume +")

def volM():
    print("Volume -")

def credit():
    print("Crédit affiché")

frame = ttk.Frame(root, padding=20)
root.after(500, lambda: generate_glitch_text(0))
root.mainloop()
