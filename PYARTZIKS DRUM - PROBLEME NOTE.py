from direct.showbase.ShowBase import ShowBase
from panda3d.core import Filename, AmbientLight, DirectionalLight, Vec4, loadPrcFileData, CollisionTraverser, CollisionNode, CollisionRay, CollisionHandlerQueue, TransparencyAttrib, NodePath , LVector3, CollisionSphere , CollisionSphere, CollisionHandlerEvent  
from direct.task import Task
from direct.gui.DirectGui import DirectButton
import os

class Note:
        def __init__(self, game, target_name):
            self.game = game
            self.target_name = target_name

                
            self.model = self.game.loader.loadModel("models/misc/rgbCube")
            self.model.setScale(0.3)
            self.model.reparentTo(self.game.render)

                
            drum_pos = self.game.drum.getPos(self.game.render)

                
            self.spawn_distance = 5  

            target_node = self.game.drum.find(f"**/Circle.120")
            if target_node.isEmpty():
                print(f"⚠️ Problème : {self.target_name} non trouvé !")
                return  

            if target_node and not target_node.isEmpty():
                self.target_pos = target_node.getPos(self.game.render)  
                print(f"📍 Position exacte de Circle.120: {self.target_pos}")
            else:
                print("⚠️ Erreur : Impossible de récupérer Circle.120 !")
                self.target_pos = LVector3(0, 0, 0)  

            print(f"📍 Position cible détectée pour {self.target_name}: {self.target_pos}")

            self.next_target_pos = self.target_pos + (self.target_pos - self.game.drum.getPos(self.game.render)) * 0.5  

            self.game.taskMgr.add(self.update, "MoveNoteTask")

                
            if target_node and not target_node.isEmpty():
                local_pos = target_node.getPos()
                world_pos = target_node.getPos(self.game.render)
                matrix_pos = target_node.getMat(self.game.render).getRow3(3)
            else:
                print(f"❌ Impossible d'obtenir les positions : {self.target_name} introuvable !")
                local_pos = world_pos = matrix_pos = LVector3(0, 0, 0)  

            print(f"🔎 Local Position: {local_pos}, World Position: {world_pos}, Matrix Position: {matrix_pos}")

                
            start_x = self.target_pos.x
            start_y = self.target_pos.y
            start_z = self.target_pos.z + 1.5  
            print(f"📍 Position cible détectée pour {self.target_name}: {self.target_pos}")
            start_x = drum_pos.x
            start_y = drum_pos.y
            start_z = drum_pos.z + 1.5

          
            self.model.setPos(start_x, start_y, start_z)
            print(f"🚀 Spawn de la note {self.target_name} à {self.model.getPos(self.game.render)}, cible : {self.target_pos}")
            print(f"🟡 Nouvelle note créée pour {self.target_name}")
            print(f"   - Position cible : {self.target_pos}")
            print(f"   - Position initiale : {self.model.getPos(self.game.render)}")
            print(f"📌 Note créée - Spawn: {self.model.getPos()} -> Cible: {self.target_pos}")

            if target_node and not target_node.isEmpty():
                bounds = target_node.getBounds()
                
                if bounds.isEmpty():
                    self.target_pos = LVector3(0, 0, 0)
                    if self.target_pos == LVector3(0, 0, 0):
                        print(f"⚠️ Alerte : Position cible invalide pour {self.target_name}, recalcul en cours...")
                        self.target_pos = self.game.drum.getPos(self.game.render) + LVector3(0, 0, 1.5)
                    print(f"📍 Position cible détectée pour {self.target_name}: {self.target_pos}")
                    print(f"⚠️ [ACTION] Bounding Box VIDE pour {self.target_name} ! Vérifier le modèle 3D.")
                else:
                    self.target_pos = bounds.getCenter()
                    print(f"📍 Position cible détectée pour {self.target_name}: {self.target_pos}")
                    print(f"📍 [ACTION] Bounding Box trouvée pour {self.target_name}, Position: {self.target_pos}")

            else:
                self.target_pos = LVector3(0, 0, 0)
                print(f"📍 Position cible détectée pour {self.target_name}: {self.target_pos}")
                print(f"❌ [ACTION] ERREUR : Cible {self.target_name} introuvable !")

                
            self.speed = 0.15  


            self.setup_collision()

                
            self.game.taskMgr.add(self.update, "MoveNoteTask")

        def setup_collision(self):
            coll_sphere = CollisionSphere(0, 0, 0, 0.3) 
            coll_node = CollisionNode(f"note_{self.target_name}")
            coll_node.addSolid(coll_sphere)
            coll_node.setFromCollideMask(0x10)
            coll_node.setIntoCollideMask(0)
            coll_np = self.model.attachNewNode(coll_node)

            
            self.game.cTrav.addCollider(coll_np, self.game.collision_handler)
            self.game.collision_handler.addInPattern('note-hit-%in')

            self.game.accept(f'note-hit-{coll_node.getName()}', self.hit_target)

        def update(self, task):

            current_pos = self.model.getPos(self.game.render)

            if not hasattr(self, "target_pos") or self.target_pos is None:
                print(f"❌ Erreur : target_pos non définie pour {self.target_name}. Annulation de l'update.")
                return task.done

            if current_pos is None:
                print(f"❌ Erreur : current_pos non définie pour {self.target_name}. Annulation de l'update.")
                return task.done

            
            if isinstance(self.target_pos, LVector3):
                target_position = self.target_pos
            else:
                target_position = LVector3(self.target_pos)

            cube_position = LVector3(current_pos)  
            distance_restante = (target_position - cube_position).length()

            
            collision_tolerance = 0.1  
            if distance_restante < collision_tolerance:
                print(f"✅ Note {self.target_name} a atteint la cible initiale {self.target_pos} !")
                self.target_pos = self.next_target_pos  
                print(f"🎯 Nouvelle cible définie pour {self.target_name}: {self.target_pos}")

            
            direction = (self.target_pos - cube_position)

            if direction.length() > 0:  
                direction.normalize()

            movement_vector = direction * self.speed
            new_pos = cube_position + movement_vector

            self.model.setPos(new_pos)

            print(f"🔄 Déplacement de {self.target_name}: Actuel {new_pos}, Cible {self.target_pos}")
            print(f"📏 Distance restante: {(self.target_pos - new_pos).length()}")

            return task.cont





        def hit_target(self):
            print(f"🎯 Note confirmée en collision : {self.target_name} !")
            
            if self in self.game.active_notes:
                self.game.active_notes.remove(self)  
                result = self.game.check_hit(self.target_name)  

            if result:
                print(f" Succès ! Note bien tapée sur {self.target_name} !")
                self.model.removeNode()
                self.game.taskMgr.remove("MoveNoteTask") 
            else:
                print(f" Vérification du timing... Note sur {self.target_name} détectée mais timing incorrect.")   

