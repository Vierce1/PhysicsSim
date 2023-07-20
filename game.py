import asyncio

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
        self.delay = .033  # 1000/85  # slowing the delay = more things happening each frame... which hurts fps
        gc.disable()
        self.render_image = pg.Surface((0, 0))  # for drawing world size + blit. Will be resized for the level
        self.spaces_to_clear = Clear_Spaces(self)  # set()
        self.terrain_manager = tm.Terrain_Manager(self.display_resolution[0], self.display_resolution[1], self)
        self.terrain_gen = tg.Terrain_Gen(self.terrain_manager)
        self.player = Player(self.terrain_manager, self, window_size[0], window_size[1], display_resolution[0],
                             display_resolution[1])
        self.quadtree_nodes = set()
        self.plane_shift = (0, 0)  # x,y shift to apply to blit. Starts on the zero-point of the world.
                                    # Updates as player moves.
        self.render_scale = (self.window_size[0], self.window_size[1])
        self.level: Level = None
        self.backdrop = pg.image.load('background_1.png')
        self.backdrop_surface = pg.Surface((0,0))
        self.physics_processing = False
        self.physics_task = None


    def setup(self, level: int) -> Level:
        # Level reading and creation
        level = Level_Getter().get_level(level=level)
        self.level = level
        self.render_image = pg.Surface(level.world_size)
        print(f'world size: {self.render_image.get_size()}')
        # self.render_scale = (self.window_size[0] / level.world_size[0], self.window_size[1] / level.world_size[1])
        self.terrain_manager.setup(render_image=self.render_image, world_size=level.world_size,
                                   ground_level=level.ground)
        self.player.set_start_position(level.start_pos)
        # self.player.render_width, self.player.render_height = level.world_size[0], level.world_size[1]

        # Set the plane shift to center the camera on the player's starting position
        self.plane_shift = self.adjust_start_planeshift(level.start_pos, level.world_size)
        print(f'plane shift: {self.plane_shift}')
        # self.plane_shift = (0, 0)

        # Create all particles
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

        # Backdrop sizing... revisit later
        self.backdrop.convert(self.render_image)
        self.backdrop_surface = pg.Surface(self.backdrop.get_size())
        self.backdrop_surface.blit(self.backdrop, (0,0))
        self.backdrop_surface = pg.transform.scale(self.backdrop_surface, (level.world_size[0], level.world_size[1]))
        self.render_image.blit(self.backdrop_surface, (0, 0))
        return level


    def adjust_start_planeshift(self, start_pos: (int, int), world_size: (int, int)) -> (int, int):
        x_shift = start_pos[0] - self.display_resolution[0] / 2
        if x_shift < 0:  # player starting at a postion between 0 - display resolution [0]
            print('Out of bounds LEFT')
            x_shift = 0
        elif start_pos[0] > world_size[0] - self.display_resolution[0] / 2:
            print('Out of bounds RIGHT')
            x_shift = - (world_size[0] - self.display_resolution[0])

        y_shift = start_pos[1] - self.display_resolution[1] / 2
        if y_shift < 0:
            y_shift = 0
        elif start_pos[1] > world_size[1] - self.display_resolution[1]:
            y_shift = world_size[1] - self.display_resolution[1]

        return (x_shift, y_shift)


    def update_plane_shift(self, change: (int, int), player_pos: (int, int)):
        # First check if hitting the bounds of the level
        new_plane_shift = (self.plane_shift[0] - change[0], self.plane_shift[1] - change[1])
        if (self.display_resolution[0] / 2) > player_pos[0] \
          or player_pos[0] > (self.level.world_size[0] - self.display_resolution[0] / 2):
            new_plane_shift = (self.plane_shift[0], new_plane_shift[1])  # Cancel x
        if (self.display_resolution[1] / 2) > player_pos[1] \
          or player_pos[1] > (self.level.world_size[1] - (self.display_resolution[1] / 2)):
            new_plane_shift = (new_plane_shift[0], self.plane_shift[1])  # Cancel y
        self.plane_shift = new_plane_shift




    def update_physics(self):
        self.physics_processing = True
        asyncio.run(self.terrain_manager.update())
        self.physics_processing = False


    def update(self, level: Level, timer: int, events: list[pg.event.Event]):
        # self.render_image.fill((0, 0, 0))  # For higher # of particles, this is faster
        # [self.render_image.set_at(pos, (0, 0, 0)) for pos in self.spaces_to_clear]
        # Update now blank spaces with the backdrop
        [self.render_image.set_at(pos, self.backdrop_surface.get_at(pos)) for pos in set(self.spaces_to_clear)]
        #TODO: Draw black/tiles if position is outside the bounds of the render image
        self.spaces_to_clear.clear()

        # self.render_image.blit(self.backdrop, (0, 0))



        # # visualization
        pg.draw.line(self.render_image, (0, 0, 255), (0, self.terrain_manager.ground),
                     (2400, self.terrain_manager.ground))  # Ground
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
    #TODO: Could remove the render_image surface and render everything on the cropped_surface first
    # That would require rendering the edges of the screen as player moves
        # Just blit a 720p rect of the render image onto a new surface and then do scaling up to window size
        draw_area = pg.Rect(self.plane_shift[0], self.plane_shift[1],
                                self.display_resolution[0], self.display_resolution[1])
        cropped_surface = pg.Surface((self.display_resolution[0], self.display_resolution[1]))
        # blit onto the cropped size surface and scale it up to the window size
        cropped_surface.blit(self.render_image, (0, 0), draw_area)
        resized_image = pg.transform.scale(cropped_surface, (self.render_scale[0], self.render_scale[1]))
        # blit the scaled image onto the screen display.
        self.screen.blit(resized_image, (0,0))
        # pg.Surface.blit(self.screen, self.render_image, (0, 0), draw_area)


        # print(f'memory % usage: {psutil.virtual_memory().percent}')
        # print(f'cpu % usage: {psutil.cpu_percent()}')

        pg.event.pump()
        pg.display.flip()  # updates the entire surface

        # pg.display.update(draw_area)  # With dynamic world size, this is 10% faster
        # Actually I don't think this makes sense with current method. I want to update the entire display window



class Clear_Spaces(set):
    def __init__(self, game):
        super(Clear_Spaces, self).__init__()
        self.game = game

    def add_pos(self, pos) -> bool:
        try:
            self.game.render_image.get_at(pos)
        except:
            print('failed to add position for clearing')
            return True
        self.add(pos)



