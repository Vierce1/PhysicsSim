SAND = 0
ROCK = 1
DIRT = 2
STATIC_SAND = 3


class Block_Type:
    def __init__(self):
        self.name = 'base'
        self.rigid = True
        self.destroyable = False
        self.color = (0,0,0)
        self.friction = 1  # slidieness. 1 = no sliding
        self.width = 1
        self.height = 1
        self.start_static = False

    def get_block_type(self, block_type):
        if block_type == SAND:
            return Sand()
        elif block_type == STATIC_SAND:
            return Static_Sand()
        elif block_type == ROCK:
            return Rock()
        elif block_type == DIRT:
            return Dirt()


class Sand(Block_Type):
    def __init__(self):
        super().__init__()
        self.name = 'sand'
        self.rigid = False
        self.destroyable = False
        self.color = (150,190,0)
        self.friction = 0.3

class Static_Sand(Block_Type):  # starts grounded until becoming ungrounded again
    def __init__(self):
        super().__init__()
        self.name = 'sand'
        self.rigid = False
        self.destroyable = False
        self.color = (150,190,0)
        self.friction = 0.3
        self.start_static = True


class Rock(Block_Type):
    def __init__(self):
        super().__init__()
        self.name = 'rock'
        self.rigid = True
        self.destroyable = False
        self.color = (160, 160, 160)
        self.friction = 0.8

class Dirt(Block_Type):
    def __init__(self):
        super().__init__()
        self.name = 'dirt'
        self.rigid = True
        self.destroyable = True
        self.color = (70,38,0)
        self.friction = 0.3