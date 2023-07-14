import pygame as pg
from pygame import time
from pygame.locals import *
from player import Player
import Blocks
from Blocks.block import Block
from Blocks.block_type import *
from Blocks import terrain_gen as tg, terrain_manager as tm
from level import *
import psutil
import gc
import sys


class Game:
    def __init__(self, window_size: list[int], display_resolution: list[int], screen: pg.Surface):
        self.display_resolution = display_resolution
        self.window_size = window_size
        self.screen = screen
        self.delay = round(1000/144)
        gc.disable()
        self.render_image = pg.Surface((display_resolution[0], display_resolution[1]))  # for drawing offscreen first
        self.spaces_to_clear = set()
        self.terrain_manager = tm.Terrain_Manager(self.display_resolution[0], self.display_resolution[1], self)
        self.level = 1
        self.terrain_manager.setup(self.render_image)
        self.terrain_gen = tg.Terrain_Gen(self.terrain_manager)
        self.player = Player(self.terrain_manager, self, window_size[0], window_size[1], display_resolution[0],
                             display_resolution[1])
        self.quadtree_nodes = set()


    def setup(self, level: int) -> Level:
        self.terrain_manager.blocks.clear()

        level = Level_Getter().get_level(level=level)
        level_blocks = set()
        for i in range(len(level.block_counts)):  # iterate over all entries in the dict for this level
            blocks = self.terrain_gen.gen_terrain(block_count=level.block_counts[i],
                                block_type=level.block_types[i], bounds=level.bounds[i])
            level_blocks.update(blocks)
            if blocks[0].type.destroyable:
                self.terrain_manager.destroyable_blocks.update(blocks)

        print(f'length of blocks = {str(len(level_blocks))}')
        self.terrain_manager.blocks.update(level_blocks)
        return level


    def update(self, level: Level, timer: int, events: list[pg.event.Event]):
        # self.render_image.fill((0, 0, 0))  # For higher # of particles, this is faster
        [self.render_image.set_at(pos, (0, 0, 0)) for pos in self.spaces_to_clear]
        self.spaces_to_clear.clear()

        self.terrain_manager.update(screen=self.screen)

        # # visualization
        pg.draw.line(self.render_image, (0, 0, 255), (0, tm.ground), (2400, tm.ground))  # Ground
        for q in self.quadtree_nodes:
            color = (255, 255, 255) # if len(q.objects) == 0 else (255, 0, 0)
            pg.draw.line(self.render_image, color, (q.x, q.y), (q.x + q.width, q.y))
            pg.draw.line(self.render_image, color, (q.x + q.width, q.y), (q.x + q.width, q.y - q.height))
            pg.draw.line(self.render_image, color, (q.x, q.y), (q.x, q.y - q.height))
            pg.draw.line(self.render_image, color, (q.x, q.y - q.height), (q.x + q.width, q.y - q.height))


        # timed functions
        for ts in level.timed_spawns:
            if timer > ts.time:
                spawn_blocks = self.terrain_gen.gen_terrain(block_count=ts.spawn_rate, block_type=ts.block_type,
                                                            bounds=ts.bounds)
                # self.blocks.update(spawn_blocks)
                self.terrain_manager.blocks.update(spawn_blocks)


        self.player.update(events, self.render_image)

        self.render_image.convert()  # optimize image after drawing on it
        draw_area = self.render_image.get_rect().move(0, 0)
        resized_screen = pg.transform.scale(self.render_image, (self.window_size[0], self.window_size[1]))
        self.screen.blit(resized_screen, draw_area)

        tick = pg.time.get_ticks()
        now = pg.time.get_ticks()
        # while now - tick < self.delay:
        #     now = pg.time.get_ticks()

        # print(f'memory % usage: {psutil.virtual_memory().percent}')
        # print(f'cpu % usage: {psutil.cpu_percent()}')

        pg.event.pump()
        pg.display.flip()  # updates the display
        # gc.collect() # possible performance improvement by removing unreferenced memory
        # pg.display.update(blocks_update)