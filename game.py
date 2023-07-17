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
        self.render_image = pg.Surface((display_resolution[0], display_resolution[1]))  # for drawing world size + blit
        self.spaces_to_clear = set()
        self.level = 1
        self.terrain_manager = tm.Terrain_Manager(self.display_resolution[0], self.display_resolution[1], self)
        self.terrain_gen = tg.Terrain_Gen(self.terrain_manager)
        self.player = Player(self.terrain_manager, self, window_size[0], window_size[1], display_resolution[0],
                             display_resolution[1])
        self.quadtree_nodes = set()
        self.plane_shift = (0, 0)  # x,y shift to apply to blit. Starts on the zero-point of the world.
                                    # Updates as player moves.
        self.render_scale = (window_size[0], window_size[1])  # update based on world size in update


    def setup(self, level: int) -> Level:
        level = Level_Getter().get_level(level=level)
        self.render_image = pg.Surface(level.world_size)
        print(f'world size: {self.render_image.get_size()}')
        self.render_scale = ( level.world_size[0] / self.render_scale[0],
                             level.world_size[1] / self.render_scale[1])
        self.terrain_manager.setup(render_image=self.render_image, world_size=level.world_size)
        level_blocks = set()
        for i in range(len(level.block_counts)):  # iterate over all entries in the dict for this level
            blocks = self.terrain_gen.gen_terrain(block_count=level.block_counts[i],
                                block_type=level.block_types[i], bounds=level.bounds[i])
            level_blocks.update(blocks)
            if blocks[0].type.destroyable:
                self.terrain_manager.destroyable_blocks.update(blocks)


        print(f'length of particles = {str(len(level_blocks))}')
        self.terrain_manager.blocks.update(level_blocks)  # have to add ALL blocks to this first so they draw on frame 1
        self.terrain_manager.all_blocks.extend(level_blocks)
        # Fill quadtree on load
        self.quadtree_nodes, created = self.terrain_manager.initialize_quadtree()
        # print(f'created {len(self.quadtree_nodes)} quadtree branch nodes')
        self.terrain_manager.fill_matrix()
        return level


    def update_plane_shift(self, change: (int, int)):
        self.plane_shift = (self.plane_shift[0] - change[0], self.plane_shift[1] - change[1])


    def update(self, level: Level, timer: int, events: list[pg.event.Event]):
        # self.render_image.fill((0, 0, 0))  # For higher # of particles, this is faster
        [self.render_image.set_at(pos, (0, 0, 0)) for pos in self.spaces_to_clear]
        self.spaces_to_clear.clear()

        self.terrain_manager.update()

        # # visualization
        pg.draw.line(self.render_image, (0, 0, 255), (0, tm.ground), (2400, tm.ground))  # Ground
        # for q in self.quadtree_nodes:
        #     color = (255, 255, 255) # if len(q.objects) == 0 else (255, 0, 0)
        #     pg.draw.line(self.render_image, color, (q.x, q.y), (q.x + q.width, q.y))
        #     pg.draw.line(self.render_image, color, (q.x + q.width, q.y), (q.x + q.width, q.y - q.height))
        #     pg.draw.line(self.render_image, color, (q.x, q.y), (q.x, q.y - q.height))
        #     pg.draw.line(self.render_image, color, (q.x, q.y - q.height), (q.x + q.width, q.y - q.height))


        # timed functions
        for ts in level.timed_spawns:
            if timer > ts.time:
                spawn_blocks = self.terrain_gen.gen_terrain(block_count=ts.spawn_rate, block_type=ts.block_type,
                                                            bounds=ts.bounds)
                # self.blocks.update(spawn_blocks)
                self.terrain_manager.blocks.update(spawn_blocks)


        self.player.update(events, self.render_image)

        # Blitting
        self.render_image.convert()  # optimize image after drawing on it
        draw_area = self.render_image.get_rect().move(self.plane_shift[0], self.plane_shift[1])
        # TODO: Figure out scaling that doesn't reduce framerate if desired
        # resized_screen = pg.transform.scale(self.render_image, (self.window_size[0] * 1.5,
        #                                                         self.window_size[1] * 1.5))
        # pg.transform.scale_by(self.render_image, 1.5, self.screen)  # error, scale must match screen size
        # pg.transform.scale(self.render_image, self.render_scale, self.screen)
        # resized_screen = pg.transform.scale_by(self.render_image, 1.5)
        self.screen.blit(self.render_image, draw_area)

        tick = pg.time.get_ticks()
        now = pg.time.get_ticks()
        # while now - tick < self.delay:
        #     now = pg.time.get_ticks()

        # print(f'memory % usage: {psutil.virtual_memory().percent}')
        # print(f'cpu % usage: {psutil.cpu_percent()}')

        pg.event.pump()
        # pg.display.flip()  # updates the entire surface
        pg.display.update(draw_area)  # With dynamic world size, this is 10% faster
        # gc.collect() # possible performance improvement by removing unreferenced memory

