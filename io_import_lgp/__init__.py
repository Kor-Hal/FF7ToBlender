# Blender addon definition

bl_info = {
    "name": "Final Fantasy 7 flevel LGP import/export",
    "author": "Sébastien Dougnac",
    "blender": (3, 0, 1),
    "location": "File > Import-Export",
    "description": "Import-Export flevel LGP models and animations",
    "warning": "",
    "support": 'TESTING',
    "category": "Import-Export"
}

# Imports

import bmesh, bpy, math, os, struct
from mathutils import Quaternion, Vector

# Constants

# The following dictionary is taken from Kujata
# https://github.com/picklejar76/kujata/blob/master/friendly-names-db/skeleton-friendly-names.json

SKELETONS_NAMES = {
    "aaaa":"Cloud",
    "aagb":"Tifa",
    "abda":"Cid",
    "abjb":"Yuffie",
    "acgd":"Barret",
    "adda":"Red XIII",
    "aebc":"Cait Sith",
    "aehd":"Vincent",
    "afec":"Bugenhagen",
    "afie":"Cloud Parachute",
    "aggb":"Tifa Parachute",
    "ahdf":"Yuffie Parachute",
    "aiba":"Barret Parachute",
    "aihb":"Cid Parachute",
    "ajif":"Skinny Highwind Crewman",
    "akee":"Burly Highwind Crewman",
    "alad":"Rufus",
    "algd":"Heidegger",
    "amcc":"Scarlet",
    "anbd":"Hojo",
    "anic":"Rude",
    "aodd":"Reno",
    "aqgc":"Chocobo",
    "arfd":"Sleeping Old Man",
    "asbf":"Tanned Midgar Man",
    "asjc":"Chocobo Sage",
    "ateb":"Command Materia",
    "atfe":"Lucretia in Cave",
    "auda":"Handgun",
    "aude":"Independent Materia",
    "auff":"Aeris",
    "avfe":"Save Point",
    "avhe":"Traditional Chest",
    "awae":"Green Chest",
    "awbe":"Summon Materia",
    "awcb":"Hojo Assistant",
    "awhf":"President Shinra",
    "axdc":"Jessie",
    "axja":"Tifa Corneo",
    "ayfb":"Barret Sailor",
    "azbb":"Aeris Corneo",
    "azhe":"Train Guard",
    "badd":"Honey Bee Girl",
    "bbab":"Sephiroth w/Sword",
    "bbge":"Costa Bar Girl",
    "bccf":"Ancient Temple Guard",
    "bcgd":"Shinra Sailor",
    "bdcd":"Mr. Dolphin",
    "bdga":"Cat",
    "beec":"Mideel Dog (Grey)",
    "bfca":"Johnny's Dad",
    "bfhe":"Sector 7 Shop Owner",
    "bgdc":"Shera",
    "bgjc":"Sephiroth w/Jenny Head",
    "bhff":"Cloud w/Buster Sword",
    "bidb":"Tifa Cowgirl",
    "bijd":"Vincent Turk",
    "bjfb":"Cloud's Mom",
    "bkbf":"Priscilla",
    "bkhd":"Sephiroth",
    "blde":"Tifa's Father's Friend",
    "bljc":"Mideel Doctor",
    "bmee":"Little Girl",
    "bnaf":"ZANGAN",
    "bngd":"Dyne w/Gun",
    "bocc":"Grey Peasant",
    "bohe":"Icicle Inn Woman/Mother",
    "bpdc":"Muscle-Man (Blonde)",
    "bpjd":"Reeve",
    "bqfb":"Blue Villager",
    "braf":"Cloud's House Occupant",
    "brgd":"Motorcycle...",
    "brib":"Cloud Motorcycle (Jesus)",
    "bsfc":"Female Villager",
    "btec":"Female Nurse",
    "buac":"Young Tifa",
    "buge":"Young Cloud",
    "bvda":"Tifa's Father",
    "bwab":"Shinra Soldier",
    "bwfd":"Biggs",
    "bxbe":"Wedge",
    "bxjb":"Train Door",
    "byba":"Slab",
    "bybf":"Panel w/Lights",
    "bycd":"Catwalk Grating",
    "bydd":"Gold Chest",
    "bygf":"Blue Potion",
    "byib":"Magic Materia",
    "bzda":"AIR BUSTER!",
    "bzhf":"Shinra Beta Copter",
    "cade":"Catwalk Grating",
    "cahc":"Aeris w/Flower Basket",
    "cbfe":"Red hair hooker",
    "ccbc":"Red Punk",
    "ccha":"Light Blue Potion",
    "cdja":"Shinra Manager",
    "cefd":"Train Drunk",
    "cfbb":"Phoenix Down Hobo",
    "cfha":"Honey Bee Guard/Punk",
    "cgda":"Sector 7 Kid",
    "cgif":"Red Cap Tifa friend",
    "ched":"Chole",
    "ciac":"Hi-Potion Dealer",
    "cige":"Biggs Train Disguise",
    "cjcc":"Wedge Train Disguise",
    "cjif":"Johnny",
    "ckfc":"Costa Guy",
    "clbb":"Costa Surf Bro",
    "clgd":"Tall Cloud Field",
    "cmde":"Tall Jessie Field",
    "cmif":"Tanned Guy",
    "cned":"Item Bag",
    "cnfb":"Moving Train (Train Graveyard)",
    "cnhf":"Train Carriage (Train Graveyard)",
    "coad":"Housewife Purple",
    "cogb":"Elmyra",
    "cpca":"Child, Red dungarees",
    "cpjf":"Ifalna",
    "cqga":"Kid Aeris",
    "crca":"Tifa's Father's Friend",
    "crid":"Tracksuit Man",
    "csed":"Cosmo Miner Repairman csga",
    "ctbe":"Magic Materia",
    "ctcc":"Gold Saucer F. Attendant",
    "ctib":"Hall; Kid Opponent",
    "cufc":"Hall; Black Flexer",
    "cvba":"Hall; Burly Flexer",
    "cvge":"Hall; Punk Flexer",
    "cwed":"Sector 7 Busy-body",
    "cyae":"Marlene",
    "cyif":"Mr. Duffi-look alike",
    "czed":"Avalanche Hideout: Pinball Machine",
    "czgb":"Yellow Rectangle",
    "czgf":"Flowers",
    "dabf":"Green Materia",
    "dafb":"Cologne Lady",
    "dbec":"Tseng",
    "dcce":"Pillar Collapse Hook-Swing",
    "dcfb":"Bright Green Potion",
    "dcic":"Tanned Guy NPC",
    "ddha":"This guy are sick",
    "deda":"Clothes Shop Son",
    "deie":"Dog (Brown)",
    "dfgd":"Tiara Guy",
    "dgcd":"Nibel Kids Boy",
    "dhaf":"Reno (No Face)",
    "dhge":"Barrel",
    "dhhf":"Ladder",
    "dhid":"Rocky Caltrops",
    "diff":"Kid Aeris, Brown Dress",
    "djfa":"Claw in Golden Saucer Claw-Game",
    "djfe":"Girder",
    "djid":"Chocobo Carriage",
    "dkie":"Metal Flooring (4)",
    "dkjd":"Metal Flooring (7)",
    "dlfb":"Cloud Corneo",
    "dmcb":"Old tanned guy",
    "dmia":"Miner/Jon-Tron",
    "dndf":"Black Muscle-man",
    "dnje":"Mukki",
    "doga":"Battle Model-Like Hand",
    "doib":"Female Trenchcoat NPC doje",
    "dpef":"Chef in Wall Market",
    "dqae":"Accessory Maid",
    "dqgd":"Diner at Wall Market",
    "drcc":"Rocket Technician",
    "dria":"Meal A TEX Wall Market",
    "drif":"Meal B TEX Wall Market",
    "drje":"Meal C TEX Wall Market",
    "dsbc":"Kalm Chef",
    "dsgf":"Junon Old Inn Lady",
    "dtce":"High-Collar NPC",
    "dtic":"Propellor (Green)",
    "dtjb":"Honey Bee Manager",
    "dufa":"Scotch",
    "dvbe":"Kotch",
    "dvhf":"Don Corneo",
    "dxbd":"Shinra Soldier Rifle",
    "dxje":"Daughter Honey Bee Room",
    "dyfd":"King Shinra",
    "dzbb":"Knight",
    "dzgf":"Shinra Manager Alt",
    "eaga":"Broken Propellor, Climb to Shinra Tower",
    "eagf":"Swinging Beam, Climb to Shinra Tower",
    "eaid":"Shinra Alpha Copter",
    "ebca":"Beam of light",
    "ebec":"Choco Billy",
    "ebjf":"Door/Panel Shinra Tower?",
    "ecae":"Ditto",
    "ecbf":"Turqouise Dress NPC",
    "echd":"Shinra Tower Glass Elevator",
    "ecib":"Shinra Secretary",
    "edea":"Woman fl60",
    "edjd":"Old Man",
    "eefb":"Construct, maybe a paddock",
    "eegc":"Palmer",
    "effb":"Grate Toilet 66th Floor",
    "eghe":"Masamune (President Shinra Dead)",
    "ehbe":"Tracksuit NPC",
    "ehhc":"Black-Cloaked Man",
    "eiac":"Red Woman NPC",
    "eihd":"Cloud, Helmet in Hands, on Truck",
    "ejdc":"Zack w/sword",
    "ekbf":"MP Cloud",
    "ekjb":"Young Hojo",
    "elgc":"Young Gast",
    "emdf":"Corel Miner",
    "enab":"Young Cloud Black Shirt",
    "eoac":"Key",
    "eoce":"Vincent Coffin lid",
    "eoea":"Sephiroth with book",
    "epfb":"Materia Keeper",
    "eqib":"Cowgirl Tifa w/Masamune",
    "erha":"Sephy w/Jenny Head",
    "eseb":"MP Cloud w/Sword",
    "etfe":"Blue Child, No Face",
    "euaf":"Red Child, No Face",
    "euhb":"Crazy old guy!",
    "evfe":"Elena",
    "ewbd":"Corel Burly Miner",
    "ewje":"Corel Miner Wife",
    "exga":"Small Condor",
    "eyie":"Rufus' Car",
    "ezcc":"Patchwork Cat",
    "faae":"Cyan Potion",
    "fabb":"Red Potion",
    "fabe":"Green Potion",
    "facc":"Black Propellor/Untex",
    "fadc":"Yellow Potion",
    "fbba":"Journalist Male",
    "fbge":"Cait Sith Journalist",
    "fcaf":"Journalist Female",
    "fcgd":"Cameraman",
    "feea":"Yuffie Journalist",
    "ffec":"Small Green Fish",
    "ffha":"Yellow/Red Shoal",
    "fgae":"Shark",
    "fgec":"Metal Door",
    "fgfb":"Crane Claw",
    "fghf":"Huge Materia Capsule Underwater Reactor",
    "fhaa":"Carry Armour",
    "fhic":"Door/Panel",
    "fhjb":"Door/Panel 1",
    "fiba":"Bottomswell",
    "fjaf":"Red Light",
    "fjbd":"Lung Meter CPR",
    "fjcf":"Red XIII Soldier Disguise",
    "fkca":"Jenova Tentacle",
    "fkdf":"Hojo Groupie lying down",
    "flac":"Costa Entrance Girl",
    "flge":"Costa Beach girl",
    "fmcc":"Snorkel Kid",
    "fmib":"Swimsuit kid",
    "fndf":"Football",
    "fnef":"Sector 7 Wep Shop Shooter",
    "fobe":"Layabout",
    "fpcb":"Catastrophe Corel girl",
    "fqab":"Long Train, Corel Chase",
    "fqbb":"Cid's Train, Corel Chase",
    "fqcb":"Barret, Corel Flashback",
    "fqjb":"Dyne, Corel Flashback frae",
    "frgd":"Corel Mayor",
    "fsdd":"Pink Potion",
    "fsge":"Corel Miner, slumped",
    "ftcf":"Corel Miner",
    "ftic":"Corel Miner, female",
    "fufe":"Corel Miner/Punk",
    "fved":"Mr. Coates",
    "fwae":"Ester",
    "fwgf":"Dyne's Pendant",
    "fxjc":"Gold Saucer Guard",
    "fzcc":"EDK",
    "gabe":"Play Wizard",
    "gajc":"Dio",
    "gbia":"G.Saucer Bird-Suit",
    "gcbd":"Male Attendant",
    "gchc":"G.Saucer Coaster",
    "gcjc":"Gondola Texture",
    "gdic":"Bat",
    "gebb":"Hotel Greeter/Lurch",
    "gehd":"Hotel Desk/Igor",
    "gfdf":"Mr. Hangman",
    "ggef":"Elixir Cabinet Door-right",
    "ggfe":"Ditto, Left door",
    "gghe":"Hand Pointer Tex",
    "ggid":"Purple shaft of light",
    "ggjc":"Yellow shaft of light (Battle Square)",
    "ghad":"Battle Square, f.kicker",
    "ghgf":"G.Saucer Capture Device",
    "giha":"ZANGIEF!",
    "gjab":"E.HONDA!",
    "gjcf":"Basketball",
    "gjeb":"Speed Bike, Field",
    "gjha":"3D Battler, Rookie",
    "gkcf":"3D Battler, Luchadore gkec",
    "gkid":"3D Battler, Afro Thunder",
    "gleb":"3D Battler, Super Hero",
    "gljd":"Mog",
    "gmha":"Pink Mog",
    "gnca":"Bright Mog",
    "gngb":"Yellow Mog",
    "goac":"Pink Mog",
    "gofd":"Choco Square Teller",
    "gpcd":"Joe",
    "gpjb":"Blue Jockey",
    "gqfe":"Green Jockey",
    "grcc":"Choco Elevator (From Corel Prison)",
    "grga":"Cosmo Canyon Greeter",
    "gsbe":"Cosmo Kid",
    "gshc":"Cosmo Propellor",
    "gsje":"Cosmo Mother",
    "gtfc":"Cosmo Elderly Lady",
    "guba":"Cosmo Kid Boy",
    "guhc":"Cosmo Door",
    "guib":"Cosmo Door",
    "gujc":"Glacier Map",
    "gvae":"Radar Dish",
    "gvbc":"Weather Vane",
    "gvce":"Yellow Huge Materia",
    "gvdc":"Green Huge Materia",
    "gvea":"Red Huge Materia",
    "gvee":"Blue Huge Materia",
    "gwaa":"Cosmo Observatory Planet/Two Moons",
    "gwcc":"Bugenhagen Lying down (Green orb missing)",
    "gwib":"Green orb",
    "gwif":"Rocket Town Citizen",
    "gxef":"Rocket Town Bored Citizen gxgc",
    "gydc":"Rocket Town Citizen",
    "gzad":"Young Cid",
    "gzgb":"Door Base; Rocket",
    "gzha":"Door Base; Rocket",
    "gzhf":"Rocket Technician",
    "hagb":"Rocket Huge Materia Capsule",
    "hcef":"Debris, pins Cid",
    "hdbb":"Wutai Citizen male",
    "hdgf":"Wutai Citizen, Staniv hdic",
    "hecd":"Wutai Citizen, Chekhov",
    "heib":"Wutai Citizen female",
    "hffb":"Wutai Citizen, Gorki",
    "hgaf":"Wutai Citizen, Shake",
    "hgia":"Yuffie House Cage",
    "hgjd":"Godo",
    "hhge":"Wutai Door",
    "hhhd":"Wutai Door",
    "hhic":"Wutai Panel",
    "hhjf":"Corneo Ninja",
    "hjdc":"Component, Gong-mechanism possibly",
    "hjga":"Ancient Temple Chest",
    "hjhf":"Rolling Stone",
    "hjie":"Clock, Minute/Sec Hand",
    "hjjd":"Clock, Minute/sec Hand",
    "hkac":"Clock, Hour Hand",
    "hkbb":"Clock core, base",
    "hkea":"Clock Core, mouth",
    "hkhb":"Temple Puzzle",
    "hkjc":"Demon Wall",
    "hlfc":"Green Digger",
    "hmbe":"Purple Digger",
    "hmif":"Ancient Forest, Fly",
    "hnaf":"Ancient FOrest, Frog",
    "hneb":"Ancient Forest, Tongue Feeler",
    "hnif":"Ancient Forest, Bee Hive",
    "hobd":"Ancient Key",
    "hpce":"Icicle Kid Girl",
    "hpib":"Icicle Man",
    "hqgc":"Blue Panel",
    "hqhc":"Snowboard",
    "hrae":"Red Flag",
    "hrce":"Blue Chest",
    "hree":"Tumbling Rock",
    "hrff":"Ice Stalagmite",
    "hrha":"Ice Stalagmite",
    "hrhe":"Ice Stalagmite",
    "hseb":"Ice Stalagmite",
    "hsjd":"Ultimate Weapon",
    "htje":"Handicapable Cloud",
    "hvcf":"Train Cars, Corel Chase",
    "hvjf":"Red XIII Para Freefall",
    "hwib":"Parachute open texture",
    "hxbc":"Proud Clod",
    "hyfd":"Jenova Synthesis",
    "iajd":"Yellow Projectile (Diamond Wep Attacks)",
    "ibad":"Zack, no sword",
    "ibgd":"Zack, w/sword"
}

