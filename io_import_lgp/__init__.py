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
import os
from mathutils import Matrix, Quaternion

# The following table is taken from Mirex's work
# Please go check his website, it's a real goldmine : https://mirex.mypage.sk/index.php?selected=0

SKELETONS_NAMES = {
    "diff":"Aeris - 10 Years Old",
    "cqga":"Aeris - 5 Years Old",
    "azbb":"Aeris - Dress",
    "cahc":"Aeris - Flowers",
    "auff":"Aeris - Normal",
    "akee":"Airship Crew - Fat",
    "ajif":"Airship Crew - Normal",
    "dhge":"Barrel - Normal",
    "acgd":"Barret - Normal",
    "aiba":"Barret - Parachute",
    "ayfb":"Barret - Sailor",
    "fqcb":"Barret - Young",
    "gjcf":"Basket Ball - Normal",
    "gdic":"Bat - Normal",
    "fmcc":"Beach Boy - Normal",
    "fmib":"Beach Girl - Normal",
    "ckfc":"Beach Man 1 - Normal",
    "clbb":"Beach Man 2 - Normal",
    "flge":"Beach Woman 1 - Normal",
    "ggid":"Beam of Light - Pink",
    "ggjc":"Beam of Light - Yellow",
    "cfbb":"Begger - Normal",
    "fobe":"Begger 2 - Normal",
    "bwfd":"Biggs - Normal",
    "gjeb":"Bike - Arcade",
    "brgd":"Bike - Normal",
    "echd":"Blink - Normal",
    "dvbe":"Bouncer - Left",
    "dufa":"Bouncer - Right",
    "fqab":"Box 1 - Left",
    "fqbb":"Box 1 - South",
    "hvcf":"Box 2 - Normal",
    "etfe":"Boy - Blank Face",
    "dgcd":"Boy 1 - Normal",
    "cgif":"Boy 2 - Normal",
    "ctib":"Boy 3 - Normal",
    "afec":"Bugenhagen - Normal",
    "gwcc":"Bugenhagen 2 - Normal",
    "hgia":"Cage - Normal",
    "aebc":"Caitsith - Normal",
    "fbge":"Caitsith - Reporter",
    "cyif":"Camera Man - Normal",
    "eyie":"Car - Normal",
    "bdga":"Cat - Normal",
    "ezcc":"Cat 2 - Normal",
    "gcjc":"Chair Lift - Normal",
    "avhe":"Chest 1 - Normal",
    "awae":"Chest 2 - Normal",
    "bydd":"Chest 3 - Normal",
    "hjga":"Chest 4 - Normal",
    "hrce":"Chest 5 - Normal",
    "cgda":"Child - Normal",
    "aqgc":"Chocobo - Normal",
    "ebec":"Chocobo Boy - Normal",
    "gbia":"Chocobo Costume - Normal",
    "gofd":"Chocobo Girl - Normal",
    "gpcd":"Chocobo Racer 1 - Normal",
    "gpjb":"Chocobo Racer 2 - Normal",
    "gqfe":"Chocobo Racer 3 - Normal",
    "abda":"Cid - Normal",
    "aihb":"Cid - Parachute",
    "gzad":"Cid - Young",
    "ehhc":"Cloaked Figure - Normal",
    "enab":"Cloud - 13 Years Old",
    "buge":"Cloud - 8 Years Old",
    "brib":"Cloud - Bike",
    "aaaa":"Cloud - Normal",
    "afie":"Cloud - Parachute",
    "ekbf":"Cloud - Soldier",
    "eihd":"Cloud - Soldier Helmet",
    "bhff":"Cloud - Sword",
    "htje":"Cloud - Wheel Chair",
    "dlfb":"Cloud - Woman",
    "bjfb":"Cloud's Mother - Normal",
    "gchc":"Coaster Car - Normal",
    "eoce":"Coffin - Normal",
    "exga":"Condor - Normal",
    "ewbd":"Condor Fort Man - Normal",
    "ewje":"Condor Fort Woman - Normal",
    "grga":"Cosmo Canyon - Man",
    "guba":"Costa Del Sol - Boy",
    "guhc":"Costa Del Sol - Door 1",
    "guib":"Costa Del Sol - Door 2",
    "gsbe":"Costa Del Sol - Girl",
    "gtfc":"Costa Del Sol - Old Woman",
    "gvae":"Costa Del Sol - Satellite Dish",
    "gvbc":"Costa Del Sol - Wind Veil",
    "gsje":"Costa Del Sol - Woman",
    "hree":"Crystal - Rock",
    "hrff":"Crystal 1 - Normal",
    "hrha":"Crystal 2 - Normal",
    "hrhe":"Crystal 3 - Normal",
    "gghe":"Cursor - Normal",
    "badd":"Dancer - Normal",
    "cige":"Detective - Normal",
    "gajc":"Dio - Normal",
    "hjie":"Dirt Line - A",
    "hjjd":"Dirt Line - B",
    "hkac":"Dirt Line - C",
    "bljc":"Doctor - Normal",
    "deie":"Dog 1 - Normal",
    "beec":"Dog 2 - Normal",
    "bdcd":"Dolphin - Normal",
    "fjbd":"Dome - Normal",
    "dvhf":"Don Corneo - Normal",
    "elgc":"Dr Gast - Normal",
    "fzcc":"Dragon - Normal",
    "bngd":"Dyne - Normal",
    "fqjb":"Dyne - Young",
    "grcc":"Elevator - Normal",
    "cogb":"Elmyra - Normal",
    "awcb":"Employee 1 - Normal",
    "dzgf":"Employee 2 - Normal",
    "cdja":"Employee 3 - Normal",
    "hkea":"Face - Normal",
    "ftic":"Farmer 1 - Normal",
    "ftcf":"Farmer 2 - Normal",
    "dmia":"Fat Man 1 - Normal",
    "dsbc":"Fat Woman 1 - Normal",
    "bfca":"Fatman - Normal",
    "gjha":"Fighter 1 - Normal",
    "gkcf":"Fighter 2 - Normal",
    "gkid":"Fighter 3 - Normal",
    "gleb":"Fighter 4 - Normal",
    "hyfd":"Final Jenova - Normal",
    "ffec":"Fish 1 - Normal",
    "fgae":"Fish 2 - Normal",
    "ffha":"Fish 3 - Normal",
    "hrae":"Flag - Red",
    "czgf":"Flower - Normal",
    "gehd":"Frankenstein - Normal",
    "ggef":"Gate 2 - Left",
    "ggfe":"Gate 2 - Right",
    "euaf":"Girl - Blank Face",
    "bmee":"Girl - Normal",
    "fkdf":"Girl - Normal",
    "cpca":"Girl 2 - Normal",
    "ched":"Girl 3 - Normal",
    "hgjd":"Godo - Normal",
    "ctcc":"Golden Saucer Staff - Female",
    "gcbd":"Golden Saucer Staff - Male",
    "bsfc":"Grandma - Normal",
    "dsgf":"Grandma 1 - Normal",
    "coad":"Grandma 2 - Normal",
    "hmif":"Grasshopper - Normal",
    "effb":"Grate - Normal",
    "azhe":"Guard - Normal",
    "fxjc":"Guard - Normal",
    "asjc":"Guide 1 - Normal",
    "bccf":"Guide 2 - Normal",
    "auda":"Gun - Normal",
    "eefb":"Gym Arm - Normal",
    "ebjf":"Hall Panel - Left",
    "ecae":"Hall Panel - Right",
    "gfdf":"Hang Man - Normal",
    "gebb":"Haunted House Butler - Normal",
    "algd":"Heidigger - Normal",
    "eaid":"Helicopter - Normal",
    "anbd":"Hojo - Normal",
    "ekjb":"Hojo - Young",
    "gujc":"Ice Map - Normal",
    "hseb":"Icecle - Normal",
    "cpjf":"Ifalna - Normal",
    "fkca":"Jenova's Arm - Normal",
    "axdc":"Jessie - Normal",
    "eoac":"Key - Normal",
    "dyfd":"King - Normal",
    "dzbb":"Knight - Normal",
    "dhhf":"Ladder - Normal",
    "fghf":"Lantern - Normal",
    "ddha":"Lonely Man - Normal",
    "atfe":"Lucrecia - Normal",
    "drif":"Lunch 1 - Normal",
    "dria":"Lunch 2 - Normal",
    "drje":"Lunch 3 - Normal",
    "ccbc":"Man - Normal",
    "hlfc":"Man - Normal",
    "blde":"Man 1 - Normal",
    "asbf":"Man 10 - Normal",
    "fnef":"Man 11 - Normal",
    "crid":"Man 12 - Normal",
    "cefd":"Man 13 - Normal",
    "ciac":"Man 14 - Normal",
    "emdf":"Man 15 - Normal",
    "csed":"Man 16 - Normal",
    "dpef":"Man 17 - Normal",
    "crca":"Man 2 - Normal",
    "fsge":"Man 2 - Normal",
    "gwif":"Man 2 - Normal",
    "deda":"Man 3 - Normal",
    "gxef":"Man 3 - Normal",
    "cjif":"Man 4 - Normal",
    "dcic":"Man 5 - Normal",
    "drcc":"Man 6 - Normal",
    "bqfb":"Man 7 - Normal",
    "dqgd":"Man 8 - Normal",
    "cjcc":"Man 9 - Normal",
    "cmif":"Man1 - Normal",
    "fjaf":"Marker - Normal",
    "cyae":"Marlene - Normal",
    "hjgc":"Materia - Black",
    "dabf":"Materia - Green",
    "gwib":"Materia - Holy",
    "aude":"Materia - Pink",
    "awbe":"Materia - Red",
    "byib":"Materia - Teal",
    "ateb":"Materia - Yellow",
    "frgd":"Mayor - Normal",
    "ghgf":"Mech - Normal",
    "gzhf":"Mechanic - Normal",
    "dfgd":"Merchant - Normal",
    "fgec":"Metal Door - Normal",
    "djfa":"Metal Hook - Normal",
    "djfe":"Metal Plank - Normal",
    "dkjd":"Midgar Door - Left",
    "dkie":"Midgar Door - Right",
    "fhaa":"Monster 1 - Normal",
    "fiba":"Monster 2 - Normal",
    "gmha":"Moogle - Adult Pink",
    "gljd":"Moogle - Adult Whitel",
    "goac":"Moogle - Young Pink",
    "gnca":"Moogle - Young White",
    "gngb":"Moogle - Young Yellow",
    "fved":"Mr Coates - Normal",
    "fwgf":"Necklace - Normal",
    "epfb":"Nibeilheim Monster - Normal",
    "bybf":"North Mako Reactor Gate 1 - Normal",
    "bycd":"North Mako Reactor Gate 2 - Normal",
    "byba":"North Mako Reactor Gate 3 - Normal",
    "btec":"Nurse - Normal",
    "bocc":"Old Farmer - Normal",
    "euhb":"Old Man - Normal",
    "bfhe":"Old Man 1 - Normal",
    "dmcb":"Old Man 2 - Normal",
    "arfd":"Old Man 3 - Normal",
    "edjd":"Old Man 4 - Normal",
    "dxje":"Old Woman 2 - Normal",
    "eegc":"Palmer - Normal",
    "bygf":"Potion - Blue",
    "dcfb":"Potion - Green",
    "ccha":"Potion - Normal",
    "fabb":"Potion - Red",
    "faae":"Potion 1 - Normal",
    "fabe":"Potion 2 - Normal",
    "fsdd":"Potion 3 - Normal",
    "fadc":"Potion 4 - Normal",
    "awhf":"President Shinra - Normal",
    "bkbf":"Priscilla - Normal",
    "eaga":"Propeller - Normal",
    "facc":"Propeller 2 - Normal",
    "gshc":"Propeller 3 - Normal",
    "hxbc":"Proud Clod - Normal",
    "cfha":"Punk - Normal",
    "cufc":"Punk 1 - Normal",
    "cvba":"Punk 2 - Normal",
    "fufe":"Punk 3 - Normal",
    "cvge":"Punk 4 - Normal",
    "adda":"Red XIII - Normal",
    "fjcf":"Red XIII - Soldier",
    "fbba":"Reporter 1 - Normal",
    "fcgd":"Reporter 2 - Normal",
    "fcaf":"Reporter 3 - Normal",
    "fgfb":"Robot Arm - Normal",
    "bzda":"Robot Soldier - Normal",
    "gzgb":"Rocket Inside Door - Left",
    "gzha":"Rocket Inside Door - Right",
    "dtce":"Rocket Man - Normal",
    "gydc":"Rocket Town - Woman",
    "hjhf":"Rolling Rock - Normal",
    "eagf":"Rope - Broken",
    "dcce":"Rope - Normal",
    "alad":"Rufus - Normal",
    "cned":"Sack - Normal",
    "avfe":"Save Icon - Normal",
    "amcc":"Scarlet - Normal",
    "eoea":"Sephiroth - Book",
    "bkhd":"Sephiroth - Normal",
    "bbab":"Sephiroth - Sword",
    "bgjc":"Sephiroth - Sword 2",
    "bgdc":"Shera - Normal",
    "bcgd":"Ship Crew - Normal",
    "hqgc":"Sled - Normal",
    "hpce":"Snow - Child",
    "hpib":"Snow - Man",
    "bohe":"Snow - Woman",
    "hqhc":"Snow Board - Normal",
    "fndf":"Soccer Ball - Normal",
    "dxbd":"Soldier - Gun",
    "bwab":"Soldier - Normal",
    "eseb":"Soldier - Sword",
    "cade":"South Mako Reactor Gate - Normal",
    "hkbb":"Spirit Pool - Normal",
    "ebca":"Spot Light - Normal",
    "dtjb":"Suit Man - Normal",
    "giha":"Sumo 1 - Top Half",
    "gjab":"Sumo 2 - Top Half",
    "hkhb":"Temple Model - Normal",
    "bidb":"Tifa - 15 Years Old",
    "buac":"Tifa - 7 Years Old",
    "axja":"Tifa - Dress",
    "aagb":"Tifa - Normal",
    "aggb":"Tifa - Parachute",
    "eqib":"Tifa - Sword",
    "bvda":"Tifa's Father - Normal",
    "doga":"Tifa's Hand - Normal",
    "hneb":"Tonge - Normal",
    "evfe":"Turks - Elena - Normal",
    "bpjb":"Turks - Reeve - Normal",
    "aodd":"Turks - Reno - Normal",
    "mmmo":"Turks - Reno Redface",
    "anic":"Turks - Rude - Normal",
    "dbec":"Turks - Tseng - Normal",
    "hsjd":"Ultima Weapon - Normal",
    "aehd":"Vincent - Normal",
    "bijd":"Vincent - Turk",
    "hkjc":"Wall Demon - Normal",
    "bxbe":"Wedge - Normal",
    "gabe":"Wizard - Normal",
    "cbfe":"Woman - Normal",
    "eiac":"Woman - Normal",
    "flac":"Woman - Normal",
    "hmbe":"Woman - Normal",
    "braf":"Woman 1 - Normal",
    "bbge":"Woman 2 - Normal",
    "cwed":"Woman 3 - Normal",
    "ghad":"Woman 4 - Normal",
    "ehbe":"Woman 5 - Normal",
    "doib":"Woman 6 - Normal",
    "ecbf":"Woman 7 - Normal",
    "fpcb":"Woman 8 - Normal",
    "dqae":"Woman 9 - Normal",
    "ecib":"Woman1 - Normal",
    "dafb":"Woman2 - Normal",
    "dnje":"Wrestler 1 - Normal",
    "bpdc":"Wrestler 2 - Normal",
    "dndf":"Wrestler 3 - Normal",
    "hgaf":"Wutai - Child",
    "hhge":"Wutai - Door Left",
    "hhhd":"Wutai - Door Right",
    "hdgf":"Wutai - Man 1",
    "hffb":"Wutai - Man 2",
    "hddb":"Wutai - Man 3",
    "hhic":"Wutai - Rolling Door",
    "hhjf":"Wutai - Shinobi",
    "hecd":"Wutai - Woman 1",
    "heib":"Wutai - Woman 2",
    "abjb":"Yuffie - Normal",
    "ahdf":"Yuffie - Parachute",
    "feea":"Yuffie - Reporter",
    "ibad":"Zack - Normal",
    "ejdc":"Zack - Sword Sheathed",
    "ibgd":"Zack - Sword Wielded",
    "bnaf":"Zangan - Normal"
}

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
    def __init__(self, filename, name, nb_bones):
        self.filename = filename
        self.name = name
        self.nb_bones = nb_bones
        self.bones = {}
    
    @property
    def filename(self):
        return self.__filename

    @filename.setter
    def filename(self, filename):
        self.__filename = filename

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
        
