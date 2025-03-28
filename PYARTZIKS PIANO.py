from direct.showbase.ShowBase import ShowBase
from panda3d.core import Filename, AmbientLight, DirectionalLight, Vec4, loadPrcFileData, CollisionTraverser, CollisionNode, CollisionRay, CollisionHandlerQueue, TransparencyAttrib, NodePath , LVector3, CollisionSphere , CollisionHandlerEvent, TextureStage, TextNode
from direct.task import Task
from direct.gui.DirectGui import DirectButton, DirectOptionMenu, DirectSlider, DirectLabel
import pygame
import os

class Note:
        def __init__(self, game, target_name, is_special=False):
            self.game = game
            self.target_name = target_name
            self.model = self.game.loader.loadModel("models/misc/rgbCube")
            self.model.setScale(0.8, self.game.note_length, 0.4)
            self.model.reparentTo(self.game.render)

            target_node = self.game.piano.find(f"**/{self.target_name}")
            if target_node.isEmpty():
                print(f"⚠️ Problème : {self.target_name} non trouvé !")
                return

            # Position cible
            self.target_pos = target_node.getBounds().getCenter()
            self.target_pos = target_node.getParent().getMat(self.game.render).xformPoint(self.target_pos)

            # Position de spawn : très haut
            spawn_height = 30.0
            spawn_pos = LVector3(self.target_pos.x, self.target_pos.y + spawn_height, self.target_pos.z)
            self.model.setPos(spawn_pos)

            self.spawn_time = self.game.taskMgr.globalClock.getFrameTime()
            self.speed = self.game.note_speed

            if is_special:
                self.model.setColor((0, 0, 0, 1), 1)
            else:
                self.model.setColor((1, 1, 1, 1), 1)

            self.task_name = f"MoveNoteTask_{id(self)}"
            self.game.taskMgr.add(self.update, self.task_name)

        
        def hit_target(self):
            if self.model.isEmpty():
                return
            print(f"🎯 Note {self.target_name} touchée !")
            self.model.removeNode()
            if self in self.game.active_notes:
                self.game.active_notes.remove(self)
            self.game.taskMgr.remove(self.task_name)


        
        def setup_collision(self):
                    coll_sphere = CollisionSphere(0, 0, 0, 0.05)
                    coll_node = CollisionNode(f"note_{self.target_name}")
                    coll_node.addSolid(coll_sphere)
                    coll_node.setFromCollideMask(0x10)
                    coll_node.setIntoCollideMask(0)
                    coll_np = self.model.attachNewNode(coll_node)

                    self.game.cTrav.addCollider(coll_np, self.game.collision_handler)
                    self.game.collision_handler.addInPattern('note-hit-%in')
                    self.game.accept(f'note-hit-{coll_node.getName()}', self.hit_target)

        def update(self, task):
            current_time = self.game.taskMgr.globalClock.getFrameTime()
            current_pos = self.model.getPos(self.game.render)

            # Descente verticale uniquement
            self.model.setY(current_pos.getY() - self.speed)

            # Disparition automatique après 5 secondes
            if current_time - self.spawn_time > 5:
                print(f"⌛ Note {self.target_name} expirée.")
                self.hit_target()
                return task.done

            # Vérification de proximité + touche espace
            target_node = self.game.piano.find(f"**/{self.target_name}")
            if not target_node.isEmpty():
                min_b, max_b = target_node.getTightBounds()
                min_w = target_node.getMat(self.game.render).xformPoint(min_b)
                max_w = target_node.getMat(self.game.render).xformPoint(max_b)

                tolerance = 0.05
                if (min_w.x - tolerance <= current_pos.x <= max_w.x + tolerance and
                    min_w.y - tolerance <= current_pos.y <= max_w.y + tolerance and
                    min_w.z - tolerance <= current_pos.z <= max_w.z + tolerance):

                    if self.game.mouseWatcherNode.isButtonDown('space'):
                        self.game.play_sound_for_key(self.target_name)
                        self.hit_target()
                        return task.done

            return task.cont


