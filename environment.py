from Blocks.block import Block


BLACK_HOLE = 1
SMALL_BLACK_HOLE = 2
LARGE_BLACK_HOLE = 3
REPULSOR = 4

def get_field(field_num: int, position: (int, int)):
    if field_num == BLACK_HOLE:
        return Black_Hole(position)
    elif field_num == LARGE_BLACK_HOLE:
        return Large_Black_Hole(position)
    
class Energy_Field:
    def __init__(self):
        self.energy = 0
        self.position = (0,0)
        self.event_horizon = 1  # total radius of effect, objects at (0,0) position destroyed
        self.quad_node = None

    
class Black_Hole(Energy_Field):
    def __init__(self, position: (int, int)):
        super().__init__()
        self.energy = 10
        self.position = position
        self.event_horizon = 20


class Large_Black_Hole(Energy_Field):
    def __init__(self, position: (int, int)):
        super().__init__()
        self.energy = 50
        self.position = position
        self.event_horizon = 100



class Environment:
    def __init__(self, wind: int, energy_fields: [Energy_Field]):
        self.wind = wind
        self.energy_fields = None
        if energy_fields:
            self.energy_fields = {e for e in energy_fields}

    def get_wind(self):
        return self.wind

