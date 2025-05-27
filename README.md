# 🎵 PYARTZIKS

**PYARTZIKS** est une application musicale interactive en 3D centrée sur un **piano virtuel**.  
Elle propose un mode défi pour tester votre précision rythmique, ainsi qu’un **mode bac à sable** permettant de **composer vos propres morceaux et créer des niveaux personnalisés à partager**.

A partir de là, **c'est à vous de jouer !**

![image](https://github.com/user-attachments/assets/937d7d18-3b3c-4099-b977-85e300a2b809)

---

## ▶️ Comment lancer le projet

1. **Installer Python**  
   Le projet requiert **Python 3.12.9**.  
   Pour l’installer sous Windows, utilisez cette commande :

   ```bash
   winget install Python.Python.3.12 --version 3.12.9
   ```

2. **Installer les bibliothèques nécessaires**  
   Dans le terminal, exécutez :

   ```bash
   pip install panda3d pygame ttkbootstrap Pillow ou pip install -r requirements.txt
   ```

3. **Lancer le projet**  
   Depuis le dossier du projet, lancez :

   ```bash
   python main.py
   ```

   Le menu principal s’ouvrira et vous permettra d’accéder :
   - au **mode bac à sable** pour créer des séquences personnalisées,
   - au **mode défi** pour tester votre timing.

---

## 📁 Fichiers principaux

- `main.py` : Menu principal de l’application
- `PYARTZIKS PIANO.py` : Piano 3D interactif avec notes générées et sons
- `sons/` : Dossier contenant les sons `.wav` pour chaque touche du piano
- `modele 3D/` : Dossier contenant le modèle 3D du piano

---

## 🐍 Version Python recommandée

Le projet est compatible avec **Python 3.12.9**.  
Certaines bibliothèques comme **Panda3D** ou **ttkbootstrap** peuvent ne pas fonctionner correctement avec d’autres versions.

---

## 🎧 Dépendances techniques

- `panda3d` : affichage 3D du piano et des notes
- `pygame` : lecture des sons associés aux touches
- `ttkbootstrap` : interface graphique avec menus stylisés
- `Pillow` : affichage du logo et effets visuels




## 🎥 Vidéo présentation 
https://youtu.be/XaN6AxuhEvc?si=3tpHuOWKnNV4q2pd
