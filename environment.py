from Blocks.block import Block


class Environment:
    def __init__(self, wind: int):
        self.wind = wind


    def get_wind(self):
        return self.wind



BLACK_HOLE = 1
SMALL_BLACK_HOLE = 2
LARGE_BLACK_HOLE = 3
REPULSOR = 4

def get_field(field_num: int, position: (int, int)):
    if field_num == BLACK_HOLE:
        return Black_Hole(position)
    
class Energy_Field:
    def __init__(self):
        self.energy = 0
        self.position = (0,0)
        self.event_horizon = 1  # total radius of effect, objects at (0,0) position destroyed

    
class Black_Hole(Energy_Field):
    def __init__(self, position: (int, int)):
        super().__init__()
        print(self.energy)
        self.energy = 10
        self.position = position
        self.event_horizon = 20