# Classes

class LGPFile:
    def __init__(self, data):
        self.toc = {}
        offset = 12 # Ignoring the first 12 bytes (File creator)
        numFiles, = struct.unpack("<I", data[offset:offset + 4])
        offset += 4
        if numFiles > 0: # If we have at least one file, we process the first one's information outside of the loop
            filename, first_offset = struct.unpack("<20sI", data[offset:offset + 24])
            filename = filename.decode("utf-8").rstrip('\x00')
            offset += 24
            self.toc[filename] = first_offset
            offset += 3 # Avoiding useless information
        for _ in range(numFiles - 1): # Now we process all remaining files
            filename, fileOffset = struct.unpack("<20sI", data[offset:offset + 24])
            filename = filename.decode("utf-8").rstrip('\x00')
            offset += 24
            if fileOffset < first_offset:
                first_offset = fileOffset
            self.toc[filename] = fileOffset
            offset += 3 # Avoiding useless information
        self.toc = { k : v - first_offset for k, v in self.toc.items() } # Modify every offset to remove header and CRC length
        self.files = data[first_offset:] # Storing all files' data

    @classmethod
    def fromFile(cls, filepath):
        with open(filepath, "rb") as f:
            return cls(f.read())

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
            raise KeyError("File name {} not in LGP file".format(filename))
        
        start_len = self.toc[filename] + 20
        start_pos = self.toc[filename] + 24
        
        length = int.from_bytes(self.files[start_len:start_pos], byteorder="little")
        
        return self.files[start_pos:start_pos + length]

