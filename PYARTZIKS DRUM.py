from direct.showbase.ShowBase import ShowBase
from panda3d.core import Filename, AmbientLight, DirectionalLight, Vec4, loadPrcFileData, CollisionTraverser, CollisionNode, CollisionRay, CollisionHandlerQueue
from direct.task import Task
import os

class DrumViewer(ShowBase):
    def __init__(self):
        print(" Test: Écoute des événements en cours...")
        self.accept("mouse1", lambda: print(" Événement `mouse1` détecté !"))

        loadPrcFileData("", "window-title PYARTZIKS - Batterie - Sandbox")
        loadPrcFileData("", "icon-filename logo.ico")
        
        super().__init__()

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

        self.speed = 0.2
        self.camera_distance = 10
        self.adjust_camera_to_fit_model()
        self.color_cymbals_black()

        self.cTrav = CollisionTraverser()
        self.pickerNode = CollisionNode('mouseRay')
        self.pickerNP = self.camera.attachNewNode(self.pickerNode)
        self.pickerRay = CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)
        self.pickerNode.setFromCollideMask(0x10)  
        self.pickerQueue = CollisionHandlerQueue()
        self.cTrav.addCollider(self.pickerNP, self.pickerQueue)
        

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
        cymbals = ["Circle.120", "Circle.397", "Circle.401", "Circle.402",
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
                    print("Partie noire cliquée !")
                    return
        
            print(" Aucun objet noir détecté.")
        else:
            print(" La souris n'est pas détectée !")

    
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
