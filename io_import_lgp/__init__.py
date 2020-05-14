bl_info = {
    "name": "Final Fantasy 7 LGP format",
    "author": "Sébastien Dougnac",
    "blender": (2, 82, 0),
    "location": "File > Import-Export",
    "description": "Import-Export LGP models and animations",
    "warning": "",
    "support": 'TESTING',
    "category": "Import-Export"
}

import bpy
import math
from mathutils import Matrix, Quaternion

class HRCBone:
    def __init__(self, name, parent, length, animations, textures):
        self.name = name
        self.parent = parent
        self.length = length
        self.animations = animations
        self.textures = textures
        
    @property
    def name(self):
        return self.__name
        
    @name.setter
    def name(self, name):
        self.__name = name
        
    @property
    def parent(self):
        return self.__parent
        
    @parent.setter
    def parent(self, parent):
        self.__parent = parent
        
    @property
    def length(self):
        return self.__length
        
    @length.setter
    def length(self, length):
        self.__length = length
        
    @property
    def animations(self):
        return self.__animations
        
    @animations.setter
    def animations(self, animations):
        self.__animations = animations
    
    @property
    def textures(self):
        return self.__textures
        
    @textures.setter
    def textures(self, textures):
        self.__textures = textures

class HRCSkeleton:
    def __init__(self, name, nb_bones):
        self.name = name
        self.nb_bones = nb_bones
        self.bones = {}
    
    @property
    def name(self):
        return self.__name
    
    @name.setter
    def name(self, name):
        self.__name = name
        
    @property
    def nb_bones(self):
        return self.__nb_bones
    
    @nb_bones.setter
    def nb_bones(self, nb_bones):
        self.__nb_bones = nb_bones if nb_bones > 0 else 1 # Default number of bones is 1
        
    @property
    def bones(self):
        return self.__bones
        
    @bones.setter
    def bones(self, bones):
        self.__bones = bones
        
    def getBone(self, name):
        return self.bones[name]
        
    def addBone(self, bone):
        self.bones[bone.name] = bone
        
def ff7RotationToQuaternion(x_angle, y_angle, z_angle):
    # FF7 works with a -Y-Up coordinate system
    # Blender is using a +Z-Up coordinate system
    # So we need to switch Y and Z angles and use a negative angle as Y
    quat_x = Quaternion((1.0, 0.0, 0.0), math.radians(x_angle))
    quat_y = Quaternion((0.0, 1.0, 0.0), -math.radians(z_angle))
    quat_z = Quaternion((0.0, 0.0, 1.0), math.radians(y_angle))
    
    # FF7 rotation order is YXZ, which becomes ZXY in Blender
    quaternion = quat_z @ quat_x @ quat_y
    
    return quaternion

