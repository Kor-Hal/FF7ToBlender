# Blender addon definition

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

# Imports

import bpy
import math
import os
import struct
from mathutils import Matrix, Quaternion

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
            filename, file_offset = struct.unpack("<20sI", data[offset:offset + 24])
            filename = filename.decode("utf-8").rstrip('\x00')
            offset += 24
            if file_offset < first_offset:
                first_offset = file_offset
            self.toc[filename] = file_offset
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
        file_offset = 4
        if len(data) - 4 != header:
            raise ValueError("Not a valid LZSS file : File size {} doesn't match header's information {}".format(len(data), header + 4))
            
        buffer = bytearray(4096)
        bufferPos = int("0xFEE", 0)

        # Format : https://en.wikipedia.org/wiki/Lempel%E2%80%93Ziv%E2%80%93Storer%E2%80%93Szymanski
        # Each block of data consists of 1 Control Byte and 8 pieces of data (of variable lengths)
        while file_offset < len(data):
            controlByte = data[file_offset]
            file_offset += 1
            controlBits = bin(int.from_bytes(controlByte, byteorder="little"))[2:].zfill(8)
            for bit in reversed(controlBits): # Bits are read LSB-first
                if bit == "1": # Literal data
                    buffer[bufferPos] = int.from_bytes(data[file_offset], byteorder="little")
                    file_offset += 1
                    self.uncompressedData.append(buffer[bufferPos])
                    bufferPos += 1
                    bufferPos &= (len(buffer) - 1) # If we reach the last index, we start at 0
                else: # Reference
                    ref = data[file_offset:file_offset + 2]
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
    def __init__(self, filename, name, nb_bones):
        self.filename = filename
        self.name = name
        self.nb_bones = nb_bones
        self.bones = {}
        self.p_file = None
        self.tex_files = None
    
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

class HRCBone:
    def __init__(self, name, parent, length, p_file, tex_files):
        self.name = name
        self.parent = parent
        self.length = length
        self.p_file = p_file
        self.tex_files = tex_files
        
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
    def p_file(self):
        return self.__p_file

    @p_file.setter
    def p_file(self, p_file):
        self.__p_file = p_file

    @property
    def tex_files(self):
        return self.__tex_files

    @tex_files.setter
    def tex_files(self, tex_files):
        self.__tex_files = tex_files

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
    
    flevel = LGPFile(filepath)
    char_filepath = os.path.join(path, "char.lgp")
    if not os.path.exists(char_filepath):
        raise FileNotFoundError(char_filepath)
    char = LGPFile.fromFile(char_filepath)
    models = []

    for filename in flevel.toc:
        field = LZSSFile(flevel.getFileContent(filename))
        field = FieldModule(field.uncompressedData)

        for model in field.sections[3].models.items(): # Section 3 of Field Module is the Model Loader
            
            hrcFile = model.skeletonFile.lower()


            hrc_lines = lgp_file.getFileContent(hrc_file).decode("utf-8").splitlines()
            
            hrc_lines = [hrc_line for hrc_line in hrc_lines if hrc_line[:1] != "#"] # Removing comments

            skeleton = HRCSkeleton(os.path.splitext(filename)[0], hrc_lines[1].split(" ")[1], int(hrc_lines[2].split(" ")[1]))
            name = parent = ""
            length = 0.0
            newBone = True
            for hrc_rownum, hrc_line in enumerate(hrc_lines[3:], start=3): # Starting right after the header
                if not hrc_line.strip(): # Empty lines mark the arrival of a new bone next line
                    name = parent = ""
                    length = 0.0
                    newBone = True
                elif newBone: # First line of a new bone
                    name = hrc_line
                    parent = hrc_lines[hrc_rownum + 1]
                    length = float(hrc_lines[hrc_rownum + 2])
                    rsd = hrc_lines[hrc_rownum + 3].split()
                    p_file = None
                    tex_list = None
                    if int(rsd[0]) > 0:
                        rsd_files = [i.lower() + ".rsd" for i in rsd[1:]] # Get list of RSD files
                        for rsd_file in rsd_files:
                            rsd_lines = lgp_file.getFileContent(rsd_file).decode("utf-8").splitlines()

                            rsd_lines = [rsd_line for rsd_line in rsd_lines if rsd_line[:1] != "#"] # Removing comments

                            # The .P file can be deduced from either PLY, GRP or MAT section
                            # I chose PLY because it's the first one
                            p_file = [i for i in rsd_lines if i.startswith("PLY=")][0]
                            p_file = p_file[4:p_file.find(".")] + ".P"

                            # The NTEX section gives us the number of texture files
                            nb_tex = int([i for i in rsd_lines if i.startswith("NTEX=")][0][5:])
                            if nb_tex > 0:
                                # We use list comprehension to extract TEX files' names
                                tex_list = [i[i.find("=") + 1:i.find(".")] + ".TEX" for i in rsd_lines if i.startswith("TEX[")]
                
                    if name != "" and parent != "" and length != 0.0:
                        bone = HRCBone(name, parent, length, p_file, tex_list)
                        skeleton.addBone(bone)
                
                    newBone = False
                else: # Line within a bone
                    continue # Already processed with the first row for each bone
        
            skeletons.append(skeleton)

            # Now we have all needed objects, we can work in Blender
            for skeleton in skeletons:
                # Adding a new Scene per skeleton
                if skeleton.filename in SKELETONS_NAMES:
                    scene = bpy.data.scenes.new(SKELETONS_NAMES[skeleton.filename])
                else:
                    scene = bpy.data.scenes.new(skeleton.filename)
                bpy.context.window.scene = scene
                view_layer = bpy.context.view_layer
                # Adding armature to the scene
                armature_data = bpy.data.armatures.new(name=skeleton.name+"_root") # The Armature will represent the root bone for transformation purposes
                armature_obj = bpy.data.objects.new(name=skeleton.name, object_data=armature_data)
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
