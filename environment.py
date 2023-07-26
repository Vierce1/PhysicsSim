from Blocks.block import Block


class Environment:
    def __init__(self, wind: int):
        self.wind = wind


    def get_wind(self):
        return self.wind


    
    
class Energy_Field:
    def __init__(self):
        pass
    
class Black_Hole(Energy_Field):
    def __init__(self):
        super().__init__()
    
