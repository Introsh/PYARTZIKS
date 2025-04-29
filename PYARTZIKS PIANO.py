from direct.showbase.ShowBase import ShowBase
from panda3d.core import Filename, AmbientLight, DirectionalLight, Vec4, loadPrcFileData, CollisionTraverser, CollisionNode, CollisionRay, CollisionHandlerQueue, TransparencyAttrib, NodePath , LVector3, CollisionSphere , CollisionHandlerEvent, TextureStage, TextNode
from direct.task import Task
from direct.gui.DirectGui import DirectButton, DirectOptionMenu, DirectSlider, DirectLabel
import pygame
import os

class Note:
        def __init__(self, jeu, nom_cible, est_speciale=False):
            self.jeu = jeu
            self.nom_cible = nom_cible
            self.modele = self.jeu.loader.loadModel("models/misc/rgbCube")
            self.modele.setScale(0.8, self.jeu.longueur_note, 0.4)
            self.modele.reparentTo(self.jeu.render)

            noeud_cible = self.jeu.piano.find(f"**/{self.nom_cible}")
            if noeud_cible.isEmpty():
                print(f"⚠️ Problème : {self.nom_cible} non trouvé !")
                return

            # Position cible
            self.position_cible = noeud_cible.getBounds().getCenter()
            self.position_cible = noeud_cible.getParent().getMat(self.jeu.render).xformPoint(self.position_cible)

            # Position d'apparition : très haut
            hauteur_apparition = 30.0
            position_apparition = LVector3(self.position_cible.x, self.position_cible.y + hauteur_apparition, self.position_cible.z)
            self.modele.setPos(position_apparition)

            self.temps_apparition = self.jeu.taskMgr.globalClock.getFrameTime()
            self.vitesse = self.jeu.vitesse_note

            if est_speciale:
                self.modele.setColor((0, 0, 0, 1), 1)
            else:
                self.modele.setColor((1, 1, 1, 1), 1)

            self.nom_tache = f"TacheDeplacementNote_{id(self)}"
            self.jeu.taskMgr.add(self.mettre_a_jour, self.nom_tache)

        
        def toucher_cible(self):
            if self.modele.isEmpty():
                return
            print(f"🎯 Note {self.nom_cible} touchée !")
            self.modele.removeNode()
            if self in self.jeu.notes_actives:
                self.jeu.notes_actives.remove(self)
            self.jeu.taskMgr.remove(self.nom_tache)

        
        def configurer_collision(self):
                    sphere_collision = CollisionSphere(0, 0, 0, 0.05)
                    noeud_collision = CollisionNode(f"note_{self.nom_cible}")
                    noeud_collision.addSolid(sphere_collision)
                    noeud_collision.setFromCollideMask(0x10)
                    noeud_collision.setIntoCollideMask(0)
                    np_collision = self.modele.attachNewNode(noeud_collision)

                    self.jeu.cTrav.addCollider(np_collision, self.jeu.gestionnaire_collision)
                    self.jeu.gestionnaire_collision.addInPattern('note-hit-%in')
                    self.jeu.accept(f'note-hit-{noeud_collision.getName()}', self.toucher_cible)

        def mettre_a_jour(self, tache):
            temps_actuel = self.jeu.taskMgr.globalClock.getFrameTime()
            position_actuelle = self.modele.getPos(self.jeu.render)

            # Descente verticale uniquement
            self.modele.setY(position_actuelle.getY() - self.vitesse)

            # Disparition automatique après 5 secondes
            if temps_actuel - self.temps_apparition > 5:
                print(f"⌛ Note {self.nom_cible} expirée.")
                self.toucher_cible()
                return tache.done

            # Vérification de proximité + touche espace
            noeud_cible = self.jeu.piano.find(f"**/{self.nom_cible}")
            if not noeud_cible.isEmpty():
                min_b, max_b = noeud_cible.getTightBounds()
                min_w = noeud_cible.getMat(self.jeu.render).xformPoint(min_b)
                max_w = noeud_cible.getMat(self.jeu.render).xformPoint(max_b)

                tolerance = 0.05
                if (min_w.x - tolerance <= position_actuelle.x <= max_w.x + tolerance and
                    min_w.y - tolerance <= position_actuelle.y <= max_w.y + tolerance and
                    min_w.z - tolerance <= position_actuelle.z <= max_w.z + tolerance):

                    if self.jeu.mouseWatcherNode.isButtonDown('space'):
                        self.jeu.jouer_son_touche(self.nom_cible)
                        self.toucher_cible()
                        return tache.done

            return tache.cont