class LGPFile:
    def __init__(self, filepath):
        self.toc = {}
        with open(filepath, "rb") as f:
            f.seek(12, 1) # Ignoring the first 12 bytes (File creator)
            self.nb_files = int.from_bytes(f.read(4), byteorder="little")
            if self.nb_files > 0: # If we have at least one file, we process the first one's information outside of the loop
                filename = f.read(20).decode("utf-8").rstrip('\x00')
                first_offset = int.from_bytes(f.read(4), byteorder="little")
                self.toc[filename] = first_offset
                f.seek(3, 1) # Avoiding useless information
            for toc_index in range(self.nb_files - 1): # Now we process all remaining files
                filename = f.read(20).decode("utf-8").rstrip('\x00')
                file_offset = int.from_bytes(f.read(4), byteorder="little")
                if file_offset < first_offset:
                    first_offset = file_offset
                self.toc[filename] = file_offset
                f.seek(3, 1) # Avoiding useless information
            self.toc = { k : v - first_offset for k, v in self.toc.items() } # Modify every offset to remove header and CRC length
            f.seek(first_offset, 0) # Moving to the first file description
            self.files = f.read() # Storing all files' data

    @property
    def toc(self):
        return self.__toc

    @toc.setter
    def toc(self, toc):
        self.__toc = toc

    @property
    def files(self):
        return self.__files

    @files.setter
    def files(self, files):
        self.__files = files

    def getFileContent(self, filename):
        if filename not in self.toc:
            raise ValueError("File name not in LGP file")
        
        start_len = self.toc[filename] + 20
        start_pos = self.toc[filename] + 24
        
        length = int.from_bytes(self.files[start_len:start_pos], byteorder="little")
        
        return self.files[start_pos:start_pos + length].decode("utf-8")

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

