import asyncio
import pygame as pg
from pygame import time
from pygame.locals import *
from player import Player
from Blocks import terrain_gen as tg, terrain_manager as tm
from Blocks.block_type import Block_Type_Instance_List
from level import *
from environment import Environment
from ui import User_Interface
from particle_spawner import Particle_Spawner
import world_helpers as help
import psutil
import gc
import time
import sys


class Game:
    def __init__(self, window_size: list[int], display_resolution: list[int], screen: pg.Surface):
        self.display_resolution = display_resolution
        self.window_size = window_size
        self.screen = screen
        self.delay = .033  # 1000/85  # slowing the delay = more things happening each frame... which hurts fps
        gc.disable()
        self.render_image = pg.Surface((0, 0))  # for drawing world size + blit. Will be resized for the level
        self.render_dict = set()  #  tuples for position:color to draw
        self.spaces_to_clear = Clear_Spaces(self)  # set()
        self.spaces_to_erase = set()
        self.terrain_manager = tm.Terrain_Manager(self.display_resolution[0], self.display_resolution[1], self)
        self.terrain_gen = tg.Terrain_Gen(self.terrain_manager)
        self.player = Player(self.terrain_manager, self, window_size[0], window_size[1], display_resolution[0],
                             display_resolution[1], self.render_image)
        self.environ = Environment(wind=0)
        self.quadtree_nodes = set()
        self.plane_shift = (0, 0)  # x,y shift to apply to blit. Starts on the zero-point of the world.
                                    # Updates as player moves.
        self.render_scale = (self.window_size[0], self.window_size[1])
        self.level: Level
        self.backdrop = pg.image.load('background_1.png')
        self.backdrop_surface = pg.Surface((0,0))
        self.physics_processing = False
        self.physics_lag_frames = 0  # how many frames behind the GUI the physics rendering is
        self.ui = User_Interface(particle_button_types=[], game=self)
        self.mouse_pos = pg.mouse.get_pos()  # store this globally so classes can reference it
        self.particle_spawner = Particle_Spawner(terrain_manager=self.terrain_manager, terrain_gen=self.terrain_gen)
        self.trails = set()
        self.block_type_list = Block_Type_Instance_List()  # holds 1 instance of each block type for referencing values


    def setup(self, level: int) -> Level:
        # Level reading and creation
        level = Level_Getter().get_level(level=level)
        self.level = level
        self.environ = Environment(wind=level.wind)
        self.render_image = pg.Surface(level.world_size)
        print(f'world size: {self.render_image.get_size()}')
        self.terrain_manager.setup(render_image=self.render_image, world_size=level.world_size,
                                   ground_level=level.ground)
        self.player.set_start_position(level.start_pos)
        self.player.render_image = self.render_image

        # Set the plane shift to center the camera on the player's starting position
        self.plane_shift = self.adjust_start_planeshift(level.start_pos, level.world_size)
        print(f'plane shift: {self.plane_shift}')

        # Create all particles
        level_blocks = set()
        for i in range(len(level.block_counts)):  # iterate over all entries in the dict for this level
            blocks = self.terrain_gen.gen_terrain(block_count=level.block_counts[i],
                                block_type=level.block_types[i], bounds=level.bounds[i])
            level_blocks.update(blocks)
            if self.block_type_list[blocks[0].type].destroyable:
                self.terrain_manager.destroyable_blocks.update(blocks)

        # create a new UI every level? or just update buttons as needed?
        self.ui = User_Interface(particle_button_types=[block_type.SAND, block_type.GRAVEL, block_type.ROCK,
                                block_type.MUD, block_type.WATER, block_type.MAGMA], game=self)

        # Particle updating
        print(f'length of particles = {str(len(level_blocks))}')
        # have to add ALL blocks to this first so they draw on frame 1
        [self.terrain_manager.blocks.add(block) for block in level_blocks]  # Add Blocks first. Convert to ID later
        self.terrain_manager.all_blocks.extend(level_blocks)
        self.terrain_manager.fill_matrix()
        # Fill quadtree on load
        self.quadtree_nodes, created = self.terrain_manager.initialize_quadtree()
        # print(f'created {len(self.quadtree_nodes)} quadtree branch nodes')

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
            x_shift = 0
        elif start_pos[0] > world_size[0] - self.display_resolution[0] / 2:
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


    def get_mouse_pos(self, scale_for_render: bool = True):
        if scale_for_render:
            pos = help.get_scaled_pos(pg.mouse.get_pos(), self.plane_shift,
                            self.window_size[0], self.display_resolution[0],
                            self.window_size[1], self.display_resolution[1])
            return pos
        else:
            return pg.mouse.get_pos()


    def clear_spaces(self, clear_spaces: set):
        # check if block has moved into that position
        for pos in list(clear_spaces):
            empty = self.terrain_manager.matrix[pos] == -1
            if empty:
                self.render_image.set_at(pos, self.backdrop_surface.get_at(pos))

    def update_physics(self):
        self.physics_processing = True
        asyncio.run(self.terrain_manager.update())
        self.physics_processing = False

    def update_trails(self):
        for trail in list(self.trails):
            self.spaces_to_clear.add(trail.position)
            pos = trail.update_pos(self.terrain_manager.all_blocks[trail.parent_id])
            if not pos:
                self.trails.remove(trail)
                continue
            self.render_dict.add((pos, trail.color))



    def update(self, level: Level, timer: int, events: list[pg.event.Event]):
        # Take a copy of the spots to render in case physics rendering is lagging
        render_spots = list(self.render_dict)
        self.render_dict.clear()  # clear it immediately. Slower blocks will be drawn next frame.

        # Update now blank spaces with the backdrop
        # TODO: Weed out spaces that are now occuipied by other blocks
        self.clear_spaces(self.spaces_to_clear)
        # [self.render_image.set_at(pos, self.backdrop_surface.get_at(pos)) for pos in set(self.spaces_to_clear)]
        # self.erase_colors(set(self.spaces_to_erase))
        # self.set_colors(set(self.spaces_to_clear))
        #TODO: Draw black/tiles if position is outside the bounds of the render image
        self.spaces_to_clear.clear()


        [self.render_image.set_at(pos, color) for pos, color in render_spots]
        self.update_trails()


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
                self.terrain_manager.add_blocks_to_matrix(spawn_blocks)


        self.player.update(events)

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

        # Draw the UI last over everything else
        self.ui.render_buttons(self.screen)

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
            # print('failed to add position for clearing')
            return True
        self.add(pos)



