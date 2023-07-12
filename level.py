from Blocks.block import Block
import Blocks.block_type as block_type
import json
from types import SimpleNamespace


class Level_Getter:
    def __init__(self):
        self.levels = []
        self.read_levels_json()


    def read_levels_json(self):
        json_file = open('levels.json')
        levels = json.load(json_file)
        print(levels)
        for level in levels:
            self.levels.append(Level(id=level['id'], block_counts=level['block_counts'],
                                     block_types=level['block_types'], bounds=level['bounds']))
        # [print(l.block_types) for l in self.levels]


    def get_level(self, level: int):
        print(f'creating level {level}')




class Level:
    def __init__(self, id: int, block_counts: list[int], block_types: list[block_type.Block_Type],
                    bounds: list[(int,int,int,int)]):
        self.id = id
        self.block_counts = block_counts
        self.block_types = block_types
        self.bounds = bounds