class DrumViewer(ShowBase):
        def __init__(self):
            print(" Test: Écoute des événements en cours...")

            loadPrcFileData("", "window-title PYARTZIKS - Batterie - Sandbox")
            loadPrcFileData("", "icon-filename logo.ico")
            
            super().__init__()

            self.score = 0
            self.cTrav = CollisionTraverser()
            self.collision_handler = CollisionHandlerEvent()
            self.collision_handler.addInPattern('%fn-into-%in')

            SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
            MODEL_DIR = os.path.join(SCRIPT_DIR, "modele 3D")
            MODEL_PATH = os.path.join(MODEL_DIR, "drum model2.obj")

            if not os.path.exists(MODEL_PATH):
                print(f"Erreur : le fichier {MODEL_PATH} n'existe pas.")
                return

            self.drum = self.loader.loadModel(Filename.fromOsSpecific(MODEL_PATH))
            if not self.drum:
                print("Erreur : Impossible de charger le modèle 3D.")
                return

            print("Modèle chargé avec succès !")

            self.drum.reparentTo(self.render)
            self.drum.setScale(2, 2, 2)
            self.drum.setPos(0, 0, 0)
            self.remove_specific_cymbal()
            print("Appel de color_parts_manually()")
            self.color_parts_manually()

            
            self.drum.setTextureOff(False)
            self.drum.reparentTo(self.render)
            self.drum.setScale(2, 2, 2) 
            self.drum.setPos(0, 0, 0)

            ambient_light = AmbientLight("ambient_light")
            ambient_light.setColor((0.5, 0.5, 0.5, 1))
            self.render.setLight(self.render.attachNewNode(ambient_light))

            directional_light = DirectionalLight("directional_light")
            directional_light.setColor((1, 1, 1, 1))
            light_node = self.render.attachNewNode(directional_light)
            light_node.setHpr(45, -45, 0)
            self.render.setLight(light_node)
            self.disableMouse()
            self.accept("space", self.check_black_click)  
            self.adjust_camera_to_fit_model()
            self.taskMgr.add(self.update_camera_task, "UpdateCameraTask")
            self.taskMgr.add(self.update_movement_task, "UpdateMovementTask")

            self.mouseWatcher = self.mouseWatcherNode
            self.is_mouse_down = False
            self.last_mouse_x = 0
            self.last_mouse_y = 0
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
            self.adjust_camera_to_fit_model()
            self.color_cymbals_black()

            self.cTrav = CollisionTraverser()
            self.pickerNode = CollisionNode('mouseRay')
            self.pickerNP = self.camera.attachNewNode(self.pickerNode)
            self.pickerRay = CollisionRay()
            self.pickerNode.addSolid(self.pickerRay)
            self.pickerNode.setFromCollideMask(0x10)
            self.pickerNode.setIntoCollideMask(0) 
            self.pickerQueue = CollisionHandlerQueue()
            self.cTrav.addCollider(self.pickerNP, self.pickerQueue)
            self.create_buttons()
            self.active_notes = []

        
        def create_buttons(self):
            button_scale = 0.07 
            button_x = -1.3  
            button_y_start = 0.9  
            self.button1 = DirectButton(text="a", scale=button_scale, pos=(button_x, 0, button_y_start),
                                    command=self.a)
            self.button2 = DirectButton(text="b", scale=button_scale, pos=(button_x, 0, button_y_start - 0.15),
                                    command=self.b)
            self.button3 = DirectButton(text="c", scale=button_scale, pos=(button_x, 0, button_y_start - 0.30),
                                    command=self.c)
            self.button4 = DirectButton(text="d", scale=button_scale, pos=(button_x, 0, button_y_start - 0.45),
                                    command=self.d)
            self.button5 = DirectButton(text="e", scale=button_scale, pos=(button_x, 0, button_y_start - 0.60),
                                    command=self.e)
            self.button6 = DirectButton(text="f", scale=button_scale, pos=(button_x, 0, button_y_start - 0.75),
                                    command=self.f)
            self.button7 = DirectButton(text="g", scale=button_scale, pos=(button_x, 0, button_y_start - 0.90),
                                    command=self.g)
            
        def a(self):
            note = Note(self, "Circle.120")  
            self.active_notes.append(note)
        def b(self):
            note = Note(self, "Circle.401")  
            self.active_notes.append(note)
        def c(self):
            note = Note(self, "Circle.402")  
            self.active_notes.append(note)
        def d(self):
            note = Note(self, "Circle.403")  
            self.active_notes.append(note)
        def e(self):
            note = Note(self, "Circle.405")  
            self.active_notes.append(note)
        def f(self):
            note = Note(self, "Circle.406")  
            self.active_notes.append(note)
        def g(self):
            note = Note(self, "Circle.408")  
            self.active_notes.append(note)
        

        def adjust_camera_to_fit_model(self):
            bounds = self.drum.getTightBounds()
            if bounds:
                min_b, max_b = bounds
                center = (min_b + max_b) / 2
                size = max_b - min_b
                distance = max(size) * 2
                self.camera.setPos(center.x, center.y - distance, center.z)
                self.camera.lookAt(center)
                self.camera_distance = distance
                self.camera_center = center

        
        

        def color_cymbals_black(self):
            cymbals = ["Circle.120", "Circle.401", "Circle.402",
                "Circle.403", "Circle.405", "Circle.406", "Circle.408"]

            for cymbal_name in cymbals:
                nodes = self.drum.findAllMatches(f"**/{cymbal_name}*")
                if nodes.isEmpty():
                    print(f"{cymbal_name} non trouvée.")
                else:
                    for node in nodes:
                        node.setColor((0, 0, 0, 1), 1)
                        node.setTransparency(False)
                        node.setTwoSided(True)
                        node.setTag("black_cymbal", "true")  
                        node.node().setIntoCollideMask(0x10)  
                        print(f"{cymbal_name} colorée en noir, taggée et prête pour la détection.")

            self.drum.setTransparency(False)
            self.drum.setTwoSided(True)

        def color_parts_manually(self):
            parts_colors = {
                "Circle": {"color": (0.8, 0.8, 0.8, 1), "name": "Gris clair"},
                "Bolt": {"color": (0.7, 0.7, 0.7, 1), "name": "Gris clair"},
                "Cube": {"color": (0.6, 0.6, 0.6, 1), "name": "Gris foncé"},
                "Cylinder": {"color": (0.5, 0.5, 0.5, 1), "name": "Gris très foncé"},
                "Floor_Shell_1": {"color": (0.3, 0.3, 0.3, 1), "name": "Charbon"},
                "Shell1": {"color": (0.9, 0.9, 0.9, 1), "name": "Coque gris clair"},
                "Plane": {"color": (0.5, 0.5, 0.5, 1), "name": "Gris moyen"}
            }
            for part_name, color_info in parts_colors.items():
                nodes = self.drum.findAllMatches(f"**/{part_name}*")
                if nodes.isEmpty():
                    print(f" Partie '{part_name}' non trouvée.")
                else:
                    for node in nodes:
                        node.setColor(color_info["color"], 1)
                        node.setTwoSided(True)
                        node.setTransparency(False)  
                        print(f" '{node.getName()}' colorée avec {color_info['name']}.")
            cymbal_name = "Circle.397"
            nodes = self.drum.findAllMatches(f"**/{cymbal_name}*")
            if not nodes.isEmpty():
                for node in nodes:
                    node.setColor((0, 0, 0, 1))  
                    node.setTransparency(False)  
                    node.setTwoSided(True)  
                    print(f" '{node.getName()}' colorée en noir.")  
            else:
                print(f"Partie '{cymbal_name}' non trouvée.")

        def remove_specific_cymbal(self):
            cymbal_name = "Circle.397"  
            nodes = self.drum.findAllMatches(f"**/{cymbal_name}*")

            if nodes.isEmpty():
                print(f"Partie '{cymbal_name}' non trouvée.")
            else:
                for node in nodes:
                    if node.isEmpty():  
                        print(f" Le node '{cymbal_name}' est déjà vide, impossible de le supprimer.")
                        continue  

                    try:
                        
                        if node:
                            print(f"Suppression de '{node.getName()}' de la scène...")
                            node.removeNode()  
                            print(f" '{node.getName()}' a été supprimée de la scène.")
                        else:
                            print(f" Node pour '{cymbal_name}' est invalide ou déjà supprimé.")
                    except Exception as e:
                        
                        print(f" Impossible de supprimer '{cymbal_name}': {e}")





        def check_hit(self, cymbal_name):
            for note in self.active_notes:
                if note.target_name == cymbal_name:
                    distance = (note.model.getPos() - note.target_pos).length()
                    if distance < 1:  
                        print(f"Parfait ! Note sur {cymbal_name} bien tapée !")
                        self.score += 10
                        note.model.removeNode()
                        self.active_notes.remove(note)
                        return
                    elif distance < 2:  
                        print(f" Correct ! Note sur {cymbal_name} mais timing moyen.")
                        self.score += 5
                        note.model.removeNode()
                        self.active_notes.remove(note)
                        return
            print(" Raté ! Mauvais timing ou mauvaise touche.")



        def check_black_click(self):
            print(" Barre espace appuyée - Vérification de la position de la souris...")

            if self.mouseWatcherNode.hasMouse():
                mpos = self.mouseWatcherNode.getMouse()
                print(f" Position de la souris : {mpos}")

                self.pickerRay.setFromLens(self.camNode, mpos.getX(), mpos.getY())
                self.cTrav.traverse(self.render)
                print(f"Nombre d'objets détectés par le rayon : {self.pickerQueue.getNumEntries()}")

                if self.pickerQueue.getNumEntries() > 0:
                    self.pickerQueue.sortEntries()
                    pickedObj = self.pickerQueue.getEntry(0).getIntoNodePath()
                    print(f" Objet détecté sous la souris : {pickedObj}")

                    if pickedObj.hasNetTag("black_cymbal"):
                        pos = pickedObj.getBounds().getCenter()
                        print(f"📍 Coordonnées (Bounding Box) : X={pos.x}, Y={pos.y}, Z={pos.z}")

                        print("Partie noire cliquée ! Changement de couleur en rouge pour 0.5s.")
                        pickedObj.setColor((1, 0, 0, 1), 1)  
                        self.taskMgr.doMethodLater(0.5, self.reset_cymbal_color, "ResetCymbalColor", extraArgs=[pickedObj], appendTask=False)
                        return
            
                print(" Aucun objet noir détecté.")
            else:
                print(" La souris n'est pas détectée !")


        def reset_cymbal_color(self, cymbal):
            if cymbal:
                cymbal_name = cymbal.getName()  
                print(f"Retour à la couleur noire. ID de la cymbale : {cymbal_name}")
                cymbal.setColor((0, 0, 0, 1), 1)  
    
        
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

app = DrumViewer()
app.run()
