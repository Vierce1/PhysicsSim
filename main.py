import pygame as pg
from pygame import time
from player import Player
import Blocks
from Blocks.block import Block
from Blocks.block_type import *
from Blocks import terrain_gen, terrain_manager



pg.init()
display_resolution = [2560, 1440]
screen = pg.display.set_mode(display_resolution)
game_running = True

player = Player()
terrain_manager = terrain_manager.Terrain_Manager()
sand_blocks = terrain_gen.gen_terrain(block_list=(1000, Sand()), bounds=(0, 2560, 800, 1200),
                                      terrain_manager=terrain_manager)
terrain_manager.blocks.extend(sand_blocks)
block_rects = [block.rect for block in sand_blocks]
terrain_manager.block_rects.extend(block_rects)

clock = time.Clock()

while game_running:
    clock.tick(60)
    events = pg.event.get()
    for event in events:
        if event.type == pg.QUIT:
            game_running = False

    # fill screen with black
    screen.fill((0, 0, 0))

    terrain_manager.update(screen)

    player.update(events, screen)

    pg.display.flip()  # updates the display. Could use display.update() and pass in PARTS of the screen to update

pg.quit()




