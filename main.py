import pygame as pg
from pygame import time
from pygame.locals import *
from game import Game
from player import Player
import Blocks
from Blocks.block import Block
from Blocks.block_type import *
from Blocks import terrain_gen, terrain_manager
import physics
from quadtree import Quadtree
import gc


pg.init()
display_resolution = [1920,1080]
flags = FULLSCREEN | DOUBLEBUF  # 5 FPS boost
screen = pg.display.set_mode(display_resolution)
gc.disable()

physics.display_res = display_resolution
game_running = True


game = Game(display_resolution=display_resolution, screen=screen)  # main game functions
game.setup()

clock = time.Clock()
timer = 0
# bliting slowed down by 30%+. Drawing directly on screen faster
# render_image = pg.Surface((display_resolution[0], display_resolution[1]))  # for drawing offscreen first
pg.event.set_allowed([pg.QUIT, pg.KEYDOWN, pg.KEYUP]) # limit allowed events we have to check for every frame

print('\n\nGame Loaded')
while game_running:
    clock.tick(999)
    timer += 1
    print(f'fps: {str(round(clock.get_fps()))}')


    events = pg.event.get()
    for event in events:
        if event.type == pg.QUIT:
            game_running = False

    game.update(timer=timer, events=events)

pg.quit()


