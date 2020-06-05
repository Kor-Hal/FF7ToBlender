# Blender addon definition

bl_info = {
    "name": "Final Fantasy 7 flevel LGP import/export",
    "author": "Sébastien Dougnac",
    "blender": (2, 82, 0),
    "location": "File > Import-Export",
    "description": "Import-Export flevel LGP models and animations",
    "warning": "",
    "support": 'TESTING',
    "category": "Import-Export"
}

# Imports

import bmesh, bpy, math, os, struct
from mathutils import Matrix, Quaternion, Vector

# Constants

# The following dictionary is taken from Kujata
# https://github.com/picklejar76/kujata/blob/master/friendly-names-db/skeleton-friendly-names.json

SKELETONS_NAMES = {
    "aaaa": "Cloud",
    "aagb": "Tifa",
    "abda": "Cid",
    "abjb": "Yuffie",
    "acgd": "Barret",
    "adda": "Red XIII",
    "aebc": "Cait Sith",
    "aehd": "Vincent",
    "afec": "Bugenhagen",
    "afie": "Cloud Parachute",
    "aggb": "Tifa Parachute",
    "ahdf": "Yuffie Parachute",
    "aiba": "Barret Parachute",
    "aihb": "Cid Parachute",
    "ajif": "Skinny Highwind Crewman",
    "akee": "Burly Highwind Crewman",
    "alad": "Rufus",
    "algd": "Heidegger",
    "amcc": "Scarlet",
    "anbd": "Hojo",
    "anic": "Rude",
    "aodd": "Reno",
    "aqgc": "Chocobo",
    "arfd": "Sleeping Old Man",
    "asbf": "Tanned Midgar Man",
    "asjc": "Chocobo Sage",
    "ateb": "Command Materia",
    "atfe": "Lucretia in Cave",
    "auda": "Handgun",
    "aude": "Independent Materia",
    "auff": "Aeris",
    "avfe": "Save Point",
    "avhe": "Traditional Chest",
    "awae": "Green Chest",
    "awbe": "Summon Materia",
    "awcb": "Hojo Assistant",
    "awhf": "President Shinra",
    "axdc": "Jessie",
    "axja": "Tifa Corneo",
    "ayfb": "Barret Sailor",
    "azbb": "Aeris Corneo",
    "azhe": "Train Guard",
    "badd": "Honey Bee Girl",
    "bbab": "Sephiroth w/Sword",
    "bbge": "Costa Bar Girl",
    "bccf": "Ancient Temple Guard",
    "bcgd": "Shinra Sailor",
    "bdcd": "Mr. Dolphin",
    "bdga": "Cat",
    "beec": "Mideel Dog (Grey)",
    "bfca": "Johnny's Dad",
    "bfhe": "Sector 7 Shop Owner",
    "bgdc": "Shera",
    "bgjc": "Sephiroth w/Jenny Head",
    "bhff": "Cloud w/Buster Sword",
    "bidb": "Tifa Cowgirl",
    "bijd": "Vincent Turk",
    "bjfb": "Cloud's Mom",
    "bkbf": "Priscilla",
    "bkhd": "Sephiroth",
    "blde": "Tifa's Father's Friend",
    "bljc": "Mideel Doctor",
    "bmee": "Little Girl",
    "bnaf": "ZANGAN",
    "bngd": "Dyne w/Gun",
    "bocc": "Grey Peasant",
    "bohe": "Icicle Inn Woman/Mother",
    "bpdc": "Muscle-Man (Blonde)",
    "bpjd": "Reeve",
    "bqfb": "Blue Villager",
    "braf": "Cloud's House Occupant",
    "brgd": "Motorcycle...",
    "brib": "Cloud Motorcycle (Jesus)",
    "bsfc": "Female Villager",
    "btec": "Female Nurse",
    "buac": "Young Tifa",
    "buge": "Young Cloud",
    "bvda": "Tifa's Father",
    "bwab": "Shinra Soldier",
    "bwfd": "Biggs",
    "bxbe": "Wedge",
    "bxjb": "Train Door",
    "byba": "Slab",
    "bybf": "Panel w/Lights",
    "bycd": "Catwalk Grating",
    "bydd": "Gold Chest",
    "bygf": "Blue Potion",
    "byib": "Magic Materia",
    "bzda": "AIR BUSTER!",
    "bzhf": "Shinra Beta Copter",
    "cade": "Catwalk Grating",
    "cahc": "Aeris w/Flower Basket",
    "cbfe": "Red hair hooker",
    "ccbc": "Red Punk",
    "ccha": "Light Blue Potion",
    "cdja": "Shinra Manager",
    "cefd": "Train Drunk",
    "cfbb": "Phoenix Down Hobo",
    "cfha": "Honey Bee Guard/Punk",
    "cgda": "Sector 7 Kid",
    "cgif": "Red Cap Tifa friend",
    "ched": "Chole",
    "ciac": "Hi-Potion Dealer",
    "cige": "Biggs Train Disguise",
    "cjcc": "Wedge Train Disguise",
    "cjif": "Johnny",
    "ckfc": "Costa Guy",
    "clbb": "Costa Surf Bro",
    "clgd": "Tall Cloud Field",
    "cmde": "Tall Jessie Field",
    "cmif": "Tanned Guy",
    "cned": "Item Bag",
    "cnfb": "Moving Train (Train Graveyard)",
    "cnhf": "Train Carriage (Train Graveyard)",
    "coad": "Housewife Purple",
    "cogb": "Elmyra",
    "cpca": "Child, Red dungarees",
    "cpjf": "Ifalna",
    "cqga": "Kid Aeris",
    "crca": "Tifa's Father's Friend",
    "crid": "Tracksuit Man",
    "csed": "Cosmo Miner Repairman csga",
    "ctbe": "Magic Materia",
    "ctcc": "Gold Saucer F. Attendant",
    "ctib": "Hall; Kid Opponent",
    "cufc": "Hall; Black Flexer",
    "cvba": "Hall; Burly Flexer",
    "cvge": "Hall; Punk Flexer",
    "cwed": "Sector 7 Busy-body",
    "cyae": "Marlene",
    "cyif": "Mr. Duffi-look alike",
    "czed": "Avalanche Hideout: Pinball Machine",
    "czgb": "Yellow Rectangle",
    "czgf": "Flowers",
    "dabf": "Green Materia",
    "dafb": "Cologne Lady",
    "dbec": "Tseng",
    "dcce": "Pillar Collapse Hook-Swing",
    "dcfb": "Bright Green Potion",
    "dcic": "Tanned Guy NPC",
    "ddha": "This guy are sick",
    "deda": "Clothes Shop Son",
    "deie": "Dog (Brown)",
    "dfgd": "Tiara Guy",
    "dgcd": "Nibel Kids Boy",
    "dhaf": "Reno (No Face)",
    "dhge": "Barrel",
    "dhhf": "Ladder",
    "dhid": "Rocky Caltrops",
    "diff": "Kid Aeris, Brown Dress",
    "djfa": "Claw in Golden Saucer Claw-Game",
    "djfe": "Girder",
    "djid": "Chocobo Carriage",
    "dkie": "Metal Flooring (4)",
    "dkjd": "Metal Flooring (7)",
    "dlfb": "Cloud Corneo",
    "dmcb": "Old tanned guy",
    "dmia": "Miner/Jon-Tron",
    "dndf": "Black Muscle-man",
    "dnje": "Mukki",
    "doga": "Battle Model-Like Hand",
    "doib": "Female Trenchcoat NPC doje",
    "dpef": "Chef in Wall Market",
    "dqae": "Accessory Maid",
    "dqgd": "Diner at Wall Market",
    "drcc": "Rocket Technician",
    "dria": "Meal A TEX Wall Market",
    "drif": "Meal B TEX Wall Market",
    "drje": "Meal C TEX Wall Market",
    "dsbc": "Kalm Chef",
    "dsgf": "Junon Old Inn Lady",
    "dtce": "High-Collar NPC",
    "dtic": "Propellor (Green)",
    "dtjb": "Honey Bee Manager",
    "dufa": "Scotch",
    "dvbe": "Kotch",
    "dvhf": "Don Corneo",
    "dxbd": "Shinra Soldier Rifle",
    "dxje": "Daughter Honey Bee Room",
    "dyfd": "King Shinra",
    "dzbb": "Knight",
    "dzgf": "Shinra Manager Alt",
    "eaga": "Broken Propellor, Climb to Shinra Tower",
    "eagf": "Swinging Beam, Climb to Shinra Tower",
    "eaid": "Shinra Alpha Copter",
    "ebca": "Beam of light",
    "ebec": "Choco Billy",
    "ebjf": "Door/Panel Shinra Tower?",
    "ecae": "Ditto",
    "ecbf": "Turqouise Dress NPC",
    "echd": "Shinra Tower Glass Elevator",
    "ecib": "Shinra Secretary",
    "edea": "Woman fl60",
    "edjd": "Old Man",
    "eefb": "Construct, maybe a paddock",
    "eegc": "Palmer",
    "effb": "Grate Toilet 66th Floor",
    "eghe": "Masamune (President Shinra Dead)",
    "ehbe": "Tracksuit NPC",
    "ehhc": "Black-Cloaked Man",
    "eiac": "Red Woman NPC",
    "eihd": "Cloud, Helmet in Hands, on Truck",
    "ejdc": "Zack w/sword",
    "ekbf": "MP Cloud",
    "ekjb": "Young Hojo",
    "elgc": "Young Gast",
    "emdf": "Corel Miner",
    "enab": "Young Cloud Black Shirt",
    "eoac": "Key",
    "eoce": "Vincent Coffin lid",
    "eoea": "Sephiroth with book",
    "epfb": "Materia Keeper",
    "eqib": "Cowgirl Tifa w/Masamune",
    "erha": "Sephy w/Jenny Head",
    "eseb": "MP Cloud w/Sword",
    "etfe": "Blue Child, No Face",
    "euaf": "Red Child, No Face",
    "euhb": "Crazy old guy!",
    "evfe": "Elena",
    "ewbd": "Corel Burly Miner",
    "ewje": "Corel Miner Wife",
    "exga": "Small Condor",
    "eyie": "Rufus' Car",
    "ezcc": "Patchwork Cat",
    "faae": "Cyan Potion",
    "fabb": "Red Potion",
    "fabe": "Green Potion",
    "facc": "Black Propellor/Untex",
    "fadc": "Yellow Potion",
    "fbba": "Journalist Male",
    "fbge": "Cait Sith Journalist",
    "fcaf": "Journalist Female",
    "fcgd": "Cameraman",
    "feea": "Yuffie Journalist",
    "ffec": "Small Green Fish",
    "ffha": "Yellow/Red Shoal",
    "fgae": "Shark",
    "fgec": "Metal Door",
    "fgfb": "Crane Claw",
    "fghf": "Huge Materia Capsule Underwater Reactor",
    "fhaa": "Carry Armour",
    "fhic": "Door/Panel",
    "fhjb": "Door/Panel 1",
    "fiba": "Bottomswell",
    "fjaf": "Red Light",
    "fjbd": "Lung Meter CPR",
    "fjcf": "Red XIII Soldier Disguise",
    "fkca": "Jenova Tentacle",
    "fkdf": "Hojo Groupie lying down",
    "flac": "Costa Entrance Girl",
    "flge": "Costa Beach girl",
    "fmcc": "Snorkel Kid",
    "fmib": "Swimsuit kid",
    "fndf": "Football",
    "fnef": "Sector 7 Wep Shop Shooter",
    "fobe": "Layabout",
    "fpcb": "Catastrophe Corel girl",
    "fqab": "Long Train, Corel Chase",
    "fqbb": "Cid's Train, Corel Chase",
    "fqcb": "Barret, Corel Flashback",
    "fqjb": "Dyne, Corel Flashback frae",
    "frgd": "Corel Mayor",
    "fsdd": "Pink Potion",
    "fsge": "Corel Miner, slumped",
    "ftcf": "Corel Miner",
    "ftic": "Corel Miner, female",
    "fufe": "Corel Miner/Punk",
    "fved": "Mr. Coates",
    "fwae": "Ester",
    "fwgf": "Dyne's Pendant",
    "fxjc": "Gold Saucer Guard",
    "fzcc": "EDK",
    "gabe": "Play Wizard",
    "gajc": "Dio",
    "gbia": "G.Saucer Bird-Suit",
    "gcbd": "Male Attendant",
    "gchc": "G.Saucer Coaster",
    "gcjc": "Gondola Texture",
    "gdic": "Bat",
    "gebb": "Hotel Greeter/Lurch",
    "gehd": "Hotel Desk/Igor",
    "gfdf": "Mr. Hangman",
    "ggef": "Elixir Cabinet Door-right",
    "ggfe": "Ditto, Left door",
    "gghe": "Hand Pointer Tex",
    "ggid": "Purple shaft of light",
    "ggjc": "Yellow shaft of light (Battle Square)",
    "ghad": "Battle Square, f.kicker",
    "ghgf": "G.Saucer Capture Device",
    "giha": "ZANGIEF!",
    "gjab": "E.HONDA!",
    "gjcf": "Basketball",
    "gjeb": "Speed Bike, Field",
    "gjha": "3D Battler, Rookie",
    "gkcf": "3D Battler, Luchadore gkec",
    "gkid": "3D Battler, Afro Thunder",
    "gleb": "3D Battler, Super Hero",
    "gljd": "Mog",
    "gmha": "Pink Mog",
    "gnca": "Bright Mog",
    "gngb": "Yellow Mog",
    "goac": "Pink Mog",
    "gofd": "Choco Square Teller",
    "gpcd": "Joe",
    "gpjb": "Blue Jockey",
    "gqfe": "Green Jockey",
    "grcc": "Choco Elevator (From Corel Prison)",
    "grga": "Cosmo Canyon Greeter",
    "gsbe": "Cosmo Kid",
    "gshc": "Cosmo Propellor",
    "gsje": "Cosmo Mother",
    "gtfc": "Cosmo Elderly Lady",
    "guba": "Cosmo Kid Boy",
    "guhc": "Cosmo Door",
    "guib": "Cosmo Door",
    "gujc": "Glacier Map",
    "gvae": "Radar Dish",
    "gvbc": "Weather Vane",
    "gvce": "Yellow Huge Materia",
    "gvdc": "Green Huge Materia",
    "gvea": "Red Huge Materia",
    "gvee": "Blue Huge Materia",
    "gwaa": "Cosmo Observatory Planet/Two Moons",
    "gwcc": "Bugenhagen Lying down (Green orb missing)",
    "gwib": "Green orb",
    "gwif": "Rocket Town Citizen",
    "gxef": "Rocket Town Bored Citizen gxgc",
    "gydc": "Rocket Town Citizen",
    "gzad": "Young Cid",
    "gzgb": "Door Base; Rocket",
    "gzha": "Door Base; Rocket",
    "gzhf": "Rocket Technician",
    "hagb": "Rocket Huge Materia Capsule",
    "hcef": "Debris, pins Cid",
    "hdbb": "Wutai Citizen male",
    "hdgf": "Wutai Citizen, Staniv hdic",
    "hecd": "Wutai Citizen, Chekhov",
    "heib": "Wutai Citizen female",
    "hffb": "Wutai Citizen, Gorki",
    "hgaf": "Wutai Citizen, Shake",
    "hgia": "Yuffie House Cage",
    "hgjd": "Godo",
    "hhge": "Wutai Door",
    "hhhd": "Wutai Door",
    "hhic": "Wutai Panel",
    "hhjf": "Corneo Ninja",
    "hjdc": "Component, Gong-mechanism possibly",
    "hjga": "Ancient Temple Chest",
    "hjhf": "Rolling Stone",
    "hjie": "Clock, Minute/Sec Hand",
    "hjjd": "Clock, Minute/sec Hand",
    "hkac": "Clock, Hour Hand",
    "hkbb": "Clock core, base",
    "hkea": "Clock Core, mouth",
    "hkhb": "Temple Puzzle",
    "hkjc": "Demon Wall",
    "hlfc": "Green Digger",
    "hmbe": "Purple Digger",
    "hmif": "Ancient Forest, Fly",
    "hnaf": "Ancient FOrest, Frog",
    "hneb": "Ancient Forest, Tongue Feeler",
    "hnif": "Ancient Forest, Bee Hive",
    "hobd": "Ancient Key",
    "hpce": "Icicle Kid Girl",
    "hpib": "Icicle Man",
    "hqgc": "Blue Panel",
    "hqhc": "Snowboard",
    "hrae": "Red Flag",
    "hrce": "Blue Chest",
    "hree": "Tumbling Rock",
    "hrff": "Ice Stalagmite",
    "hrha": "Ice Stalagmite",
    "hrhe": "Ice Stalagmite",
    "hseb": "Ice Stalagmite",
    "hsjd": "Ultimate Weapon",
    "htje": "Handicapable Cloud",
    "hvcf": "Train Cars, Corel Chase",
    "hvjf": "Red XIII Para Freefall",
    "hwib": "Parachute open texture",
    "hxbc": "Proud Clod",
    "hyfd": "Jenova Synthesis",
    "iajd": "Yellow Projectile (Diamond Wep Attacks)",
    "ibad": "Zack, no sword",
    "ibgd": "Zack, w/sword"
}

