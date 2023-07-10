import pygame as pg
from pygame import time
from pygame.locals import *
from player import Player
import Blocks
from Blocks.block import Block
from Blocks.block_type import *
from Blocks import terrain_gen as tg, terrain_manager as tm
import physics
from quadtree import Quadtree
import psutil


class Game:
    def __init__(self, display_resolution: list[int], screen: pg.Surface):
        self.display_resolution = display_resolution
        self.screen = screen
        self.quadtrees = []
        # Initial load time goes up with more cells, but fps is better
        # Having a huge number of trees decreases FPS but reduces impact of collision.
        # width and height of each quadtree cell
        self.quadtree_height = 1000  # Update to nested nodes
        self.quadtree_width = 1000
        self.y_count = 1
        self.x_count = 2
        self.delay = 2
        # self.y_count = round(self.display_resolution[1] / self.quadtree_height)
        # self.x_count = round(self.display_resolution[0] / self.quadtree_width)


    def setup(self):
        self.terrain_manager = tm.Terrain_Manager(self.display_resolution[0], self.display_resolution[1])
        self.blocks = tg.gen_terrain(block_list=(1000, Sand()), bounds=(620, 780, 100, 600),
                                         terrain_manager=self.terrain_manager)
        rocks = tg.gen_terrain(block_list=(1000, Rock()), bounds=(600, 800, 800, 900),
                                        terrain_manager=self.terrain_manager)
        self.blocks.extend(rocks)
        self.blocks.extend(tg.gen_terrain(block_list=(60, Rock()), bounds=(580, 599, 760, 800),
                                              terrain_manager=self.terrain_manager))
        self.blocks.extend(tg.gen_terrain(block_list=(60, Rock()), bounds=(801, 820, 760, 800),
                                              terrain_manager=self.terrain_manager))
        # print(f'length of blocks = {str(len(self.blocks))}')

        self.terrain_manager.blocks.extend(self.blocks)
        block_rects = [block.rect for block in self.blocks]
        self.terrain_manager.block_rects.extend(block_rects)
        self.terrain_manager.setup()


    def update(self, timer: int, events: list[pg.event.Event]):
        # fill screen with black
        # render_image.fill((0, 0, 0))
        self.screen.fill((0, 0, 0))

        self.quadtrees = self.terrain_manager.update(screen=self.screen)

        # # visualization
        pg.draw.line(self.screen, (0, 0, 255), (0, physics.ground), (2400, physics.ground))  # Ground
        for q in self.quadtrees:
            color = (255, 255, 255) # if len(q.objects) == 0 else (255, 0, 0)
            pg.draw.line(self.screen, color, (q.x, q.y), (q.x + q.width, q.y))
            pg.draw.line(self.screen, color, (q.x + q.width, q.y), (q.x + q.width, q.y - q.height))
            pg.draw.line(self.screen, color, (q.x, q.y), (q.x, q.y - q.height))
            pg.draw.line(self.screen, color, (q.x, q.y - q.height), (q.x + q.width, q.y - q.height))

        # timed functions
        # if timer > 60:
        #     new_blocks = tg.gen_terrain(block_list=(1, Sand()), bounds=(620, 780, 0, 200),
        #                                          terrain_manager=self.terrain_manager)
        #     # terrain_manager.blocks.extend(blocks)
        #     self.blocks.extend(new_blocks)
        #     self.terrain_manager.blocks.extend(new_blocks)
        #     [self.terrain_manager.block_rects.extend(block.rect) for block in new_blocks]
        #     [self.terrain_manager.add_rects_to_quadtree(block, self.quadtrees, self.y_count, self.x_count)
        #             for block in new_blocks]



        # render_image.convert()  # optimize image after drawing on it
        # draw_area = render_image.get_rect().move(0, 0)
        # screen.blit(render_image, draw_area)  # blitting was slower

        # self.player.update(events, self.screen)

        # tick = pg.time.get_ticks()
        # now = pg.time.get_ticks()
        # while now - tick < self.delay:
        #     now = pg.time.get_ticks()

        print(f'memory % usage: {psutil.virtual_memory().percent}')
        print(f'cpu % usage: {psutil.cpu_percent()}')

        pg.event.pump()
        pg.display.flip()  # updates the display. Could use display.update() and pass in PARTS of the screen to update
        # gc.collect() # possible performance improvement by removing unreferenced memory
        # blocks_update = [block.rect for block in self.blocks]  # slower and would need to also clear the prev. space
        # pg.display.update(blocks_update)