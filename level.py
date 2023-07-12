from Blocks.block import Block
import Blocks.block_type as block_type
import json


class Level_Getter:
    def __init__(self):
        pass
    def get_level(level: int):
        print(f'creating level {level}')
        # First read the level Json
        level = json.load
        # for i in range(len(self.block_counts)):



class Level:
    def __init__(self, id: int, block_counts: list[int], block_types: list[block_type.Block_Type],
                    bounds: list[(int,int,int,int)]):
        self.id = id
        self.block_counts = block_counts
        self.block_types = block_types
        self.bounds = bounds



