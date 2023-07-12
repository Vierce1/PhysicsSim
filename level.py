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
        for level in levels:
            self.levels.append(Level(id=level['id'], block_counts=level['block_counts'],
                                     block_types=level['block_types'], bounds=level['bounds']))
        # [print(l.bounds) for l in self.levels]


    def get_level(self, level: int):
        print(f'creating level {level}')
        level = self.levels[level - 1]
        return level



class Level:
    def __init__(self, id: int, block_counts: list[int], block_types: list[block_type.Block_Type],
                    bounds: list[(int,int,int,int)]):
        self.id = id
        self.block_counts = block_counts
        self.bounds = bounds
        self.block_types = []
        for t in block_types:
            tp = block_type.Block_Type().get_block_type(t['name'])
            self.block_types.append(tp)



