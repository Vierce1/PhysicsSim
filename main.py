import pygame as pg
from pygame import time
from pygame.locals import *
from game import Game
from player import Player
import Blocks
from Blocks.block import Block
from Blocks.block_type import *
from Blocks import terrain_gen, terrain_manager
import gc


pg.init()
window_size = [1920, 1080]
display_resolution = [1280, 720]
flags = FULLSCREEN | DOUBLEBUF  # 5 FPS boost
screen = pg.display.set_mode(window_size)
gc.disable()

game_running = True


game = Game(window_size=window_size, display_resolution=display_resolution, screen=screen)  # main game functions
level = game.setup(level=3)

clock = time.Clock()
timer = 0
# bliting slowed down by 30%+. Drawing directly on screen faster
pg.event.set_allowed([pg.QUIT, pg.KEYDOWN, pg.KEYUP]) # limit allowed events we have to check for every frame



print('\n\nGame Loaded')
while game_running:
    clock.tick(30)  # Limit to 30fps. This is the most consistent method and don't see drops when limiting
                    # the frame rate and then stuff happening
    fps = clock.get_fps()
    timer += 1 / fps if fps > 0 else 0
    print(f'fps: {str(round(fps))}')


    events = pg.event.get()
    for event in events:
        if event.type == pg.QUIT:
            game_running = False

    game.update(level=level, timer=timer, events=events)

pg.quit()


