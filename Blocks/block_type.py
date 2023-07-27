import random
# from numba.experimental import jitclass

SAND = 0
ROCK = 1
DIRT = 2
STATIC_SAND = 3
WATER = 4
GRAVEL = 5
MAGMA = 6
MUD = 7


class Block_Type_Instance_List(list):   # holds 1 instance of each block type to access properties
    def __init__(self):
        super(Block_Type_Instance_List).__init__()
        for i in range(8):  # Update this when add block types
            self.append(Block_Type().get_block_type(i))


class Block_Type:
    def __init__(self):
        self.name = 'base'
        self.rigid = True
        self.destroyable = False
        self.color = (0,0,0)
        self.colors = None
        self.liquid = False
        self.slide_grade = (1, 1)  # x,y tolerance. If no block is in x+1, y+1, it will slide
        self.start_static = False
        self.destructive = False   # lava. Destroys blocks it touches if they're destroyable
        self.destroy_count = 50
        self.weight = 1  # controls how easily it gets blown by wind. Divide wind by this value


    def get_color(self):
        if self.colors:
            return self.colors[random.randrange(len(self.colors))]
        return self.color


    def get_block_type(self, block_type):
        if block_type == SAND:
            return Sand()
        elif block_type == STATIC_SAND:
            return Static_Sand()
        elif block_type == ROCK:
            return Rock()
        elif block_type == DIRT:
            return Dirt()
        elif block_type == WATER:
            return Water()
        elif block_type == GRAVEL:
            return Gravel()
        elif block_type == MAGMA:
            return Magma()
        elif block_type == MUD:
            return Mud()



class Sand(Block_Type):
    def __init__(self):
        super().__init__()
        self.name = 'sand'
        self.rigid = False
        self.liquid = False
        self.destroyable = True
        self.color = (150,190,0)
        self.slide_grade = (3, 1)
        self.weight = 1

class Static_Sand(Block_Type):  # starts grounded until becoming ungrounded again
    def __init__(self):
        super().__init__()
        self.name = 'sand'
        self.rigid = False
        self.liquid = False
        self.destroyable = True
        self.color = (150,190,0)
        self.slide_grade = (1, 1)
        self.start_static = True
        self.weight = 1


class Rock(Block_Type):
    def __init__(self):
        super().__init__()
        self.name = 'rock'
        self.rigid = True
        self.liquid = False
        self.destroyable = False
        self.color = (160, 160, 160)
        self.slide_grade = (0, 0)
        self.weight = 5

class Gravel(Block_Type):
    def __init__(self):
        super().__init__()
        self.name = 'gravel'
        self.rigid = False
        self.liquid = False
        self.destroyable = True
        self.slide_grade = (1, 1)
        self.color = (130, 130, 130)
        self.colors = [(130, 130, 130), (165, 165, 165), (52, 52, 52)]
        self.weight = 3

class Dirt(Block_Type):
    def __init__(self):
        super().__init__()
        self.name = 'dirt'
        self.rigid = True
        self.liquid = False
        self.destroyable = True
        self.color = (70,38,0)
        self.slide_grade = (1, 1)
        self.weight = 2

class Mud(Block_Type):
    def __init__(self):
        super().__init__()
        self.name = 'mud'
        self.rigid = False
        self.liquid = False
        self.destroyable = True
        self.color = (45,25,0)
        self.slide_grade = (1, 4)
        self.weight = 3



    # Liquids
#TODO: Solid blocks should fall through liquids. They screw up liquid flowing when land on top
# Need to tint them blue (or whatever color the liquid is)
class Water(Block_Type):
    def __init__(self):
        super().__init__()
        self.name = 'water'
        self.rigid = False
        self.liquid = True
        self.destroyable = True
        self.color = (0,120,255)
        self.slide_grade = (1, 0)  # Slide grade works for solids, but not really for liquids. Leave at 1,1
        self.weight = 1


class Magma(Block_Type):
    def __init__(self):
        super().__init__()
        self.name = 'magma'
        self.rigid = False
        self.liquid = True
        self.destroyable = False
        self.color = (255,85,0)
        self.slide_grade = (1,0)
        self.destructive = True
        self.destroy_count = 25  # Keep this really high. It creates an additive effect
        self.weight = 4
