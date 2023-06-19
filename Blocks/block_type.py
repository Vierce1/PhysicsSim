class Block_Type:
    def __init__(self):
        self.name = 'base'
        self.rigid = True


class Sand(Block_Type):
    def __init__(self):
        self.name = 'sand'
        self.rigid = False

class Rock(Block_Type):
    def __init__(self):
        self.name = 'rock'
        self.rigid = True