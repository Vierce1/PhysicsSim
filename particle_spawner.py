import pygame as pg
from Blocks.block_type import *
from Blocks.terrain_manager import *
from Blocks.terrain_gen import *

class Particle_Spawner:
    def __init__(self, terrain_manager: Terrain_Manager, terrain_gen: Terrain_Gen):
        self.tm = terrain_manager
        self.tg = terrain_gen
        self.particle_type = GRAVEL


    def spawn(self, x: int, y: int, count: int):
        # create the blocks
        # Should probably set up a queue and any particles still in queue when player stops pressing button don't spawn
        count = round(count / self.tm.game.physics_lag_frames)
        particles = self.tg.gen_terrain(block_count=count, block_type=self.particle_type,
                            bounds=(round(x - count/4),round(x + count/4), round(y - count/4), round(y + count/4)))
        # add them to the matrix & the various lists
        self.tm.add_blocks_to_matrix(particles)