class PianoViewer(ShowBase):

        def get_global_volume(self):
            try:
                from main import GLOBAL_VOLUME
                return GLOBAL_VOLUME
            except:
                return 0.5

        def __init__(self):
            loadPrcFileData("", "window-title PYARTZIKS - Piano - Sandbox")
            loadPrcFileData("", "icon-filename logo.ico")
            super().__init__()
            pygame.mixer.init(frequency=22050, size=-16, channels=32)  # Initialisation avec 8 canaux

            self.sounds = {}
            self.music_enabled = False
            SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
            SOUND_DIR = os.path.join(SCRIPT_DIR, "sons")

            # Chargement automatique des sons nommés pCubeXX.wav
            for filename in os.listdir(SOUND_DIR):
                if filename.endswith(".wav") and filename.startswith("pCube"):
                    key_name = filename.replace(".wav", "")
                    full_path = os.path.join(SOUND_DIR, filename)
                    try:
                        self.sounds[key_name] = pygame.mixer.Sound(full_path)
                        self.sounds[key_name].set_volume(self.get_global_volume())
                        print(f"🔊 Son chargé : {key_name}")
                    except Exception as e:
                        print(f"❌ Erreur de chargement pour {filename} : {e}")

            self.score = 0
            self.cTrav = CollisionTraverser()
            self.collision_handler = CollisionHandlerEvent()
            self.collision_handler.addInPattern('%fn-into-%in')

            SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
            MODEL_DIR = os.path.join(SCRIPT_DIR, "modele 3D/Piano")
            MODEL_PATH = os.path.join(MODEL_DIR, "model.dae")
            TEXTURE_DIR = os.path.join(MODEL_DIR, "textures")

            if not os.path.exists(MODEL_PATH):
                print(f"Erreur : le fichier {MODEL_PATH} n'existe pas.")
                return

            self.piano = self.loader.loadModel(Filename.fromOsSpecific(MODEL_PATH))
            self.piano.reparentTo(self.render)
            self.piano.setScale(2)
            self.piano.setPos(0, 0, 0)
            self.piano.setTransparency(TransparencyAttrib.MDual)
            self.piano.setTwoSided(True)
            self.accept("space", self.space_pressed)

            if os.path.exists(TEXTURE_DIR):
                self.piano.clearTexture()
                self.piano.setTextureOff(False)
                print("🎨 Textures automatiques conservées depuis le dossier .dae.")
            else:
                print("⚠️ Aucun dossier 'textures' détecté à côté de model.dae")

            self.setup_lighting()
            self.color_keys_manually()
            self.disable_interaction_with_pCube1()
            self.note_length = 0.4  # longueur par défaut
            self.note_spawn_distance = 10  # distance de spawn initiale (axe Y)
            self.note_speed = 0.15  # vitesse initiale des notes
            self.create_buttons()
            self.create_dropdown_menu()
            self.setup_click_detection()

            self.disableMouse()
            self.accept("space", self.check_key_click)
            self.taskMgr.add(self.update_camera_task, "UpdateCameraTask")
            self.taskMgr.add(self.update_movement_task, "UpdateMovementTask")

            self.mouseWatcher = self.mouseWatcherNode
            self.is_mouse_down = False
            self.last_mouse_x = 0
            self.last_mouse_y = 0
            self.keys_pressed = {}
            self.accept("mouse1", self.on_mouse_press)
            self.accept("mouse1-up", self.on_mouse_release)
            self.accept("wheel_up", self.zoom_in)
            self.accept("wheel_down", self.zoom_out)

            self.movement_keys = {"z": False, "s": False, "q": False, "d": False, "a": False, "e": False}
            for key in self.movement_keys:
                self.accept(key, self.set_movement, [key, True])
                self.accept(key + "-up", self.set_movement, [key, False])

            self.speed = 0.18
            self.camera_distance = 10
            self.adjust_camera()
            self.active_notes = []


        def space_pressed(self):
            print("Barre d'espace pressée")

        def play_sound_for_key(self, key_name):
            if self.music_enabled and key_name in self.sounds:
                volume = self.get_global_volume()
                sound = self.sounds[key_name]
                sound.set_volume(volume)
                print(f"🔊 Lecture de {key_name} à volume {volume:.2f}")

                channel = pygame.mixer.find_channel(True)
                if channel:
                    channel.play(sound)
                else:
                    print(f"❌ Aucun canal libre pour jouer {key_name}")
            else:
                print(f"❌ Aucun son associé à {key_name} ou musique désactivée")

        def color_keys_manually(self):
            black_keys = ["pCube1", "pCube33", "pCube52", "pCube53", "pCube54", "pCube55", "pCube56", "pCube57", "pCube58", "pCube59", "pCube60"]
            white_keys = ["pCube40", "pCube51", "pCube45", "pCube44", "pCube48", "pCube50", "pCube43", "pCube47", "pCube49", "pCube42", "pCube41", "pCube46", "pCube6", "pCube10", "pCube2"]
            all_keys = black_keys + white_keys

            for key_name in all_keys:
                key = self.piano.find(f"**/{key_name}")
                if not key.isEmpty():
                    if key_name in black_keys:
                        key.setColor((0, 0, 0, 1), 1)
                        key.setTag("black_key", "true")
                    else:
                        key.setColor((1, 1, 1, 1), 1)
                        key.setTag("white_key", "true")
                    key.setTransparency(False)
                    key.setTwoSided(True)
                    if key_name != "pCube1":
                        key.node().setIntoCollideMask(0x10)
                    else:
                        key.node().setIntoCollideMask(0)
                    key.setName(key_name)

        def disable_interaction_with_pCube1(self):
            key = self.piano.find("**/pCube1")
            if not key.isEmpty():
                key.node().setIntoCollideMask(0)
                print("🔒 Interaction désactivée pour pCube1")

        def create_dropdown_menu(self):
            self.black_keys = ["pCube33", "pCube52", "pCube53", "pCube54", "pCube55", "pCube56", "pCube57", "pCube58", "pCube59", "pCube60"]
            self.white_keys = ["pCube40", "pCube51", "pCube45", "pCube44", "pCube48", "pCube50", "pCube43", "pCube47", "pCube49", "pCube42", "pCube41", "pCube46", "pCube6", "pCube10", "pCube2"]
            
            self.special_keys = self.black_keys + self.white_keys  # Inclut toutes les touches accessibles dans le menu
            self.option_menu = DirectOptionMenu(
                text="Textures",
                scale=0.08,
                items=self.special_keys,
                initialitem=0,
                highlightColor=(0.65, 0.65, 0.65, 1),
                command=self.spawn_note_to_selected
            )
            self.option_menu.setPos(-1.3, 0, 0.9)
            self.latest_selected_key = self.special_keys[0]



        def spawn_note_to_selected(self, selected_key):
            self.latest_selected_key = selected_key
            print(f"🔁 Total notes actives : {len(self.active_notes)}")
            print(f"🧱 Note créée depuis bouton : {self.latest_selected_key}")



        def spawn_note_button_clicked(self):
            if hasattr(self, 'latest_selected_key'):
                key_name = self.latest_selected_key
                key_node = self.piano.find(f"**/{key_name}")
                is_black = key_node.hasNetTag("black_key")
                note = Note(self, key_name, is_special=is_black)
                self.active_notes.append(note)
                print(f"🧱 Généré vers {key_name} | Couleur: {'noire' if is_black else 'blanche'}")

        def create_buttons(self):
            self.spawn_button = DirectButton(
                text="Générer Note",
                scale=0.07,
                pos=(-1.3, 0, 0.75),
                command=self.spawn_note_button_clicked
            )

            self.spawn_distance_slider = DirectSlider(
                range=(1.0, 50.0),
                value=self.note_spawn_distance,
                pageSize=1.0,
                scale=0.8,
                pos=(0.2, 0, 0.85),
                command=self.update_spawn_distance,
                extraArgs=[]
            )
            
            self.speed_slider = DirectSlider(
                range=(0.05, 1.0),
                value=self.note_speed,
                pageSize=0.01,
                scale=0.8,
                pos=(0.2, 0, 0.75),
                command=self.update_note_speed,
                extraArgs=[]
            )

            self.music_button = DirectButton(
                text="Activer/Désactiver Musique",
                scale=0.07,
                pos=(-1.3, 0, 0.65),
                command=self.toggle_music  # Appelle la méthode pour changer l'état de la musique
            )

            self.speed_label = DirectLabel(
                text=f"Vitesse des notes : {self.note_speed:.2f}",
                scale=0.05,
                pos=(0.2, 0, 0.83)
            )

            self.slider_label = DirectLabel(
                text=f"Distance de spawn : {self.note_spawn_distance:.1f}",
                scale=0.05,
                pos=(0.2, 0, 0.95)
            )


        def update_spawn_distance(self):
            self.note_spawn_distance = float(self.spawn_distance_slider['value'])
            self.slider_label["text"] = f"Distance de spawn : {self.note_spawn_distance:.1f}"
        
        def update_note_speed(self):
            self.note_speed = float(self.speed_slider['value'])
            self.speed_label["text"] = f"Vitesse des notes : {self.note_speed:.2f}"

        def setup_lighting(self):
            ambient_light = AmbientLight("ambient_light")
            ambient_light.setColor((0.5, 0.5, 0.5, 1))
            self.render.setLight(self.render.attachNewNode(ambient_light))

            directional_light = DirectionalLight("directional_light")
            directional_light.setColor((1, 1, 1, 1))
            light_node = self.render.attachNewNode(directional_light)
            light_node.setHpr(45, -45, 0)
            self.render.setLight(light_node)

        def adjust_camera(self):
            bounds = self.piano.getTightBounds()
            if bounds:
                min_b, max_b = bounds
                center = (min_b + max_b) / 2
                size = max_b - min_b
                distance = max(size) * 2
                self.camera.setPos(center.x, center.y - distance, center.z)
                self.camera.lookAt(center)

        def toggle_music(self):
            self.music_enabled = not self.music_enabled
            print("Musique activée" if self.music_enabled else "Musique désactivée")

        def setup_click_detection(self):
            self.pickerNode = CollisionNode('mouseRay')
            self.pickerNP = self.camera.attachNewNode(self.pickerNode)
            self.pickerRay = CollisionRay()
            self.pickerNode.addSolid(self.pickerRay)
            self.pickerNode.setFromCollideMask(0x10)
            self.pickerNode.setIntoCollideMask(0)
            self.pickerQueue = CollisionHandlerQueue()
            self.cTrav.addCollider(self.pickerNP, self.pickerQueue)

        def check_key_click(self):
            if self.mouseWatcherNode.hasMouse():
                mpos = self.mouseWatcherNode.getMouse()
                self.pickerRay.setFromLens(self.camNode, mpos.getX(), mpos.getY())
                self.cTrav.traverse(self.render)

                if self.pickerQueue.getNumEntries() > 0:
                    self.pickerQueue.sortEntries()
                    pickedObj = self.pickerQueue.getEntry(0).getIntoNodePath()
                    if pickedObj.hasNetTag("black_key") or pickedObj.hasNetTag("white_key"):
                        key_name = pickedObj.getName()
                        key_node = self.piano.find(f"**/{key_name}")

                        key_center = key_node.getBounds().getCenter()
                        key_center = key_node.getParent().getMat(self.render).xformPoint(key_center)

                        print(f"✅ Touche pressée : {key_name}")
                        self.play_sound_for_key(key_name)
                        if key_center is not None:
                            print(f"📍 Position touche : {key_center}")


                        pickedObj.setColor((1, 0, 0, 1), 1)
                        self.taskMgr.doMethodLater(0.3, self.reset_color, "resetKeyColor", extraArgs=[pickedObj], appendTask=False)


        def reset_color(self, node):
            if node:
                if node.hasNetTag("black_key"):
                    node.setColor((0, 0, 0, 1), 1)
                elif node.hasNetTag("white_key"):
                    node.setColor((1, 1, 1, 1), 1)

        def print_camera_info(self):
            print(f"Camera Pos: {self.camera.getPos()} | HPR: {self.camera.getHpr()}")

        def on_mouse_press(self):
            if self.mouseWatcher.hasMouse():
                self.is_mouse_down = True
                self.last_mouse_x = self.mouseWatcher.getMouseX()
                self.last_mouse_y = self.mouseWatcher.getMouseY()

        def on_mouse_release(self):
            self.is_mouse_down = False

        def update_camera_task(self, task):
            if self.is_mouse_down and self.mouseWatcher.hasMouse():
                new_x = self.mouseWatcher.getMouseX()
                new_y = self.mouseWatcher.getMouseY()
                delta_x = (new_x - self.last_mouse_x) * 100
                delta_y = (new_y - self.last_mouse_y) * 100
                self.camera.setH(self.camera.getH() - delta_x)
                self.camera.setP(self.camera.getP() + delta_y)
                self.last_mouse_x = new_x
                self.last_mouse_y = new_y
            return Task.cont

        def zoom_in(self):
            self.camera.setY(self.camera, 0.2)

        def zoom_out(self):
            self.camera.setY(self.camera, -0.2)

        def set_movement(self, key, value):
            self.movement_keys[key] = value

        def update_movement_task(self, task):
            if self.movement_keys["z"]:
                self.camera.setY(self.camera, self.speed)
            if self.movement_keys["s"]:
                self.camera.setY(self.camera, -self.speed)
            if self.movement_keys["q"]:
                self.camera.setX(self.camera, -self.speed)
            if self.movement_keys["d"]:
                self.camera.setX(self.camera, self.speed)
            if self.movement_keys["a"]:
                self.camera.setZ(self.camera, self.speed)
            if self.movement_keys["e"]:
                self.camera.setZ(self.camera, -self.speed)
            return Task.cont
        

        
        def check_hit(self, key_name):
            print(f"✅ check_hit appelé pour {key_name}")
            return True
        
if __name__ == "__main__":
        app = PianoViewer()
        app.run()