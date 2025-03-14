import cv2
import mediapipe as mp
import tkinter as tk
from tkinter import ttk, messagebox
import platform
import subprocess
import pygame
import os
import time  

os.chdir(os.path.dirname(__file__))

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

pygame.mixer.init()
drum_sound = pygame.mixer.Sound("drum.wav") 

drums = [
    {"pos": (75, 300), "radius": 50, "color": (0, 0, 255), "last_hit": 0},  # Batterie rouge
    {"pos": (500, 300), "radius": 50, "color": (0, 255, 0), "last_hit": 0},  # Batterie verte
]


cooldown_time = 0.5  

def detect_cameras():
    cameras = []
    
    if platform.system() == "Windows":
        try:
            from pygrabber.dshow_graph import FilterGraph  # Module specifique a Windows
            graph = FilterGraph()
            devices = graph.get_input_devices()
            for index, name in enumerate(devices):
                cameras.append((index, name))
        except ImportError:
            messagebox.showerror("Erreur", "Veuillez installer pygrabber avec : pip install pygrabber")
            return []
    
    elif platform.system() == "Linux":
        try:
            result = subprocess.run(["v4l2-ctl", "--list-devices"], capture_output=True, text=True)
            lines = result.stdout.split("\n")
            index = -1
            for line in lines:
                if "usb" in line.lower() or "video" in line.lower():
                    index += 1
                    cameras.append((index, line.strip()))
        except FileNotFoundError:
            messagebox.showerror("Erreur", "Installez v4l-utils avec : sudo apt install v4l-utils")
            return []
    
    return cameras

def open_camera():
    selected_camera = camera_var.get()
    
    if not selected_camera:
        messagebox.showwarning("Selection requise", "Veuillez selectionner une camera.")
        return
    
    index = next((idx for idx, name in cameras if name == selected_camera), None)
    
    if index is None:
        messagebox.showerror("Erreur", "Impossible de trouver l'index de la camera selectionnee.")
        return

    cap = cv2.VideoCapture(index)
    
    if not cap.isOpened():
        messagebox.showerror("Erreur", f"Impossible d'ouvrir la camera {selected_camera}.")
        return

    with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
        
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("Image non capturee, on continue...")
                continue

            frame = cv2.flip(frame, 1) 
            h, w, _ = frame.shape
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)

            
            for drum in drums:
                cv2.circle(frame, drum["pos"], drum["radius"], drum["color"], -1)

            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style()
                    )

                    
                    index_finger = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    x, y = int(index_finger.x * w), int(index_finger.y * h)

                    
                    current_time = time.time()
                    for drum in drums:
                        drum_x, drum_y = drum["pos"]
                        if (x - drum_x) ** 2 + (y - drum_y) ** 2 < drum["radius"] ** 2:
                            if current_time - drum["last_hit"] > cooldown_time:
                                pygame.mixer.Sound.play(drum_sound) 
                                drum["last_hit"] = current_time 

            cv2.imshow(f"Camera : {selected_camera} - Detection de mains", frame)

            # TEST (juste pour quitter avec q)
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()


root = tk.Tk()
root.title("PYARTZIKS Backend")


cameras = detect_cameras()

if not cameras:
    messagebox.showwarning("Aucune camera detectee", "Aucune camera trouvee.")
else:
    camera_options = [name for _, name in cameras]
    camera_var = tk.StringVar()
    camera_var.set(camera_options[0])

    
    label = tk.Label(root, text="Selectionnez une camera :")
    label.pack(pady=5)

    camera_dropdown = ttk.Combobox(root, textvariable=camera_var, values=camera_options, state="readonly")
    camera_dropdown.pack(pady=5)

    open_button = tk.Button(root, text="Ouvrir la camera", command=open_camera)
    open_button.pack(pady=10)

root.mainloop()