# Classes

class LGPFile:
    def __init__(self, data):
        self.toc = {}
        offset = 12 # Ignoring the first 12 bytes (File creator)
        nb_files, = struct.unpack("<I", data[offset:offset + 4])
        offset += 4
        if nb_files > 0: # If we have at least one file, we process the first one's information outside of the loop
            filename, first_offset = struct.unpack("<20sI", data[offset:offset + 24])
            filename = filename.decode("utf-8").rstrip('\x00')
            offset += 24
            self.toc[filename] = first_offset
            offset += 3 # Avoiding useless information
        for _ in range(nb_files - 1): # Now we process all remaining files
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

        _, nbSections, sec1off, sec2off, sec3off, sec4off, sec5off, sec6off, sec7off, sec8off, sec9off = struct.unpack("<H10I", data[:42])
        if nbSections != 9:
            raise ValueError("The Field Module must have exactly 9 sections ({} encountered)".format(nbSections))
        
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
            _, nbModels, _ = struct.unpack("<3H", data[:6]) # Header
            offset = 6 # Position after header
            self.models = {}

            for _ in range(nbModels):
                modelNameSize, = struct.unpack("<H", data[offset:offset + 2])
                offset += 2
                modelName, _, skeletonFile, _, nbAnim, lightColor1, _, lightColor2, _, lightColor3, _, globalLightColor = struct.unpack("<{}sH8s4sH3s6s3s6s3s6s3s".format(modelNameSize), data[offset:offset + modelNameSize + 46])
                offset += modelNameSize + 46
                anim = []
                for _ in range(nbAnim):
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
        self.pFile = None
        self.texFiles = None

        hrcLines = hrcData.decode("utf-8").splitlines()
        
        hrcLines = [hrcLine for hrcLine in hrcLines if hrcLine[:1] != "#"] # Removing comments

        self.name = hrcLines[1].split(" ")[1]
        self.nbBones = int(hrcLines[2].split(" ")[1])
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
                pFile = None
                texList = None
                if int(rsd[0]) > 0:
                    rsdFiles = [i.lower() + ".rsd" for i in rsd[1:]] # Get list of RSD files
                    for rsdFile in rsdFiles:
                        try:
                            rsdLines = charLGPFile.getFileContent(rsdFile).decode("utf-8").splitlines()
                        except:
                            continue

                        rsdLines = [rsdLine for rsdLine in rsdLines if rsdLine[:1] != "#"] # Removing comments

                        # The .P file can be deduced from either PLY, GRP or MAT section
                        # I chose PLY because it's the first one
                        pFile = [i.lower() for i in rsdLines if i.startswith("PLY=")][0]
                        pFile = os.path.splitext(pFile)[0] + ".p"

                        # The NTEX section gives us the number of texture files
                        nbTex = int([i for i in rsdLines if i.startswith("NTEX=")][0][5:])
                        if nbTex > 0:
                            # We use list comprehension to extract TEX files' names
                            texList = [i[i.find("=") + 1:i.find(".")].lower() + ".tex" for i in rsdLines if i.startswith("TEX[")]
            
                if name != "" and parent != "" and length != 0.0:
                    bone = self.HRCBone(name, parent, length, pFile, texList)
                    self.bones.append(bone)
            
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
    def nbBones(self):
        return self.__nbBones
    
    @nbBones.setter
    def nbBones(self, nbBones):
        self.__nbBones = nbBones if nbBones > 0 else 1 # Default number of bones is 1
        
    @property
    def bones(self):
        return self.__bones
        
    @bones.setter
    def bones(self, bones):
        self.__bones = bones
        
    class HRCBone:
        def __init__(self, name, parent, length, pFile, texFiles):
            self.name = name
            self.parent = parent
            self.length = length
            self.pFile = pFile
            self.texFiles = texFiles
            
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
        def pFile(self):
            return self.__pFile

        @pFile.setter
        def pFile(self, pFile):
            self.__pFile = pFile

        @property
        def texFiles(self):
            return self.__texFiles

        @texFiles.setter
        def texFiles(self, texFiles):
            self.__texFiles = texFiles

    class PFile:
        def __init__(self, filename, charLGPFile):
            data = charLGPFile.getFileContent(filename)
            _, vertexType, nbVertices, nbNormals, nbUnknown1, nbTexCoords, nbVertexColors, nbEdges, nbPolys, nbUnknown2, nbUnknown3, nbHundreds, nbGroups, nbBoundingBoxes = struct.unpack("<Q13L", data[:60])
            offset = 128 # Header is 128 bytes long
            #self.bmesh = bmesh.new()
            vertices_list = list(struct.unpack("<{}f".format(3 * nbVertices), data[offset:offset + 12 * nbVertices]))
            offset += 12 * nbVertices
            it = iter(vertices_list)
            vertices = list(zip(it, it, it)) # Creating a list of tuples containing X,Y,Z vertices
            #for i, vertex in enumerate(vertices): # Adding vertices to the bmesh
            #    vert = self.bmesh.verts.new(co=vertex)
            #    vert.index = i # Ensuring the insertion order is the same as in the file
            #self.bmesh.ensure_lookup_table() # Mandatory after adding vertices
            normals_list = list(struct.unpack("<{}f".format(3 * nbNormals), data[offset:offset + 12 * nbNormals]))
            offset += 12 * nbNormals + 12 * nbUnknown1 # Avoiding unknown block
            it = iter(normals_list)
            normals = list(zip(it, it, it)) # Creating a list of tuples containing X,Y,Z vertices
            #for i, normal in enumerate(normals):
            #    self.bmesh.verts[i].normal = Vector(normal)
            texCoords_list = list(struct.unpack("<{}f".format(2 * nbTexCoords), data[offset:offset + 8 * nbTexCoords]))
            offset += 8 * nbTexCoords
            it = iter(texCoords_list)
            texCoords = list(zip(it, it)) # Tex coords are tuples of X and Y coordinates
            vertexColors_list = list(struct.unpack("<{}c".format(4 * nbVertexColors), data[offset:offset + 4 * nbVertexColors]))
            offset += 4 * nbVertexColors
            it = iter(vertexColors_list)
            vertexColors = [{"b": int.from_bytes(b, byteorder="little"), "g": int.from_bytes(g, byteorder="little"), "r": int.from_bytes(r, byteorder="little"), "a": int.from_bytes(a, byteorder="little")} for b, g, r, a in zip(it, it, it, it)] # Colors are stored as BGRA
            polygonColors_list = list(struct.unpack("<{}c".format(4 * nbPolys), data[offset:offset + 4 * nbPolys]))
            offset += 4 * nbPolys
            it = iter(polygonColors_list)
            polygonColors = [{"b": int.from_bytes(b, byteorder="little"), "g": int.from_bytes(g, byteorder="little"), "r": int.from_bytes(r, byteorder="little"), "a": int.from_bytes(a, byteorder="little")} for b, g, r, a in zip(it, it, it, it)] # Colors are stored as BGRA
            edges = [struct.unpack("<{}I".format(nbEdges), data[offset:offset + 4 * nbEdges])]
            offset += 4 * nbEdges
            polygons_list = list(struct.unpack("<{}H".format(12 * nbPolys), data[offset:offset + 24 * nbPolys]))
            offset += 24 * nbPolys + 24 * nbUnknown2 + 3 * nbUnknown3 + 108 * nbHundreds # Avoiding Unknown 2, 3 and Hundreds
            it = iter(polygons_list)
            polygons = [{"vertexIndex1":vertexIndex1, "vertexIndex2":vertexIndex2, "vertexIndex3":vertexIndex3, "normalIndex1":normalIndex1, "normalIndex2":normalIndex2, "normalIndex3":normalIndex3, "edgeIndex1":edgeIndex1, "edgeIndex2":edgeIndex2, "edgeIndex3":edgeIndex3} for _, vertexIndex1, vertexIndex2, vertexIndex3, normalIndex1, normalIndex2, normalIndex3, edgeIndex1, edgeIndex2, edgeIndex3, _, _ in zip(it, it, it, it, it, it, it, it, it, it, it, it)]
            groups_list = list(struct.unpack("<{}L".format(14 * nbGroups), data[offset:offset + 56 * nbGroups]))
            offset += 56 * nbGroups
            it = iter(groups_list)
            groups = [{"primitiveType":primitiveType, "polygonStartIndex":polygonStartIndex, "nbPolygons":nbPolygons, "verticesStartIndex":verticesStartIndex, "nbVertices":nbVertices, "edgeStartIndex":edgeStartIndex, "nbEdges":nbEdges, "texCoordStartIndex":texCoordStartIndex, "areTexturesUsed":areTexturesUsed, "textureNumber":textureNumber} for primitiveType, polygonStartIndex, nbPolygons, verticesStartIndex, nbVertices, edgeStartIndex, nbEdges, _, _, _, _, texCoordStartIndex, areTexturesUsed, textureNumber in zip(it, it, it, it, it, it, it, it, it, it, it, it, it, it)]
            boundingBoxes_list = list(struct.unpack("<{}f".format(6 * nbBoundingBoxes), data[offset:offset + 24 * nbBoundingBoxes]))
            offset += 24 * nbBoundingBoxes
            it = iter(boundingBoxes_list)
            boundingBoxes = [[(max_x, max_y, max_z), (min_x, min_y, min_z)] for max_x, max_y, max_z, min_x, min_y, min_z in zip(it, it, it, it, it, it)]
            # Last section is Normal index table, unused

