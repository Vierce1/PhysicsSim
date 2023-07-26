from Blocks.block import Block


class Environment:
    def __init__(self, wind: int):
        self.wind = wind


    def get_wind(self):
        return self.wind

    # def wind_blow(self, active_blocks: [Block]):
    #     for block in active_blocks:
    #         block.horiz_velocity += self.wind