class PianoViewer(ShowBase):

        def obtenir_volume_global(self):
            try:
                from main import GLOBAL_VOLUME
                return GLOBAL_VOLUME
            except:
                return 0.5

        def __init__(self):
            loadPrcFileData("", "window-title PYARTZIKS - Piano - Sandbox")
            loadPrcFileData("", "icon-filename logo.ico")
            super().__init__()
            pygame.mixer.init(frequency=22050, size=-16, channels=32)

            self.sons = {}
            self.musique_activee = False
            REPERTOIRE_SCRIPT = os.path.dirname(os.path.abspath(__file__))
            REPERTOIRE_SONS = os.path.join(REPERTOIRE_SCRIPT, "sons")

            # Chargement automatique des sons nommés pCubeXX.wav
            for fichier in os.listdir(REPERTOIRE_SONS):
                if fichier.endswith(".wav") and fichier.startswith("pCube"):
                    nom_touche = fichier.replace(".wav", "")
                    chemin_complet = os.path.join(REPERTOIRE_SONS, fichier)
                    try:
                        self.sons[nom_touche] = pygame.mixer.Sound(chemin_complet)
                        self.sons[nom_touche].set_volume(self.obtenir_volume_global())
                        print(f"🔊 Son chargé : {nom_touche}")
                    except Exception as e:
                        print(f"❌ Erreur de chargement pour {fichier} : {e}")

            self.score = 0
            self.cTrav = CollisionTraverser()
            self.gestionnaire_collision = CollisionHandlerEvent()
            self.gestionnaire_collision.addInPattern('%fn-into-%in')

            REPERTOIRE_SCRIPT = os.path.dirname(os.path.abspath(__file__))
            REPERTOIRE_MODELE = os.path.join(REPERTOIRE_SCRIPT, "modele 3D/Piano")
            CHEMIN_MODELE = os.path.join(REPERTOIRE_MODELE, "model.dae")
            REPERTOIRE_TEXTURES = os.path.join(REPERTOIRE_MODELE, "textures")

            if not os.path.exists(CHEMIN_MODELE):
                print(f"Erreur : le fichier {CHEMIN_MODELE} n'existe pas.")
                return

            self.piano = self.loader.loadModel(Filename.fromOsSpecific(CHEMIN_MODELE))
            self.piano.reparentTo(self.render)
            self.piano.setScale(2)
            self.piano.setPos(0, 0, 0)
            self.piano.setTransparency(TransparencyAttrib.MDual)
            self.piano.setTwoSided(True)
            self.accept("space", self.espace_appuye)

            if os.path.exists(REPERTOIRE_TEXTURES):
                self.piano.clearTexture()
                self.piano.setTextureOff(False)
                print("🎨 Textures automatiques conservées depuis le dossier .dae.")
            else:
                print("⚠️ Aucun dossier 'textures' détecté à côté de model.dae")

            self.configurer_eclairage()
            self.colorer_touches_manuellement()
            self.desactiver_interaction_pCube1()
            self.longueur_note = 0.4
            self.distance_apparition_note = 10
            self.vitesse_note = 0.15
            self.creer_boutons()
            self.creer_menu_deroulant()
            self.configurer_detection_clic()

            self.disableMouse()
            self.accept("space", self.verifier_clic_touche)
            self.taskMgr.add(self.mettre_a_jour_camera, "TacheMiseAJourCamera")
            self.taskMgr.add(self.mettre_a_jour_deplacement, "TacheMiseAJourDeplacement")

            self.mouseWatcher = self.mouseWatcherNode
            self.souris_appuyee = False
            self.dernier_x_souris = 0
            self.dernier_y_souris = 0
            self.touches_appuyees = {}
            self.accept("mouse1", self.on_mouse_press)
            self.accept("mouse1-up", self.on_mouse_release)
            self.accept("wheel_up", self.zoomer)
            self.accept("wheel_down", self.dezoomer)

            self.touches_deplacement = {"z": False, "s": False, "q": False, "d": False, "a": False, "e": False}
            for touche in self.touches_deplacement:
                self.accept(touche, self.definir_deplacement, [touche, True])
                self.accept(touche + "-up", self.definir_deplacement, [touche, False])

            self.vitesse = 0.18
            self.distance_camera = 10
            self.ajuster_camera()
            self.notes_actives = []


        def espace_appuye(self):
            print("Barre d'espace pressée")

        def jouer_son_touche(self, nom_touche):
            if self.musique_activee and nom_touche in self.sons:
                volume = self.obtenir_volume_global()
                son = self.sons[nom_touche]
                son.set_volume(volume)
                print(f"🔊 Lecture de {nom_touche} à volume {volume:.2f}")

                canal = pygame.mixer.find_channel(True)
                if canal:
                    canal.play(son)
                else:
                    print(f"❌ Aucun canal libre pour jouer {nom_touche}")
            else:
                print(f"❌ Aucun son associé à {nom_touche} ou musique désactivée")

        def colorer_touches_manuellement(self):
            touches_noires = ["pCube1", "pCube33", "pCube52", "pCube53", "pCube54", "pCube55", "pCube56", "pCube57", "pCube58", "pCube59", "pCube60"]
            touches_blanches = ["pCube40", "pCube51", "pCube45", "pCube44", "pCube48", "pCube50", "pCube43", "pCube47", "pCube49", "pCube42", "pCube41", "pCube46", "pCube6", "pCube10", "pCube2"]
            toutes_touches = touches_noires + touches_blanches

            for nom_touche in toutes_touches:
                touche = self.piano.find(f"**/{nom_touche}")
                if not touche.isEmpty():
                    if nom_touche in touches_noires:
                        touche.setColor((0, 0, 0, 1), 1)
                        touche.setTag("touche_noire", "true")
                    else:
                        touche.setColor((1, 1, 1, 1), 1)
                        touche.setTag("touche_blanche", "true")
                    touche.setTransparency(False)
                    touche.setTwoSided(True)
                    if nom_touche != "pCube1":
                        touche.node().setIntoCollideMask(0x10)
                    else:
                        touche.node().setIntoCollideMask(0)
                    touche.setName(nom_touche)

        def desactiver_interaction_pCube1(self):
            touche = self.piano.find("**/pCube1")
            if not touche.isEmpty():
                touche.node().setIntoCollideMask(0)
                print("🔒 Interaction désactivée pour pCube1")

        def creer_menu_deroulant(self):
            self.touches_noires = ["pCube33", "pCube52", "pCube53", "pCube54", "pCube55", "pCube56", "pCube57", "pCube58", "pCube59", "pCube60"]
            self.touches_blanches = ["pCube40", "pCube51", "pCube45", "pCube44", "pCube48", "pCube50", "pCube43", "pCube47", "pCube49", "pCube42", "pCube41", "pCube46", "pCube6", "pCube10", "pCube2"]
            
            self.touches_speciales = self.touches_noires + self.touches_blanches
            self.menu_options = DirectOptionMenu(
                text="Textures",
                scale=0.08,
                items=self.touches_speciales,
                initialitem=0,
                highlightColor=(0.65, 0.65, 0.65, 1),
                command=self.generer_note_selectionnee
            )
            self.menu_options.setPos(-1.3, 0, 0.9)
            self.derniere_touche_selectionnee = self.touches_speciales[0]

        def generer_note_selectionnee(self, touche_selectionnee):
            self.derniere_touche_selectionnee = touche_selectionnee
            print(f"🔁 Total notes actives : {len(self.notes_actives)}")
            print(f"🧱 Note créée depuis bouton : {self.derniere_touche_selectionnee}")

        def clic_bouton_generer_note(self):
            if hasattr(self, 'derniere_touche_selectionnee'):
                nom_touche = self.derniere_touche_selectionnee
                noeud_touche = self.piano.find(f"**/{nom_touche}")
                est_noire = noeud_touche.hasNetTag("touche_noire")
                note = Note(self, nom_touche, est_speciale=est_noire)
                self.notes_actives.append(note)
                print(f"🧱 Généré vers {nom_touche} | Couleur: {'noire' if est_noire else 'blanche'}")

        def creer_boutons(self):
            self.bouton_generer = DirectButton(
                text="Générer Note",
                scale=0.07,
                pos=(-1.3, 0, 0.75),
                command=self.clic_bouton_generer_note
            )

            self.slider_distance = DirectSlider(
                range=(1.0, 50.0),
                value=self.distance_apparition_note,
                pageSize=1.0,
                scale=0.8,
                pos=(0.2, 0, 0.85),
                command=self.mettre_a_jour_distance_apparition,
                extraArgs=[]
            )
            
            self.slider_vitesse = DirectSlider(
                range=(0.05, 1.0),
                value=self.vitesse_note,
                pageSize=0.01,
                scale=0.8,
                pos=(0.2, 0, 0.75),
                command=self.mettre_a_jour_vitesse_note,
                extraArgs=[]
            )

            self.bouton_musique = DirectButton(
                text="Activer/Désactiver Musique",
                scale=0.07,
                pos=(-1.3, 0, 0.65),
                command=self.basculer_musique
            )

            self.label_vitesse = DirectLabel(
                text=f"Vitesse des notes : {self.vitesse_note:.2f}",
                scale=0.05,
                pos=(0.2, 0, 0.83)
            )

            self.label_slider = DirectLabel(
                text=f"Distance d'apparition : {self.distance_apparition_note:.1f}",
                scale=0.05,
                pos=(0.2, 0, 0.95)
            )

        def mettre_a_jour_distance_apparition(self):
            self.distance_apparition_note = float(self.slider_distance['value'])
            self.label_slider["text"] = f"Distance d'apparition : {self.distance_apparition_note:.1f}"
        
        def mettre_a_jour_vitesse_note(self):
            self.vitesse_note = float(self.slider_vitesse['value'])
            self.label_vitesse["text"] = f"Vitesse des notes : {self.vitesse_note:.2f}"

        def configurer_eclairage(self):
            lumiere_ambiante = AmbientLight("lumiere_ambiante")
            lumiere_ambiante.setColor((0.5, 0.5, 0.5, 1))
            self.render.setLight(self.render.attachNewNode(lumiere_ambiante))

            lumiere_directionnelle = DirectionalLight("lumiere_directionnelle")
            lumiere_directionnelle.setColor((1, 1, 1, 1))
            noeud_lumiere = self.render.attachNewNode(lumiere_directionnelle)
            noeud_lumiere.setHpr(45, -45, 0)
            self.render.setLight(noeud_lumiere)

        def ajuster_camera(self):
            limites = self.piano.getTightBounds()
            if limites:
                min_b, max_b = limites
                centre = (min_b + max_b) / 2
                taille = max_b - min_b
                distance = max(taille) * 2
                self.camera.setPos(centre.x, centre.y - distance, centre.z)
                self.camera.lookAt(centre)

        def basculer_musique(self):
            self.musique_activee = not self.musique_activee
            print("Musique activée" if self.musique_activee else "Musique désactivée")

        def configurer_detection_clic(self):
            self.noeud_selection = CollisionNode('rayon_souris')
            self.np_selection = self.camera.attachNewNode(self.noeud_selection)
            self.rayon_selection = CollisionRay()
            self.noeud_selection.addSolid(self.rayon_selection)
            self.noeud_selection.setFromCollideMask(0x10)
            self.noeud_selection.setIntoCollideMask(0)
            self.file_attente_selection = CollisionHandlerQueue()
            self.cTrav.addCollider(self.np_selection, self.file_attente_selection)

        def verifier_clic_touche(self):
            if self.mouseWatcherNode.hasMouse():
                position_souris = self.mouseWatcherNode.getMouse()
                self.rayon_selection.setFromLens(self.camNode, position_souris.getX(), position_souris.getY())
                self.cTrav.traverse(self.render)

                if self.file_attente_selection.getNumEntries() > 0:
                    self.file_attente_selection.sortEntries()
                    objet_selectionne = self.file_attente_selection.getEntry(0).getIntoNodePath()
                    if objet_selectionne.hasNetTag("touche_noire") or objet_selectionne.hasNetTag("touche_blanche"):
                        nom_touche = objet_selectionne.getName()
                        noeud_touche = self.piano.find(f"**/{nom_touche}")

                        centre_touche = noeud_touche.getBounds().getCenter()
                        centre_touche = noeud_touche.getParent().getMat(self.render).xformPoint(centre_touche)

                        print(f"✅ Touche pressée : {nom_touche}")
                        self.jouer_son_touche(nom_touche)
                        if centre_touche is not None:
                            print(f"📍 Position touche : {centre_touche}")

                        objet_selectionne.setColor((1, 0, 0, 1), 1)
                        self.taskMgr.doMethodLater(0.3, self.reinitialiser_couleur, "reinitialiserCouleurTouche", extraArgs=[objet_selectionne], appendTask=False)

        def reinitialiser_couleur(self, noeud):
            if noeud:
                if noeud.hasNetTag("touche_noire"):
                    noeud.setColor((0, 0, 0, 1), 1)
                elif noeud.hasNetTag("touche_blanche"):
                    noeud.setColor((1, 1, 1, 1), 1)

        def afficher_info_camera(self):
            print(f"Position Camera: {self.camera.getPos()} | Orientation: {self.camera.getHpr()}")

        def on_mouse_press(self):  # Anciennement souris_appuyee
            if self.mouseWatcher.hasMouse():
                self.souris_appuyee = True  # Garder le même nom d'attribut
                self.dernier_x_souris = self.mouseWatcher.getMouseX()
                self.dernier_y_souris = self.mouseWatcher.getMouseY()

        def on_mouse_release(self):  # Anciennement souris_relachee
            self.souris_appuyee = False

        def mettre_a_jour_camera(self, tache):
            if self.souris_appuyee and self.mouseWatcher.hasMouse():
                nouveau_x = self.mouseWatcher.getMouseX()
                nouveau_y = self.mouseWatcher.getMouseY()
                delta_x = (nouveau_x - self.dernier_x_souris) * 100
                delta_y = (nouveau_y - self.dernier_y_souris) * 100
                self.camera.setH(self.camera.getH() - delta_x)
                self.camera.setP(self.camera.getP() + delta_y)
                self.dernier_x_souris = nouveau_x
                self.dernier_y_souris = nouveau_y
            return tache.cont

        def zoomer(self):
            self.camera.setY(self.camera, 0.2)

        def dezoomer(self):
            self.camera.setY(self.camera, -0.2)

        def definir_deplacement(self, touche, valeur):
            self.touches_deplacement[touche] = valeur

        def mettre_a_jour_deplacement(self, tache):
            if self.touches_deplacement["z"]:
                self.camera.setY(self.camera, self.vitesse)
            if self.touches_deplacement["s"]:
                self.camera.setY(self.camera, -self.vitesse)
            if self.touches_deplacement["q"]:
                self.camera.setX(self.camera, -self.vitesse)
            if self.touches_deplacement["d"]:
                self.camera.setX(self.camera, self.vitesse)
            if self.touches_deplacement["a"]:
                self.camera.setZ(self.camera, self.vitesse)
            if self.touches_deplacement["e"]:
                self.camera.setZ(self.camera, -self.vitesse)
            return tache.cont

        def verifier_touche(self, nom_touche):
            print(f"✅ verifier_touche appelé pour {nom_touche}")
            return True
        
if __name__ == "__main__":
        app = PianoViewer()
        app.run()