class Animation:
    def __init__(self, data):
        self.frames = []
        _, nbFrames, self.nbBones, firstRotation, secondRotation, thirdRotation = struct.unpack("<3I3c", data[:15])
        offset = 36 # Header's size
        # Converting rotations to X / Y / Z letters
        firstRotation = chr(int.from_bytes(firstRotation, byteorder="little") + 88)
        secondRotation = chr(int.from_bytes(secondRotation, byteorder="little") + 88)
        thirdRotation = chr(int.from_bytes(thirdRotation, byteorder="little") + 88)

        self.rotationOrder = "{}{}{}".format(firstRotation, secondRotation, thirdRotation)

        # Getting all frames info
        for _ in range(nbFrames):
            rootRotation = list(struct.unpack("<3f", data[offset:offset + 12]))
            offset += 12
            rootTranslation = list(struct.unpack("<3f", data[offset:offset + 12]))
            offset += 12
            rotations_list = list(struct.unpack("<{}f".format(self.nbBones * 3), data[offset:offset + self.nbBones * 12]))
            it = iter(rotations_list)
            rotations = list(zip(it, it, it)) # Creating a list of tuples containing X,Y,Z rotations
            offset += self.nbBones * 12
            self.frames.append({ "rootRotation" : rootRotation, "rootTranslation" : rootTranslation, "bonesRotations" : rotations })

    @property
    def frames(self):
        return self.__frames

    @frames.setter
    def frames(self, frames):
        self.__frames = frames
    
    @property
    def nbBones(self):
        return self.__nbBones

    @nbBones.setter
    def nbBones(self, nbBones):
        self.__nbBones = nbBones

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
            skeletonFile = model.skeletonFile.lower() # Gettig the skeleton file's name
            if not skeletonFile in models:
                # We don't have the skeleton yet, we need to create it with an empty animations set
                try:
                    skeleton = HRCSkeleton(os.path.splitext(skeletonFile)[0], charLGP.getFileContent(skeletonFile), charLGP)
                except:
                    continue
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
            # TODO : Replace this with animations = { k:v for k,v in animations.items() if skeleton.nbBones == v.nbBones }
            for animName in list(animations.keys()):
                if skeleton.nbBones != animations[animName].nbBones and not(skeleton.nbBones == 1 and animations[animName].nbBones == 0):
                    # For debugging purposes
                    print("ERROR : {} - {} {} has {} bones and its animation {} has {} bones.".format(filename, skeleton.name, skeletonFile, skeleton.nbBones, animName, animations[animName].nbBones))
                    # Removing the incorrect animation
                    del animations[animName]

            # Storing (eventually updated) character data
            character = { "skeleton" : skeleton, "animations" : animations }
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
        viewLayer.objects.active = armatureObj
        bpy.ops.object.mode_set(mode="OBJECT") # Used to validate the Edit mode stuff. Not sure if really needed
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
        viewLayer.objects.active = armatureObj
        bpy.ops.object.mode_set(mode="OBJECT")
            
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