def importLgp(context, filepath):
    # Loading Python objects (do not put Blender related stuff in there)
    lgp_file = LGPFile(filepath)
    skeletons = []

    for filename in lgp_file.toc:
        if os.path.splitext(filename)[1] != ".hrc": # We only process skeletons
            continue

        lines = lgp_file.getFileContent(filename).splitlines()
        
        skeleton = HRCSkeleton(os.path.splitext(filename)[0], lines[1].split(" ")[1], int(lines[2].split(" ")[1]))
        newBone = True
        first_bone_row = 0
        name = parent = ""
        length = 0.0
        for rownum, line in enumerate(lines[3:], start=4): # Starting right after the header
            if line[:1] == "#": # No use of comments
                if not newBone:
                    first_bone_row = first_bone_row + 1 # Hack to ignore commented rows within a bone
            elif not line.strip(): # Empty lines mark the arrival of a new bone next line
                if name != "" and parent != "" and length != 0.0:
                    bone = HRCBone(name, parent, length, None, None)
                    skeleton.addBone(bone)
                name = parent = ""
                length = 0.0
                newBone = True
            elif newBone: # First line of a new bone
                first_bone_row = rownum
                name = line
                newBone = False
            else: # Line within a bone
                if rownum == first_bone_row + 1: # Parent
                    parent = line
                elif rownum == first_bone_row + 2: # Length
                    length = float(line)
                elif rownum == first_bone_row + 3: # RSD files
                    rsd = line.split(maxsplit=1)
                    if int(rsd[0]) > 0:
                        rsd_files = rsd[1].split()
                        for rsd_file in rsd_files:
                            pass
                else:
                    first_bone_row = first_bone_row + 1 # Unhandled row, ignoring it
        if newBone:
            if name != "" and parent != "" and length != 0.0: # Last bone of the model
                bone = HRCBone(name, parent, length, None, None)
                skeleton.addBone(bone)

        skeletons.append(skeleton)

    # Now we have all needed objects, we can work in Blender
    for skeleton in skeletons:
        # Adding a new Scene per skeleton
        scene = bpy.data.scenes.new(skeleton.name)
        bpy.context.window.scene = scene
        view_layer = bpy.context.view_layer
        # Adding armature to the scene
        if skeleton.filename in SKELETONS_NAMES:
            armature_data = bpy.data.armatures.new(name=SKELETONS_NAMES[skeleton.filename]+"_root") # The Armature will represent the root bone for transformation purposes
            armature_obj = bpy.data.objects.new(name=SKELETONS_NAMES[skeleton.filename], object_data=armature_data)
        else:
            armature_data = bpy.data.armatures.new(name=skeleton.filename+"_root") # The Armature will represent the root bone for transformation purposes
            armature_obj = bpy.data.objects.new(name=skeleton.filename, object_data=armature_data)
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
        default="*.lgp",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        return importLgp(context, self.filepath)


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