def import_lgp(context, filepath):
    # Loading Python objects (do not put Blender related stuff in there)
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
        
    skeleton = HRCSkeleton(lines[1].split(" ")[1], int(lines[2].split(" ")[1]))
    newBone = True
    for rownum, line in enumerate(lines[3:], start=3): # Starting right after the header
        if line[:1] == "#": # No use of comments
            pass
        elif not line.strip(): # Empty lines mark the arrival of a new bone next line
            newBone = True
        elif newBone: # First line of a new bone
            name = lines[rownum]
            parent = lines[rownum+1]
            length = float(lines[rownum+2])
            rsd = lines[rownum+3].split(maxsplit=1)
            if int(rsd[0]) > 0:
                rsd_files = rsd[1].split()
            else:
                rsd_files = None
            bone = HRCBone(name, parent, length, None, None)
            skeleton.addBone(bone)
            newBone = False
        else: # Line within a bone, already taken into account when we encountered the first one
            pass

    # Now we have all needed objects, we can work in Blender
    # Adding a new Scene per skeleton
    scene = bpy.data.scenes.new(skeleton.name)
    bpy.context.window.scene = scene
    view_layer = bpy.context.view_layer
    # Adding armature to the scene
    armature_data = bpy.data.armatures.new(name="root") # The Armature will represent the root bone for transformation purposes
    armature_obj = bpy.data.objects.new(name="Cloud's skeleton", object_data=armature_data)
    view_layer.active_layer_collection.collection.objects.link(armature_obj)
    armature_obj.select_set(True)
    view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode="EDIT")
    armature_obj.rotation_mode = "QUATERNION"
    # Defining root rotation
    armature_obj.rotation_quaternion = ff7RotationToQuaternion(0.0, 0.0, 0.0) # TODO : Remove this and put real values
    # Adding bones to armature
    edit_bones = armature_data.edit_bones
    for bone in skeleton.bones.values():
        parent_name = skeleton.bones[bone.name].parent
        cur_bone = edit_bones.new(bone.name)
        cur_bone.length = skeleton.bones[bone.name].length
        if parent_name != "root":
            cur_bone.translate(edit_bones[parent_name].tail)
            cur_bone.parent = edit_bones[parent_name]
            cur_bone.use_connect = True
    view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode="OBJECT") # Used to validate the Edit mode stuff. Not sure if really needed
    # Defining bones' rotations
    bpy.ops.object.mode_set(mode="POSE")
    for poseBone in armature_obj.pose.bones: # TODO : Remove hardcoded values
        if poseBone.name == "hip":
            poseBone.rotation_quaternion = ff7RotationToQuaternion(270.0,0.0,0.0) # TODO : Remove this and put real values
        elif poseBone.name == "chest":
            poseBone.rotation_quaternion = ff7RotationToQuaternion(352.5625,0.0,356.0) # TODO : Remove this and put real values
        elif poseBone.name == "head":
            poseBone.rotation_quaternion = ff7RotationToQuaternion(13.4375,0.0,3.0) # TODO : Remove this and put real values
        elif poseBone.name == "l_chest":
            poseBone.rotation_quaternion = ff7RotationToQuaternion(347.0,324.84375,77.34375) # TODO : Remove this and put real values
        elif poseBone.name == "l_collar":
            poseBone.rotation_quaternion = ff7RotationToQuaternion(306.0,317.0,22.0) # TODO : Remove this and put real values
        elif poseBone.name == "l_uparm":
            poseBone.rotation_quaternion = ff7RotationToQuaternion(301.0,44.0,45.0) # TODO : Remove this and put real values
        elif poseBone.name == "l_foarm":
            poseBone.rotation_quaternion = ff7RotationToQuaternion(347.343811035156,0.0,0.0) # TODO : Remove this and put real values
        elif poseBone.name == "l_hand":
            poseBone.rotation_quaternion = ff7RotationToQuaternion(0.0,0.0,0.0) # TODO : Remove this and put real values
        elif poseBone.name == "r_chest":
            poseBone.rotation_quaternion = ff7RotationToQuaternion(350.15625,35.15625,282.65625) # TODO : Remove this and put real values
        elif poseBone.name == "r_collar":
            poseBone.rotation_quaternion = ff7RotationToQuaternion(303.75,30.9375,324.84375) # TODO : Remove this and put real values
        elif poseBone.name == "r_uparm":
            poseBone.rotation_quaternion = ff7RotationToQuaternion(289.0,37.9687995910645,229.218795776367) # TODO : Remove this and put real values
        elif poseBone.name == "r_foarm":
            poseBone.rotation_quaternion = ff7RotationToQuaternion(341.718811035156,0.0,0.0) # TODO : Remove this and put real values
        elif poseBone.name == "r_hand":
            poseBone.rotation_quaternion = ff7RotationToQuaternion(0.0,0.0,0.0) # TODO : Remove this and put real values
        elif poseBone.name == "l_hip":
            poseBone.rotation_quaternion = ff7RotationToQuaternion(0.0,251.71875,180.0) # TODO : Remove this and put real values
        elif poseBone.name == "l_femur":
            poseBone.rotation_quaternion = ff7RotationToQuaternion(298.125,255.9375,175.781295776367) # TODO : Remove this and put real values
        elif poseBone.name == "l_tibia":
            poseBone.rotation_quaternion = ff7RotationToQuaternion(12.6562004089355,0.0,0.0) # TODO : Remove this and put real values
        elif poseBone.name == "l_foot":
            poseBone.rotation_quaternion = ff7RotationToQuaternion(275.625,340.3125,22.5) # TODO : Remove this and put real values
        elif poseBone.name == "r_hip":
            poseBone.rotation_quaternion = ff7RotationToQuaternion(0.0,108.28125,180.0) # TODO : Remove this and put real values
        elif poseBone.name == "r_femur":
            poseBone.rotation_quaternion = ff7RotationToQuaternion(296.718811035156,289.6875,0.0) # TODO : Remove this and put real values
        elif poseBone.name == "r_tibia":
            poseBone.rotation_quaternion = ff7RotationToQuaternion(23.9062004089355,0.0,0.0) # TODO : Remove this and put real values
        elif poseBone.name == "r_foot":
            poseBone.rotation_quaternion = ff7RotationToQuaternion(270.0,177.1875,180.0) # TODO : Remove this and put real values
    view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode="OBJECT")
            
    return {'FINISHED'}

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

class ImportLGP(Operator, ImportHelper):
    """Import from LGP file format (.lgp)"""
    bl_idname = "import_lgp.import_scenes"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import LGP"

    # ImportHelper mixin class uses this
    filename_ext = ".lgp"

    filter_glob: StringProperty(
        default="*.hrc", # TODO : Change this to LGP
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        return import_lgp(context, self.filepath)


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportLGP.bl_idname, text="LGP files (.lgp)")


def register():
    bpy.utils.register_class(ImportLGP)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportLGP)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.import_lgp.import_scenes('INVOKE_DEFAULT')
