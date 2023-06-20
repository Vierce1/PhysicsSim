class Block_Type:
    def __init__(self):
        self.name = 'base'
        self.rigid = True
        self.color = (0,0,0)
        self.friction = 1  # slidieness. 1 = no sliding


class Sand(Block_Type):
    def __init__(self):
        self.name = 'sand'
        self.rigid = False
        self.color = (150,190,0)
        self.friction = 0.3

class Rock(Block_Type):
    def __init__(self):
        self.name = 'rock'
        self.rigid = True
        self.color = (160, 160, 160)
        self.friction = 0.8