class LZSSFile:
    def __init__(self, data):
        self.uncompressedData = bytearray()

        # Header is 4 bytes defining the file's length, not including itself
        header, = struct.unpack("<I", data[:4])
        fileOffset = 4
        if len(data) - 4 != header:
            raise ValueError("Not a valid LZSS file : File size {} doesn't match header's information {}".format(len(data), header + 4))
            
        buffer = bytearray(4096)
        bufferPos = int("0xFEE", 0)

        # Format : https://en.wikipedia.org/wiki/Lempel%E2%80%93Ziv%E2%80%93Storer%E2%80%93Szymanski
        # Each block of data consists of 1 Control Byte and 8 pieces of data (of variable lengths)
        while fileOffset < len(data):
            controlByte = data[fileOffset]
            fileOffset += 1
            controlBits = bin(controlByte)[2:].zfill(8)
            for bit in reversed(controlBits): # Bits are read LSB-first
                if bit == "1": # Literal data
                    buffer[bufferPos] = data[fileOffset]
                    fileOffset += 1
                    self.uncompressedData.append(buffer[bufferPos])
                    bufferPos += 1
                    bufferPos &= (len(buffer) - 1) # If we reach the last index, we start at 0
                else: # Reference
                    ref = data[fileOffset:fileOffset + 2]
                    fileOffset += 2
                    if len(ref) == 0: # We reached the end of the file
                        break
                    elif len(ref) == 1: # Specific case of a 1 Byte reference -> OOOOLLLL
                        offset = (ref[0] & 0b11110000) >> 4
                        length = (ref[0] & 0b00001111) + 3
                    else: # 2 Bytes reference -> OOOOOOOO OOOOLLLL
                        offset = ((ref[1] & 0b11110000) << 4) | ref[0]
                        length = (ref[1] & 0b00001111) + 3
                    for i in range(length):
                        byte = buffer[(offset + i) & (len(buffer) - 1)]
                        buffer[bufferPos] = byte
                        self.uncompressedData.append(byte)
                        bufferPos += 1
                        bufferPos &= (len(buffer) - 1)
    
    @classmethod
    def fromFile(cls, filepath):
        with open(filepath, "rb") as f:
            return cls(f.read())

    @property
    def uncompressedData(self):
        return self.__uncompressedData

    @uncompressedData.setter
    def uncompressedData(self, uncompressedData):
        self.__uncompressedData = uncompressedData

