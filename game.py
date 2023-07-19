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
        self.render_scale = (display_resolution[0], display_resolution[1])
        self.level: Level = None
        self.backdrop = pg.image.load('background_1.png')
        self.backdrop_surface = pg.Surface((0,0))


    def setup(self, level: int) -> Level:
        # Level reading and creation
        level = Level_Getter().get_level(level=level)
        self.level = level
        self.render_image = pg.Surface(level.world_size)
        print(f'world size: {self.render_image.get_size()}')
        # self.render_scale = (self.window_size[0] / level.world_size[0], self.window_size[1] / level.world_size[1])
        self.terrain_manager.setup(render_image=self.render_image, world_size=level.world_size)
        self.player.set_start_position(level.start_pos)
        self.player.render_width, self.player.render_height = level.world_size[0], level.world_size[1]
        # Set the plane shift to center the camera on the player's starting position
        # self.plane_shift = (self.display_resolution[0] * .5 - level.start_pos[0],
        #                     self.display_resolution[1] / 2 - level.start_pos[1])
        self.plane_shift = (level.start_pos[0] - self.display_resolution[0] / 2,  # this is corerct
                            level.start_pos[1])
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


    def update_plane_shift(self, change: (int, int), player_pos: (int, int)):
        # First check if hitting the bounds of the level
        new_plane_shift = (self.plane_shift[0] - change[0], self.plane_shift[1] - change[1])
        if (self.display_resolution[0]) > player_pos[0] \
          or player_pos[0] > (self.level.world_size[0] - (self.display_resolution[0])):
            new_plane_shift = (self.plane_shift[0], new_plane_shift[1])  # Cancel x
        if (self.display_resolution[1]) > player_pos[1] \
          or player_pos[1] > (self.level.world_size[1] - (self.display_resolution[1])):  # /2
            new_plane_shift = (new_plane_shift[0], self.plane_shift[1])  # Cancel y
        self.plane_shift = new_plane_shift


    def update(self, level: Level, timer: int, events: list[pg.event.Event]):
        # self.render_image.fill((0, 0, 0))  # For higher # of particles, this is faster
        # [self.render_image.set_at(pos, (0, 0, 0)) for pos in self.spaces_to_clear]
        # Update now blank spaces with the backdrop
        [self.render_image.set_at(pos, self.backdrop_surface.get_at(pos)) for pos in self.spaces_to_clear]
        #TODO: Draw black/tiles if position is outside the bounds of the render image
        self.spaces_to_clear.clear()

        # self.render_image.blit(self.backdrop, (0, 0))

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
        # sub_surface = self.render_image.subsurface(pg.Rect(self.plane_shift[0] - 640, self.plane_shift[1], 1280, 720))
        # draw_area = self.render_image.get_rect().move(self.plane_shift[0], self.plane_shift[1])
        print(self.plane_shift)
        draw_area = pg.Rect(self.player.position[0] - self.display_resolution[0] / 2, 0, 1280, 720)
                            #  -self.plane_shift[1] + self.display_resolution[1] , 1280, 720)
        # TODO: Figure out scaling that doesn't reduce framerate
        # Just blit a 720p rect of the render image onto the screen and then do scaling up to window size
        # resized_screen = pg.transform.scale(self.render_image, (self.render_scale[0],
        #                                                         self.render_scale[1]))
        # pg.transform.scale_by(self.render_image, 1.5, self.screen)  # error, scale must match screen size

        # pg.transform.scale(self.render_image, self.render_scale, self.screen)
        # resized_screen = pg.transform.scale_by(self.render_image, 1.5)
        self.screen.blit(self.render_image, (0, 0), draw_area)
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

    def add_pos(self, pos) -> None:
        try:
            self.game.render_image.get_at(pos)
        except:
            print('failed to add position for clearing')
            return
        self.add(pos)



