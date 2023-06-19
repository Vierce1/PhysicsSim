class Block_Type:
    def __init__(self):
        self.name = 'base'
        self.rigid = True
        self.color = (0,0,0)
        # slipperiness : how long it has to sit still before being grounded


class Sand(Block_Type):
    def __init__(self):
        self.name = 'sand'
        self.rigid = False
        self.color = (150,190,0)

class Rock(Block_Type):
    def __init__(self):
        self.name = 'rock'
        self.rigid = True
        self.color = (160, 160, 160)