class FieldModule:
    def __init__(self, data):
        self.sections = { k : None for k in range(1,10) } # Field Module always has 9 sections

        _, numSections, sec1off, sec2off, sec3off, sec4off, sec5off, sec6off, sec7off, sec8off, sec9off = struct.unpack("<H10I", data[:42])
        if numSections != 9:
            raise ValueError("The Field Module must have exactly 9 sections ({} encountered)".format(numSections))
        
        for i in range(1,10):
            secOff = eval("sec{}off".format(i)) # Getting the offset for the current section
            secLen, = struct.unpack("<I", data[secOff:secOff + 4]) # The first 4 bytes are the length of the section
            secOff += 4 # Getting the real starting offset for the section
            self.sections[i] = data[secOff:secOff + secLen] # Storing binary data for this section

        # Only Section 3 is of interest here but using generic code in case of reuse later
        self.sections[3] = self.ModelLoader(self.sections[3])

    @classmethod
    def fromFile(cls, filepath):
        with open(filepath, "rb") as f:
            return cls(f.read())

    @property
    def sections(self):
        return self.__sections

    @sections.setter
    def sections(self, sections):
        self.__sections = sections

    class ModelLoader:
        def __init__(self, data):
            _, numModels, _ = struct.unpack("<3H", data[:6]) # Header
            offset = 6 # Position after header
            self.models = {}

            for _ in range(numModels):
                modelNameSize, = struct.unpack("<H", data[offset:offset + 2])
                offset += 2
                modelName, \
                _, \
                skeletonFile, \
                _, \
                numAnim, \
                lightColor1, \
                _, \
                lightColor2, \
                _, \
                lightColor3, \
                _, \
                globalLightColor = struct.unpack("<{}sH8s4sH3s6s3s6s3s6s3s".format(modelNameSize), data[offset:offset + modelNameSize + 46])
                offset += modelNameSize + 46
                anim = []
                for _ in range(numAnim):
                    animNameSize, = struct.unpack("<H", data[offset:offset + 2])
                    offset += 2
                    animFile, = struct.unpack("<{}s".format(animNameSize), data[offset:offset + animNameSize])
                    offset += animNameSize + 2 # There are 2 unused bytes at the end of each animation
                    anim.append(os.path.splitext(animFile.decode("utf-8"))[0] + ".a")
                model = self.Model(modelName.decode("utf-8"), skeletonFile.decode("utf-8"), lightColor1, lightColor2, lightColor3, globalLightColor, anim)
                self.models[modelName.decode("utf-8")] = model

        @property
        def models(self):
            return self.__models

        @models.setter
        def models(self, models):
            self.__models = models

        class Model:
            def __init__(self, name, skeletonFile, lightColor1, lightColor2, lightColor3, globalLightColor, animations):
                self.name = name
                self.skeletonFile = skeletonFile
                self.lightColor1 = lightColor1
                self.lightColor2 = lightColor2
                self.lightColor3 = lightColor3
                self.globalLightColor = globalLightColor
                self.animations = animations

            @property
            def name(self):
                return self.__name

            @name.setter
            def name(self, name):
                self.__name = name

            @property
            def skeletonFile(self):
                return self.__skeletonFile

            @skeletonFile.setter
            def skeletonFile(self, skeletonFile):
                self.__skeletonFile = skeletonFile

            @property
            def lightColor1(self):
                return self.__lightColor1

            @lightColor1.setter
            def lightColor1(self, lightColor1):
                self.__lightColor1 = lightColor1

            @property
            def lightColor2(self):
                return self.__lightColor2

            @lightColor2.setter
            def lightColor2(self, lightColor2):
                self.__lightColor2 = lightColor2

            @property
            def lightColor3(self):
                return self.__lightColor3

            @lightColor3.setter
            def lightColor3(self, lightColor3):
                self.__lightColor3 = lightColor3

            @property
            def globalLightColor(self):
                return self.__globalLightColor

            @globalLightColor.setter
            def globalLightColor(self, globalLightColor):
                self.__globalLightColor = globalLightColor

            @property
            def animations(self):
                return self.__animations

            @animations.setter
            def animations(self, animations):
                self.__animations = animations

