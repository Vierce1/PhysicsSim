SAND = 0
ROCK = 1


class Block_Type:
    def __init__(self):
        self.name = 'base'
        self.rigid = True
        self.color = (0,0,0)
        self.friction = 1  # slidieness. 1 = no sliding
        self.width = 1
        self.height = 1

    def get_block_type(self, block_type):
        if block_type == SAND:
            return Sand()
        elif block_type == ROCK:
            return Rock()


class Sand(Block_Type):
    def __init__(self):
        self.name = 'sand'
        self.rigid = False
        self.color = (150,190,0)
        self.friction = 0.3
        self.width = 1
        self.height = 1


class Rock(Block_Type):
    def __init__(self):
        self.name = 'rock'
        self.rigid = True
        self.color = (160, 160, 160)
        self.friction = 0.8
        self.width = 6
        self.height = 6
