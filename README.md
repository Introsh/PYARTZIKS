# PYARTZIKS 🎵🎮 ![image](https://github.com/user-attachments/assets/a3cae037-2713-4529-844b-179c2994e6ce)


PYARTZIKS est une application interactive et immersive permettant de jouer de la musique en réalité augmentée à l’aide de la détection de mouvements et de sons. Ce projet combine **modélisation 3D**, **reconnaissance des gestes**, **génération de sons** et **enregistrement de performances musicales**.

## 🚀 **Fonctionnalités principales**
### 🎼 **1. Musik'Défis**
Un mode **défi musical** pour tester vos compétences !  
- Sélectionnez un instrument et un morceau prédéfini.
- La **caméra se lance** avec une **partition simplifiée affichée en AR**.
- Une **modélisation 3D de l’instrument** apparaît.
- Un **système de reconnaissance sonore** vérifie si la note jouée correspond à celle affichée.
- **Si la note est fausse, le défi s’arrête**.

### 🎹 **2. Bac à sable (Sandbox)**
Un espace libre pour expérimenter et créer !  
- Sélectionnez un instrument (piano, batterie, etc.).
- La **caméra affiche l’instrument en 3D**.
- Un **bouton "Enregistrer votre performance"** permet :
  - **Enregistrement des notes jouées** dans un fichier texte (`1) Do, 2) Ré, ...`).
  - **Enregistrement audio** stocké dans un dossier `Enregistrements`.
  - **Possibilité de nommer son enregistrement avant sauvegarde**.

### 🎵 **3. Lecture et partage (à confirmer)**
- Accédez à un menu listant **vos enregistrements précédents**.
- Si aucun enregistrement n’a été fait, un **message d’information** apparaît.
- Possibilité de **réécouter** et **partager** ses créations.
- (Optionnel) **Système de "quête"** débloquant cette fonctionnalité après un premier enregistrement.

## 🎸 **Technologies utilisées**
- **🔹 OpenCV** : Capture vidéo et reconnaissance d'objets.
- **🔹 Mediapipe** : Détection des mains et des gestes.
- **🔹 PyOpenGL** : Modélisation et affichage d’instruments en 3D.
- **🔹 Tkinter & ttkbootstrap** : Interface graphique interactive.
- **🔹 Pygame** : Gestion et lecture des sons.
- **🔹 Pygrabber** : Détection des caméras disponibles.

## 🥁 **Instruments de musique en réalité augmentée**
- **Modélisation 3D** des instruments (piano, batterie).
- **Animations interactives** (ex. touches de piano qui s’enfoncent, baguettes de batterie en mouvement).
- **Détection des gestes** pour déclencher une note.

## 📸 **Système de capture de mouvement**
- **Utilisation de la caméra** pour détecter la main et la position des doigts.
- **Reconnaissance des gestes** pour interagir avec l’instrument en réalité augmentée.
- **Gestion de la force et de la vitesse du mouvement** pour moduler l’intensité du son.

## 🎙 **Génération et enregistrement des sons**
- **Banque de sons réalistes** pour chaque instrument.
- **Gestion des variations d’intensité** en fonction de la force du geste détecté.
- **Mode enregistrement et relecture** pour sauvegarder et écouter ses performances.