class HRCSkeleton:
    def __init__(self, filename, hrcData, charLGPFile):
        self.filename = filename
        self.texFiles = None

        hrcLines = hrcData.decode("utf-8").splitlines()
        
        hrcLines = [hrcLine for hrcLine in hrcLines if hrcLine[:1] != "#"] # Removing comments

        self.name = hrcLines[1].split(" ")[1]
        self.numBones = int(hrcLines[2].split(" ")[1])
        self.bones = []
        name = parent = ""
        length = 0.0
        newBone = True
        for hrcRownum, hrcLine in enumerate(hrcLines[3:], start=3): # Starting right after the header
            if not hrcLine.strip(): # Empty lines mark the arrival of a new bone next line
                name = parent = ""
                length = 0.0
                newBone = True
            elif newBone: # First line of a new bone
                name = hrcLine
                parent = hrcLines[hrcRownum + 1]
                length = float(hrcLines[hrcRownum + 2])
                rsd = hrcLines[hrcRownum + 3].split()
                pFileList = []
                if int(rsd[0]): # If there's at least one RSD file
                    rsdFiles = [i.lower() + ".rsd" for i in rsd[1:]] # Get list of RSD files
                    for rsdFile in rsdFiles:
                        try:
                            rsdLines = charLGPFile.getFileContent(rsdFile).decode("utf-8").splitlines()
                        except:
                            continue

                        rsdLines = [rsdLine for rsdLine in rsdLines if rsdLine[:1] != "#"] # Removing comments

                        # The .P file can be deduced from either PLY, GRP or MAT section
                        # I chose PLY because it's the first one
                        pFileName = [i.lower() for i in rsdLines if i.startswith("PLY=")][0].split("=")[1]
                        pFileName = os.path.splitext(pFileName)[0] + ".p"

                        # The NTEX section gives us the number of texture files
                        numTex = int([i for i in rsdLines if i.startswith("NTEX=")][0][5:])
                        texFiles = []
                        if numTex > 0:
                            # We use list comprehension to extract TEX files' names
                            texList = [i[i.find("=") + 1:i.find(".")].lower() + ".tex" for i in rsdLines if i.startswith("TEX[")]
                            for tex in texList:
                                try:
                                    texFiles.append(self.TextureFile(tex, charLGPFile.getFileContent(tex)))
                                except Exception as e:
                                    print("Error creating TextureFile {} : {}".format(tex, e))
                                    raise

                        try:
                            pFile = self.PFile(pFileName, charLGPFile.getFileContent(pFileName), texFiles)
                            pFileList.append(pFile)
                        except Exception as e:
                            print("Error creating P file {} : {}".format(pFileName, e))
                            raise
            
                if name != "" and parent != "" and length != 0.0:
                    try:
                        bone = self.HRCBone(name, parent, length, pFileList)
                        self.bones.append(bone)
                    except Exception as e:
                        print("Error creating HRCBone {} : {}".format(name, e))
                        raise
            
                newBone = False
            else: # Line within a bone
                continue # Already processed with the first row for each bone
    
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
    def numBones(self):
        return self.__numBones
    
    @numBones.setter
    def numBones(self, numBones):
        self.__numBones = numBones if numBones > 0 else 1 # Default number of bones is 1
        
    @property
    def bones(self):
        return self.__bones
        
    @bones.setter
    def bones(self, bones):
        self.__bones = bones
        
    class HRCBone:
        def __init__(self, name, parent, length, pFiles):
            self.name = name
            self.parent = parent
            self.length = length
            self.pFiles = pFiles
            
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
        def pFiles(self):
            return self.__pFiles

        @pFiles.setter
        def pFiles(self, pFiles):
            self.__pFiles = pFiles

    class PFile:
        def __init__(self, filename, data, textureFiles):
            self.filename = filename

            # Loading header
            _, \
            _, \
            numVertices, \
            numNormals, \
            numUnknown1, \
            numTexCoords, \
            numVertexColors, \
            numEdges, \
            numPolys, \
            numUnknown2, \
            numUnknown3, \
            numHundreds, \
            numGroups, \
            numBoundingBoxes = struct.unpack("<Q13L", data[:60])
            offset = 128 # Header is 128 bytes long
            
            vertices_list = list(struct.unpack("<{}f".format(3 * numVertices), data[offset:offset + 12 * numVertices]))
            it = iter(vertices_list)
            vertices = list(zip(it, it, it)) # Creating a list of tuples containing X,Y,Z vertices
            vertices = [(x, -z, y) for x, y, z in vertices] # Converting coordinates between FF7's referential and Blender's
            offset += 12 * numVertices
            
            normals_list = list(struct.unpack("<{}f".format(3 * numNormals), data[offset:offset + 12 * numNormals]))
            it = iter(normals_list)
            normals = list(zip(it, it, it)) # Creating a list of tuples containing X,Y,Z vertices
            normals = [(x, -z, y) for x, y, z in normals] # Converting coordinates between FF7's referential and Blender's
            offset += 12 * numNormals + 12 * numUnknown1 # Avoiding unknown block

            texCoords_list = list(struct.unpack("<{}f".format(2 * numTexCoords), data[offset:offset + 8 * numTexCoords]))
            it = iter(texCoords_list)
            texCoords = list(zip(it, it)) # Tex coords are tuples of X and Y coordinates
            offset += 8 * numTexCoords
            
            vertexColors_list = list(struct.unpack("<{}c".format(4 * numVertexColors), data[offset:offset + 4 * numVertexColors]))
            it = iter(vertexColors_list)
            vertexColors = [
                (
                    int.from_bytes(r, byteorder="little")/255,
                    int.from_bytes(g, byteorder="little")/255,
                    int.from_bytes(b, byteorder="little")/255,
                    int.from_bytes(a, byteorder="little")/255
                )
                for b, g, r, a in zip(it, it, it, it)
                ] # Colors are stored as BGRA
            offset += 4 * numVertexColors
            
            # Uncomment this section if needed
            # polygonColors_list = list(struct.unpack("<{}c".format(4 * numPolys), data[offset:offset + 4 * numPolys]))
            # it = iter(polygonColors_list)
            # polygonColors = [{"b":int.from_bytes(b, byteorder="little"), "g":int.from_bytes(g, byteorder="little"), "r":int.from_bytes(r, byteorder="little"), "a":int.from_bytes(a, byteorder="little")} for b, g, r, a in zip(it, it, it, it)] # Colors are stored as BGRA
            offset += 4 * numPolys

            # Uncomment this section if needed
            # edges = list(struct.unpack("<{}I".format(numEdges), data[offset:offset + 4 * numEdges]))
            offset += 4 * numEdges
            
            polygons_list = list(struct.unpack("<{}H".format(12 * numPolys), data[offset:offset + 24 * numPolys]))
            it = iter(polygons_list)
            polygons = [
                { 
                "vertexIndex1":vertexIndex1, 
                "vertexIndex2":vertexIndex2, 
                "vertexIndex3":vertexIndex3, 
                "normalIndex1":normalIndex1, 
                "normalIndex2":normalIndex2, 
                "normalIndex3":normalIndex3, 
                "edgeIndex1":edgeIndex1, 
                "edgeIndex2":edgeIndex2, 
                "edgeIndex3":edgeIndex3 
                } 
                for _,
                    vertexIndex1,
                    vertexIndex2,
                    vertexIndex3,
                    normalIndex1,
                    normalIndex2,
                    normalIndex3,
                    edgeIndex1,
                    edgeIndex2,
                    edgeIndex3,
                    _,
                    _ 
                in zip(it, it, it, it, it, it, it, it, it, it, it, it)
            ]
            offset += 24 * numPolys + 24 * numUnknown2 + 3 * numUnknown3 + 100 * numHundreds # Avoiding Unknown2, Unknown3 and Hundreds
            
            groups_list = list(struct.unpack("<{}L".format(14 * numGroups), data[offset:offset + 56 * numGroups]))
            it = iter(groups_list)
            groups = [
                {
                    "primitiveType":primitiveType, 
                    "polygonStartIndex":polygonStartIndex, 
                    "numPolygons":numPolygons, 
                    "verticesStartIndex":verticesStartIndex, 
                    "numVertices":numVertices, 
                    "edgeStartIndex":edgeStartIndex, 
                    "numEdges":numEdges, 
                    "texCoordStartIndex":texCoordStartIndex, 
                    "areTexturesUsed":areTexturesUsed, 
                    "textureNumber":textureNumber
                } 
                for primitiveType,
                    polygonStartIndex,
                    numPolygons,
                    verticesStartIndex,
                    numVertices,
                    edgeStartIndex,
                    numEdges,
                    _,
                    _,
                    _,
                    _,
                    texCoordStartIndex,
                    areTexturesUsed,
                    textureNumber 
                in zip(it, it, it, it, it, it, it, it, it, it, it, it, it, it)
            ]
            offset += 56 * numGroups + 4
            
            # Uncomment this section if needed
            # boundingBoxes_list = list(struct.unpack("<{}f".format(6 * numBoundingBoxes), data[offset:offset + 24 * numBoundingBoxes]))
            # it = iter(boundingBoxes_list)
            # boundingBoxes = [[(max_x, max_y, max_z), (min_x, min_y, min_z)] for max_x, max_y, max_z, min_x, min_y, min_z in zip(it, it, it, it, it, it)]
            offset += 24 * numBoundingBoxes

            # Last section is Normal index table, unused

            self.polygonGroups = []
            for group in groups:
                polys = []
                gr_polygons = polygons[group["polygonStartIndex"]:group["polygonStartIndex"] + group["numPolygons"]] # Selecting group's polygons
                for polygon in gr_polygons:
                    # Adding vertices
                    vert1 = { 
                        "vertex":vertices[polygon["vertexIndex1"] + group["verticesStartIndex"]], 
                        "normal":normals[polygon["normalIndex1"]], 
                        "color":vertexColors[polygon["vertexIndex1"] + group["verticesStartIndex"]], 
                        "uv":texCoords[polygon["vertexIndex1"] + group["texCoordStartIndex"]] if group["areTexturesUsed"] else None
                    }

                    vert2 = { 
                        "vertex":vertices[polygon["vertexIndex2"] + group["verticesStartIndex"]], 
                        "normal":normals[polygon["normalIndex2"]], 
                        "color":vertexColors[polygon["vertexIndex2"] + group["verticesStartIndex"]], 
                        "uv":texCoords[polygon["vertexIndex2"] + group["texCoordStartIndex"]] if group["areTexturesUsed"] else None
                    }

                    vert3 = { 
                        "vertex":vertices[polygon["vertexIndex3"] + group["verticesStartIndex"]], 
                        "normal":normals[polygon["normalIndex3"]], 
                        "color":vertexColors[polygon["vertexIndex3"] + group["verticesStartIndex"]], 
                        "uv":texCoords[polygon["vertexIndex3"] + group["texCoordStartIndex"]] if group["areTexturesUsed"] else None
                    }

                    polys.append((vert1, vert2, vert3))
                
                self.polygonGroups.append({ 
                    "polygons":polys, 
                    "textureFile":textureFiles[group["textureNumber"]] if group["areTexturesUsed"] else None
                })
            
        @property
        def filename(self):
            return self.__filename

        @filename.setter
        def filename(self, filename):
            self.__filename = filename

        @property
        def polygonGroups(self):
            return self.__polygonGroups

        @polygonGroups.setter
        def polygonGroups(self, polygonGroups):
            self.__polygonGroups = polygonGroups

    class TextureFile:
        def __init__(self, filename, data):
            self.filename = filename

            # Loading header
            _, \
            _, \
            colorKeyFlag, \
            _, \
            _, \
            minBitsPerColor, \
            maxBitsPerColor, \
            minAlphaBits, \
            maxAlphaBits, \
            minBitsPerPixel, \
            maxBitsPerPixel, \
            _, \
            numPalettes, \
            numColorsPerPalette, \
            self.bitDepth, \
            self.width, \
            self.height, \
            _, \
            _, \
            paletteFlag, \
            bitsPerIndex, \
            _, \
            paletteSize, \
            _, \
            _, \
            bitsPerPixel, \
            bytesPerPixel = struct.unpack("<27L", data[:108])
            offset = 108 # Header is 108 bytes long

            # Every image in FF7 is supposed to be paletted, but you never know...
            if not paletteFlag:
                # Pixel format
                numRedBits, \
                numGreenBits, \
                numBlueBits, \
                numAlphaBits, \
                redBitmask, \
                greenBitmask, \
                blueBitmask, \
                alphaBitmask, \
                redShift, \
                greenShift, \
                blueShift, \
                alphaShift, \
                _, \
                _, \
                _, \
                _, \
                redMax, \
                greenMax, \
                blueMax, \
                alphaMax = struct.unpack("<20L", data[offset:offset + 80])

            offset += 80

            colorKeyArrayFlag, \
            _, \
            referenceAlpha = struct.unpack("<3L", data[offset:offset + 12])
            offset += 48 # Skipping unused bytes

            if paletteFlag:
                # Palette data
                paletteData_list = list(struct.unpack("<{}c".format(4 * paletteSize), data[offset:offset + 4 * paletteSize]))
                it = iter(paletteData_list)
                paletteData = [
                    (
                        int.from_bytes(r, byteorder="little")/255,
                        int.from_bytes(g, byteorder="little")/255,
                        int.from_bytes(b, byteorder="little")/255,
                        int.from_bytes(a, byteorder="little")/255 if a != '\xFE' else referenceAlpha
                    )
                    for b, g, r, a in zip(it, it, it, it)
                ] # Colors are stored as BGRA
                offset += 4 * paletteSize
            else:
                paletteData = None

            pixelData = []
            pixelData_ba = bytearray(data[offset:offset + self.width * self.height * bytesPerPixel])
            for i in range(0, self.width * self.height * bytesPerPixel, bytesPerPixel):
                pixelData.append(int.from_bytes(pixelData_ba[i:i + bytesPerPixel], byteorder="little"))
            offset += self.width * self.height * bytesPerPixel

            if colorKeyFlag and colorKeyArrayFlag:
                colorKeyArray = struct.unpack("<{}c".format(numPalettes), data[offset:offset + numPalettes])
            else:
                colorKeyArray = None

            self.pixels = [None] * self.width * self.height

            if paletteFlag:
                # Every value in pixelData is an index referencing the palette
                for i, index in enumerate(pixelData):
                    if colorKeyFlag and colorKeyArray:
                        # Update the colorKeyFlag according to the array
                        colorKeyFlag = colorKeyArray[index]

                    if colorKeyFlag and index == 0:
                        # The pixel needs to be transparent, aka having an alpha value of 0
                        self.pixels[i] = (0,0,0,0)
                    else:
                        # No color keying to perform
                        self.pixels[i] = paletteData[index]

                # Flatten the list of tuples
                self.pixels = list(sum(self.pixels, ()))
            else:
                pass # No idea how to use non-paletted data. Should not be used in FF7 anyway

        @property
        def filename(self):
            return self.__filename

        @filename.setter
        def filename(self, filename):
            self.__filename = filename

        @property
        def width(self):
            return self.__width

        @width.setter
        def width(self, width):
            self.__width = width

        @property
        def height(self):
            return self.__height

        @height.setter
        def height(self, height):
            self.__height = height

        @property
        def bitDepth(self):
            return self.__bitDepth

        @bitDepth.setter
        def bitDepth(self, bitDepth):
            self.__bitDepth = bitDepth

        @property
        def pixels(self):
            return self.__pixels

        @pixels.setter
        def pixels(self, pixels):
            self.__pixels = pixels

