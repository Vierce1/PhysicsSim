SAND = 0
ROCK = 1
DIRT = 2


class Block_Type:
    def __init__(self):
        self.name = 'base'
        self.rigid = True
        self.destroyable = False
        self.color = (0,0,0)
        self.friction = 1  # slidieness. 1 = no sliding
        self.width = 1
        self.height = 1

    def get_block_type(self, block_type):
        if block_type == SAND:
            return Sand()
        elif block_type == ROCK:
            return Rock()
        elif block_type == DIRT:
            return Dirt()


class Sand(Block_Type):
    def __init__(self):
        self.name = 'sand'
        self.rigid = False
        self.destroyable = False
        self.color = (150,190,0)
        self.friction = 0.3
        self.width = 1
        self.height = 1


class Rock(Block_Type):
    def __init__(self):
        self.name = 'rock'
        self.rigid = True
        self.destroyable = False
        self.color = (160, 160, 160)
        self.friction = 0.8
        self.width = 1
        self.height = 1

class Dirt(Block_Type):
    def __init__(self):
        self.name = 'dirt'
        self.rigid = True
        self.destroyable = False
        self.color = (70,38,0)
        self.friction = 0.3
        self.width = 1
        self.height = 1