import tkinter as tk
import ttkbootstrap as ttk

def zikB1(): #on peut aussi mettre indisponible...
    print("zikB1")#doit renvoyer a un challenge de Noe
def zikP1():
    print("zikP1")
    
def zikB2():
    print("zikB2")
def zikP2():
    print("zikP2")
    
def zikB3():
    print("zikB3")
def zikP3():
    print("zikP3")
    
def zik1():
    for widget in frame.winfo_children():
        widget.destroy()
    back_button = ttk.Button(frame, text="←", command=challenge)
    back_button.pack(side="left",padx=20)
    batterie_button = ttk.Button(frame, text="Batterie", command=zikB1)
    batterie_button.pack(side="left", padx=5)
    piano_button = ttk.Button(frame, text="Piano", command=zikP1)
    piano_button.pack(side="left", padx=5)
    
def zik2():
    for widget in frame.winfo_children():
        widget.destroy()
    back_button = ttk.Button(frame, text="←", command=challenge)
    back_button.pack(side="left",padx=20)
    batterie_button = ttk.Button(frame, text="Batterie", command=zikB2)
    batterie_button.pack(side="left", padx=5)
    piano_button = ttk.Button(frame, text="Piano", command=zikP2)
    piano_button.pack(side="left", padx=5)
def zik3():
    for widget in frame.winfo_children():
        widget.destroy()
    back_button = ttk.Button(frame, text="←", command=challenge)
    back_button.pack(side="left",padx=20)
    batterie_button = ttk.Button(frame, text="Batterie", command=zikB3)
    batterie_button.pack(side="left", padx=5)
    piano_button = ttk.Button(frame, text="Piano", command=zikP3)
    piano_button.pack(side="left", padx=5)


def challenge(): #ouvert depuis le MP permet de choisir une musique pr challenge
    for widget in frame.winfo_children():
        widget.destroy()
    back_button = ttk.Button(frame, text="←", command=main)
    back_button.pack(side="left",padx=20)
    zik1_button = ttk.Button(frame, text="Zik 1", command=zik1)
    zik1_button.pack(side="left", padx=5)
    zik2_button = ttk.Button(frame, text="Zik 2", command=zik2)
    zik2_button.pack(side="left", padx=5)
    zik3_button = ttk.Button(frame, text="Zik 3", command=zik3)
    zik3_button.pack(side="left", padx=5)
    root.mainloop()

def volP(): #ouvert depuis parametre un nbr de 1 a 10 a voir si c'est comptatible avec le log de son
    print("Vol+↑ clicked") 
def volM():
    print("Vol-↓ clicked")

def credit(): #ouvert depuis parametre renvoie le liens du projet national avec la video
    print("Crédit clicked")

def parametre(): #ouvert depuis le MP permet de gerer intesité du son, liens vers le projet 
    for widget in frame.winfo_children():
        widget.destroy()
    back_button = ttk.Button(frame, text="←", command=main)
    back_button.pack(side="left",padx=20)
    volP_button = ttk.Button(frame, text="Volume ↑", command=volP)
    volP_button.pack(side="left", padx=5)
    volM_button = ttk.Button(frame, text="Volume ↓", command=volM)
    volM_button.pack(side="left", padx=5)
    credit_button = ttk.Button(frame, text="Crédit", command=credit)
    credit_button.pack(side="left", padx=5)
    root.mainloop()

def sandbox():
    print("Sandbox clicked!")

def main(): #premiere fenetre = menu principal "MP"
    for widget in frame.winfo_children():
        widget.destroy()
    sandbox_button = ttk.Button(frame, text="Sandbox", command=sandbox)
    sandbox_button.pack(side="left", padx=5)
    challenge_button = ttk.Button(frame, text="Challenge", command=challenge)
    challenge_button.pack(side="left", padx=5)
    parametre_button = ttk.Button(frame, text="Parametre", command=parametre)
    parametre_button.pack(side="left", padx=5)
    root.mainloop()

root = ttk.Window(themename="journal")
root.title("My Application")
frame = ttk.Frame(root)
frame.pack(padx=200, pady=40)
command=main()