class Animation:
    def __init__(self, data):
        self.frames = []
        _, numFrames, self.numBones, firstRotation, secondRotation, thirdRotation = struct.unpack("<3I3c", data[:15])
        offset = 36 # Header's size
        # Converting rotations to X / Y / Z letters
        firstRotation = chr(int.from_bytes(firstRotation, byteorder="little") + 88)
        secondRotation = chr(int.from_bytes(secondRotation, byteorder="little") + 88)
        thirdRotation = chr(int.from_bytes(thirdRotation, byteorder="little") + 88)

        self.rotationOrder = "{}{}{}".format(firstRotation, secondRotation, thirdRotation)

        # Getting all frames info
        for _ in range(numFrames):
            rootRotation = list(struct.unpack("<3f", data[offset:offset + 12]))
            offset += 12
            rootTranslation = list(struct.unpack("<3f", data[offset:offset + 12]))
            offset += 12
            rotations_list = list(struct.unpack("<{}f".format(self.numBones * 3), data[offset:offset + self.numBones * 12]))
            it = iter(rotations_list)
            rotations = list(zip(it, it, it)) # Creating a list of tuples containing X,Y,Z rotations
            offset += self.numBones * 12
            self.frames.append({ 
                "rootRotation":rootRotation, 
                "rootTranslation":rootTranslation, 
                "bonesRotations":rotations 
            })

    @property
    def frames(self):
        return self.__frames

    @frames.setter
    def frames(self, frames):
        self.__frames = frames
    
    @property
    def numBones(self):
        return self.__numBones

    @numBones.setter
    def numBones(self, numBones):
        self.__numBones = numBones

    @property
    def rotationOrder(self):
        return self.__rotationOrder

    @rotationOrder.setter
    def rotationOrder(self, rotationOrder):
        self.__rotationOrder = rotationOrder

