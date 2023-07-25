import random
# from numba.experimental import jitclass

SAND = 0
ROCK = 1
DIRT = 2
STATIC_SAND = 3
WATER = 4
GRAVEL = 5
MAGMA = 6


class Block_Type_Instance_List(list):   # holds 1 instance of each block type to access properties
    def __init__(self):
        super(Block_Type_Instance_List).__init__()
        for i in range(7):
            self.append(Block_Type().get_block_type(i))
        # self.extend(Sand(), Rock(), Dirt(), Static_Sand(), Water(), Gravel(), Magma())


class Block_Type:
    def __init__(self):
        self.name = 'base'
        self.rigid = True
        self.destroyable = False
        self.color = (0,0,0)
        # self.slipperiness = 1  # slidieness. 1 = no sliding
        self.slide_grade = (1, 1)  # x,y tolerance. If no block is in x+1, y+1, it will slide
        self.start_static = False
        self.destructive = False   # lava. Destroys blocks it touches if they're destroyable


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
            rand = random.randrange(0, 3)
            if rand == 0:
                return Gravel_A()
            elif rand == 1:
                return Gravel_B()
            else:
                return Gravel_C()
        elif block_type == MAGMA:
            return Magma()



class Sand(Block_Type):
    def __init__(self):
        super().__init__()
        self.name = 'sand'
        self.rigid = False
        self.destroyable = True
        self.color = (150,190,0)
        self.slide_grade = (1, 1)

class Static_Sand(Block_Type):  # starts grounded until becoming ungrounded again
    def __init__(self):
        super().__init__()
        self.name = 'sand'
        self.rigid = False
        self.destroyable = True
        self.color = (150,190,0)
        self.slide_grade = (1, 1)
        self.start_static = True


class Rock(Block_Type):
    def __init__(self):
        super().__init__()
        self.name = 'rock'
        self.rigid = True
        self.destroyable = False
        self.color = (160, 160, 160)
        self.slide_grade = (0, 0)

class Gravel(Block_Type):  # Inheritance seems pointless here since there are no methods to inherit.
    def __init__(self):
        super().__init__()
        self.name = 'gravel'
        self.rigid = False
        self.destroyable = True
        self.slide_grade = (1, 3)


class Gravel_A(Gravel):  # All that changes is the color, so for everything else can just access Gravel() / GRAVEL
    def __init__(self):
        super().__init__()
        self.name = 'gravel'
        self.rigid = False
        self.destroyable = True
        self.slide_grade = (1, 3)
        self.color = (130, 130, 130)

class Gravel_B(Gravel):
    def __init__(self):
        super().__init__()
        self.name = 'gravel'
        self.rigid = False
        self.destroyable = True
        self.slide_grade = (1, 3)
        self.color = (165, 165, 165)

class Gravel_C(Gravel):
    def __init__(self):
        super().__init__()
        self.name = 'gravel'
        self.rigid = False
        self.destroyable = True
        self.slide_grade = (1, 3)
        self.color = (52, 52, 52)


class Dirt(Block_Type):
    def __init__(self):
        super().__init__()
        self.name = 'dirt'
        self.rigid = True
        self.destroyable = True
        self.color = (70,38,0)
        self.slide_grade = (1, 1)


class Water(Block_Type):
    def __init__(self):
        super().__init__()
        self.name = 'water'
        self.rigid = False
        self.destroyable = True
        self.color = (0,120,255)
        self.slide_grade = (6, 1)


class Magma(Block_Type):
    def __init__(self):
        super().__init__()
        self.name = 'magma'
        self.rigid = False
        self.destroyable = False
        self.color = (255,85,0)
        self.slide_grade = (4, 1)
        self.destructive = True

