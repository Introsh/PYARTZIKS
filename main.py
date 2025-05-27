import tkinter as tk
import ttkbootstrap as ttk
from PIL import Image, ImageTk, ImageEnhance
import pygame   
import os
import random
import subprocess

animation_skipped = False

pygame.mixer.init()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "volume.cfg")
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
SON_PATH = os.path.join(DATA_DIR, "son.txt")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def lire_volume_depuis_fichier():
    if os.path.exists(SON_PATH):
        try:
            with open(SON_PATH, "r") as f:
                return float(f.read())
        except:
            return 0.5
    return 0.5

def sauvegarder_volume_dans_fichier(volume):
    with open(SON_PATH, "w") as f:
        f.write(str(volume))


ICON_PATH = os.path.join(SCRIPT_DIR, "logo.ico")



GLOBAL_VOLUME = lire_volume_depuis_fichier()
pygame.mixer.music.set_volume(GLOBAL_VOLUME)


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


def skip_animation(event=None):
    global animation_skipped
    animation_skipped = True

def generate_glitch_text(step=0):
    
    if animation_skipped:
        glitch_label.place_forget()
        transition_label.place_forget()
        logo_label.place_forget()
        create_main_menu()
        return

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
 
def zikP1():
    print("Lancement de PYARTZIKS Piano...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pyartziks_path = os.path.join(script_dir, "PYARTZIKS PIANO.py")
    subprocess.Popen(["py", pyartziks_path], shell=True) 

def zik1():
    print("zik1")

def zik2():
    print("zik2")

def zik3():
    print("zik3")

def volP():
    global GLOBAL_VOLUME
    GLOBAL_VOLUME = min(1.0, GLOBAL_VOLUME + 0.1)
    pygame.mixer.music.set_volume(GLOBAL_VOLUME)
    sauvegarder_volume_dans_fichier(GLOBAL_VOLUME)
    print(f"🔊 Volume augmenté : {GLOBAL_VOLUME:.1f}")

def volM():
    global GLOBAL_VOLUME
    GLOBAL_VOLUME = max(0.0, GLOBAL_VOLUME - 0.1)
    pygame.mixer.music.set_volume(GLOBAL_VOLUME)
    sauvegarder_volume_dans_fichier(GLOBAL_VOLUME)
    print(f"🔉 Volume diminué : {GLOBAL_VOLUME:.1f}")

def credit():
    clear_frame()
    ttk.Label(frame, text="Crédits", font=("Helvetica", 16, "bold")).pack(pady=10)
    ttk.Label(frame, text="🎨 Design et Développement :", font=("Helvetica", 12)).pack(pady=2)
    ttk.Label(frame, text="Maher OSMAN et Naël MANTELLE", font=("Helvetica", 12, "italic")).pack(pady=2)
    ttk.Label(frame, text="🎵 Sons et musique :", font=("Helvetica", 12)).pack(pady=2)
    ttk.Label(frame, text="AKAI LPK25 & Bibliothèque d’échantillons libres", font=("Helvetica", 12, "italic")).pack(pady=2)
    ttk.Label(frame, text="🛠 Librairies utilisées :", font=("Helvetica", 12)).pack(pady=2)
    ttk.Label(frame, text="Panda3D, Pygame, Tkinter, ttkbootstrap,", font=("Helvetica", 12, "italic")).pack(pady=1)
    ttk.Label(frame, text="Pillow, subprocess, os, random", font=("Helvetica", 12, "italic")).pack(pady=1)
    ttk.Button(frame, text="Retour", command=parametre, bootstyle="danger").pack(pady=10, fill="x")

frame = ttk.Frame(root, padding=20)
root.bind("<Button-1>", skip_animation)
root.after(500, lambda: generate_glitch_text(0))
root.mainloop()