# Functions

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
    path = os.path.dirname(filepath)
    
    flevelLGP = LGPFile.fromFile(filepath)
    charFilepath = os.path.join(path, "char.lgp")
    if not os.path.exists(charFilepath):
        raise FileNotFoundError(charFilepath)
    charLGP = LGPFile.fromFile(charFilepath)
    models = {}

    for filename in flevelLGP.toc:
        # Avoiding non field files
        if filename in ("maplist", "flevel.siz") or os.path.splitext(filename)[1] in (".tut", ".tex"):
            continue
        try:
            field = LZSSFile(flevelLGP.getFileContent(filename))
        except:
            continue
        field = FieldModule(field.uncompressedData)

        for model in field.sections[3].models.values(): # Section 3 of Field Module is the Model Loader
            skeletonFile = model.skeletonFile.lower() # Getting the skeleton file's name
            # TODO : Remove this if, debug purpose
            if skeletonFile != "aaaa.hrc":
                continue
            if not skeletonFile in models:
                # We don't have the skeleton yet, we need to create it with an empty animations set
                try:
                    skeleton = HRCSkeleton(
                        os.path.splitext(skeletonFile)[0], 
                        charLGP.getFileContent(skeletonFile), 
                        charLGP
                    )
                except Exception as e:
                    print("Error creating HRCSkeleton {} : {}".format(skeletonFile, e))
                    raise
                animations = {}
            else:
                # We already know the current skeleton, we take it and its animations
                skeleton = models[skeletonFile]["skeleton"]
                animations = models[skeletonFile]["animations"]

            for animName in model.animations:
                animName = animName.lower()
                if not animName in animations: # No need to add already known animations
                    try:
                        animations[animName] = Animation(charLGP.getFileContent(animName))
                    except:
                        continue

            # Checking that animations have the same number of bones as skeleton
            # TODO : Replace this with animations = { k:v for k,v in animations.items() if skeleton.numBones == v.numBones }
            for animName in list(animations.keys()):
                if skeleton.numBones != animations[animName].numBones and not(skeleton.numBones == 1 and animations[animName].numBones == 0):
                    # For debugging purposes
                    print("ERROR : {} - {} {} has {} bones and its animation {} has {} bones.".format(filename, skeleton.name, skeletonFile, skeleton.numBones, animName, animations[animName].numBones))
                    # Removing the incorrect animation
                    del animations[animName]

            # Storing (eventually updated) character data
            character = { 
                "skeleton":skeleton, 
                "animations":animations 
            }
            models[skeletonFile] = character

    # Now we have all needed objects, we can work in Blender
    for model in models.values():
        # Adding a new Scene per model
        if model["skeleton"].filename in SKELETONS_NAMES:
            scene = bpy.data.scenes.new(SKELETONS_NAMES[model["skeleton"].filename])
        else:
            scene = bpy.data.scenes.new(model["skeleton"].filename)
        bpy.context.window.scene = scene
        viewLayer = bpy.context.view_layer

        # Creating meshes
        meshes = {}
        for bone in model["skeleton"].bones:
            if not bone.pFiles:
                continue
            for pFile in bone.pFiles:
                for i, polygonGroup in enumerate(pFile.polygonGroups):
                    # Creating a mesh for the current polygon group and linking it to the current scene
                    meshData = bpy.data.meshes.new(
                        "{}_{}".format(bone.name,i)
                    )
                    meshObj = bpy.data.objects.new(
                        "{}_mesh".format(meshData.name), 
                        meshData
                    )
                    scene.collection.objects.link(meshObj)

                    # Defining vertex colors
                    vertexColor = meshData.vertex_colors.new(
                        name="{}_col".format(meshData.name)
                    )

                    # Creating the UV Map
                    uv_layer = meshData.uv_layers.new(
                        name="{}_uv".format(meshData.name)
                    )

                    bm = bmesh.new()

                    # Array of BMesh vertices, used to avoid duplicates
                    verts = {}

                    # Getting information from polygons, 
                    for polygon in polygonGroup["polygons"]:
                        if polygon[0]["vertex"] not in verts:
                            vert1 = bm.verts.new(polygon[0]["vertex"])
                            vert1.normal = Vector(polygon[0]["normal"])

                            verts[polygon[0]["vertex"]] = vert1
                        else:
                            vert1 = [polygon[0]["vertex"]]

                        if polygon[1]["vertex"] not in verts:
                            vert2 = bm.verts.new(polygon[1]["vertex"])
                            vert2.normal = Vector(polygon[1]["normal"])

                            verts[polygon[1]["vertex"]] = vert2
                        else:
                            vert2 = [polygon[1]["vertex"]]

                        if polygon[2]["vertex"] not in verts:
                            vert3 = bm.verts.new(polygon[2]["vertex"])
                            vert3.normal = Vector(polygon[2]["normal"])

                            verts[polygon[2]["vertex"]] = vert3
                        else:
                            vert3 = [polygon[2]["vertex"]]
                    
                        # Mandatory functions after inserting vertices
                        bm.verts.index_update()
                        bm.verts.ensure_lookup_table()

                        # Defining a face (= polygon in FF7) for the mesh
                        bm.faces.new((vert1, vert2, vert3))
                        bm.faces.index_update()
                        bm.faces.ensure_lookup_table()

                    # Putting information from bmesh to mesh
                    bm.to_mesh(meshData)
                    bm.free()
                    
                    k = 0
                    for poly in meshData.polygons:
                        for _ in poly.loop_indices:
                            vertexColor.data[k].color = (
                                polygon[poly.index]["color"][0], 
                                polygon[poly.index]["color"][1], 
                                polygon[poly.index]["color"][2], 
                                polygon[poly.index]["color"][3]
                            )
                            k += 1

                    
                    for loop in meshData.loops:
                        if polygon[loop.index]["uv"]:
                            uv_layer.data[loop.index].uv = polygon[loop.index]["uv"]

                    # Creating image (= texture) and attach it to a material
                    if polygonGroup["textureFile"]:
                        image = bpy.data.images.new(
                            "{}_{}_tex".format(bone.name,i), 
                            width=polygonGroup["textureFile"].width, 
                            height=polygonGroup["textureFile"].height, 
                            alpha=True
                        )
                        image.source = "GENERATED"
                        image.file_format = "BMP"
                        image.pixels = polygonGroup["textureFile"].pixels
                        # TODO : Create material and associate it to mesh

                    # Storing the mesh object to link it later to the corresponding bone
                    if bone.name not in meshes:
                        meshes[bone.name] = [meshObj]
                    else:
                        meshes[bone.name].append(meshObj)

        # Adding armature to the scene
        armatureData = bpy.data.armatures.new(name=model["skeleton"].name+"_root") # The Armature will represent the root bone for transformation purposes
        armatureObj = bpy.data.objects.new(name=model["skeleton"].name, object_data=armatureData)
        viewLayer.active_layer_collection.collection.objects.link(armatureObj)
        armatureObj.select_set(True)
        viewLayer.objects.active = armatureObj
        bpy.ops.object.mode_set(mode="EDIT")
        # Adding bones to armature
        editBones = armatureData.edit_bones
        for bone in model["skeleton"].bones:
            parentName = bone.parent
            curBone = editBones.new(bone.name)
            curBone.length = bone.length
            if parentName != "root":
                curBone.translate(editBones[parentName].tail)
                curBone.parent = editBones[parentName]
                curBone.use_connect = True
            # Linking meshes to the corresponding bone
            bpy.ops.object.mode_set(mode="OBJECT") # Used to make sure bone exist before linking meshes to it
            if bone.name in meshes:
                for mesh in meshes[bone.name]:
                    mesh.parent = armatureObj
                    mesh.parent_bone = bone.name
                    mesh.parent_type = 'BONE'
                    constraint = mesh.constraints.new('COPY_TRANSFORMS')
                    constraint.target = armatureObj
                    constraint.subtarget = bone.name
            bpy.ops.object.mode_set(mode="EDIT") # Switching back to Edit mode before looping

        viewLayer.objects.active = armatureObj
        bpy.ops.object.mode_set(mode="OBJECT") # Used to validate the Edit mode stuff
        
        # Defining bones' rotations
        bpy.ops.object.mode_set(mode="POSE")
        armatureObj.rotation_mode = "QUATERNION"
        for animation in model["animations"].values():
            # For each animation, create it frame by frame
            for numFrame in range(len(animation.frames)):
                # Defining root rotation
                x, y, z = animation.frames[numFrame]["rootRotation"]
                armatureObj.rotation_quaternion = ff7RotationToQuaternion(x, y, z)
                armatureObj.keyframe_insert("rotation_quaternion", frame = numFrame + 1)
                # And root translation
                armatureObj.location = animation.frames[numFrame]["rootTranslation"]
                armatureObj.keyframe_insert("location", frame = numFrame + 1)
                # And finally bones' rotations
                for bone in model["skeleton"].bones:
                    curPoseBone = armatureObj.pose.bones[bone.name]
                    pos = model["skeleton"].bones.index(bone) # Getting bone's position in list, which matches rotation's position in the animation
                    if pos < len(animation.frames[numFrame]["bonesRotations"]): # Avoiding index error
                        x, y, z = animation.frames[numFrame]["bonesRotations"][pos]
                        curPoseBone.rotation_quaternion = ff7RotationToQuaternion(x, y, z)
                        curPoseBone.keyframe_insert("rotation_quaternion", frame = numFrame + 1)
            if len(animation.frames): # If we have at least one frame
                scene.frame_end = len(animation.frames)
            break # TODO : Remove this, only for debugging purposes
            
        # Set the space to Vertex mode to display colors
        for area in bpy.data.workspaces['Layout'].screens[0].areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.color_type = 'VERTEX'
    return {'FINISHED'}

# Code taken from Blender import template

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

class ImportLGP(Operator, ImportHelper):
    """Import flevel file in LGP file format (*flevel.lgp)"""
    bl_idname = "import_lgp.import_scenes"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import flevel LGP"

    # ImportHelper mixin class uses this
    filename_ext = ".lgp"

    filter_glob: StringProperty(
        default="*flevel.lgp",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        return importLgp(context, self.filepath)


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportLGP.bl_idname, text="flevel LGP files (*flevel.lgp)")


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
