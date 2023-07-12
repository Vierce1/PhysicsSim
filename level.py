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
                                     block_types=level['block_types'], bounds=level['bounds']
                                     , timed_spawns=level['timed_spawns']))
        # [print(l.bounds) for l in self.levels]


    def get_level(self, level: int):
        print(f'creating level {level}')
        level = self.levels[level]
        return level


# noinspection PyTypeChecker
class Level:
    def __init__(self, id: int, block_counts: list[int], block_types: list[str],
                    bounds: list[(int,int,int,int)], timed_spawns: list = None, writing: bool = False):
        self.id = id
        self.block_counts = block_counts
        self.bounds = bounds
        self.block_types = []

        if writing:  # Creating json. Don't convert to objects
            self.block_types = block_types
        # Timed Spawn example format:  [{"block_types":[SAND, SAND], "times":[10, 23], "bounds":[(0,1,2,3), (4,4,4,4)}]
            self.timed_spawns = timed_spawns  # particles that spawn over time. Time in seconds

        else:  # Reading level. Create block types from the enums
            for t in block_types:  # Block Types
                tp = block_type.Block_Type().get_block_type(t)
                self.block_types.append(tp)
            if timed_spawns:
                self.timed_spawns = []
                # get the length of 1 of the fields, which will equate to length for all fields
                for i in range(len(timed_spawns['block_types'])):
                    timed_spawn = Timed_Spawn(b_type=timed_spawns['block_types'][i],
                                  spawn_rate=timed_spawns['spawn_rate'][i], time=timed_spawns['times'][i],
                                              bounds=timed_spawns['bounds'][i])
                    self.timed_spawns.append(timed_spawn)




class Timed_Spawn:
    def __init__(self, b_type: block_type.Block_Type, spawn_rate: int, time: int, bounds: (int, int, int, int)):
        self.block_type = block_type.Block_Type().get_block_type(b_type)
        self.spawn_rate = spawn_rate
        self.time = time
        self.bounds = bounds
