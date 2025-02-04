import cv2
import mediapipe as mp
import tkinter as tk
from tkinter import ttk, messagebox
import platform
import subprocess

# Initialisation de Mediapipe
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# Détection des caméras avec leurs noms
def detect_cameras():
    cameras = []
    
    if platform.system() == "Windows":
        try:
            from pygrabber.dshow_graph import FilterGraph  # Module spécifique à Windows
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
                if "usb" in line.lower() or "video" in line.lower():  # Identifier les périphériques
                    index += 1
                    cameras.append((index, line.strip()))
        except FileNotFoundError:
            messagebox.showerror("Erreur", "Installez v4l-utils avec : sudo apt install v4l-utils")
            return []
    
    return cameras

# Ouvrir la webcam sélectionnée avec détection des mains
def open_camera():
    selected_camera = camera_var.get()
    
    if not selected_camera:
        messagebox.showwarning("Sélection requise", "Veuillez sélectionner une caméra.")
        return
    
    # Récupérer l'index (id de la caméra ) correspondant
    index = next((idx for idx, name in cameras if name == selected_camera), None)
    
    if index is None:
        messagebox.showerror("Erreur", "Impossible de trouver l'index de la caméra sélectionnée.")
        return

    cap = cv2.VideoCapture(index)
    
    if not cap.isOpened():
        messagebox.showerror("Erreur", f"Impossible d'ouvrir la caméra {selected_camera}. Vérifiez qu'elle est bien branchée ou essayez en une autre.")
        return

    with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
        
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("On ignore le cadre de camera vide")
                continue

            # Conversion en RGB pour MediaPipe
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(image)

            # Conversion en BGR pour OpenCV
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Dessiner les landmarks (en gros les traits de trackings) si des mains sont détectées
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style())

            # Afficher l'image
            cv2.imshow(f"Camera : {selected_camera} - Detection de mains", cv2.flip(image, 1))

            # Quitter avec la touche 'q'
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

# Interface graphique Tkinter
root = tk.Tk()
root.title("Selection de Camera avec Detection de Mains")

# Détection des caméras disponibles
cameras = detect_cameras()

if not cameras:
    messagebox.showwarning("Aucune caméra détectée", "Aucune caméra trouvée.")
else:
    camera_options = [name for _, name in cameras]
    camera_var = tk.StringVar()
    camera_var.set(camera_options[0])

    # Interface
    label = tk.Label(root, text="Sélectionnez une caméra :")
    label.pack(pady=5)

    camera_dropdown = ttk.Combobox(root, textvariable=camera_var, values=camera_options, state="readonly")
    camera_dropdown.pack(pady=5)

    open_button = tk.Button(root, text="Ouvrir la caméra", command=open_camera)
    open_button.pack(pady=10)

root.mainloop()
