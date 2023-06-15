import pygame as pg
from player import Player
import Blocks
from Blocks.block import Block
from Blocks.block_type import *
from Blocks import terrain_gen


pg.init()
screen = pg.display.set_mode([1920, 1080])
game_running = True

player = Player()
sand_blocks = terrain_gen.gen_terrain(block_list=(100, Sand()), bounds=(600, 1000, 400, 800))


while game_running:
    events = pg.event.get()
    for event in events:
        if event.type == pg.QUIT:
            game_running = False

    # fill screen with black
    screen.fill((0, 0, 0))

    # draw blocks, each frame update position for each block
    for block in sand_blocks:


    # player movement
    player.accept_input(events=events, screen=screen)

    pg.display.flip()  # updates the display. Could use display.update() and pass in PARTS of the screen to update

pg.quit()



