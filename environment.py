from Blocks.block import Block


BLACK_HOLE = 1
SMALL_BLACK_HOLE = 2
LARGE_BLACK_HOLE = 3
REPULSOR = 4


class Environment:
    def __init__(self, wind: int):
        self.wind = wind


    def get_wind(self):
        return self.wind


    
    
class Energy_Field:
    def __init__(self):
        self.energy = 0
        self.position = (0,0)
        self.event_horizon = 1  # total radius of effect, objects at (0,0) position destroyed

    
class Black_Hole(Energy_Field):
    def __init__(self):
        super().__init__()
        print(self.energy)
        self.energy = 10
        self.event_horizon = 20

