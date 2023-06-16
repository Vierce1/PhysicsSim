import pygame as pg
from pygame import time
from player import Player
import Blocks
from Blocks.block import Block
from Blocks.block_type import *
from Blocks import terrain_gen, terrain_manager
import physics
from quadtree import Quadtree


pg.init()
display_resolution = [2560, 1440]
screen = pg.display.set_mode(display_resolution)
physics.display_res = display_resolution
game_running = True

player = Player()
terrain_manager = terrain_manager.Terrain_Manager()
sand_blocks = terrain_gen.gen_terrain(block_list=(1000, Sand()), bounds=(0, 2560, 800, 1000),
                                      terrain_manager=terrain_manager)
terrain_manager.blocks.extend(sand_blocks)
block_rects = [block.rect for block in sand_blocks]
terrain_manager.block_rects.extend(block_rects)

y_count = 8
x_count = 14
# The quadtrees are slowing it down. More quadtrees = slower
width = display_resolution[1] / y_count
height = display_resolution[0] / x_count
quadtrees = []
for y in range(y_count):
    for x in range(x_count):
        quadtrees.append(Quadtree(x * width, y * height, width, height))
for quadtree in quadtrees:
    quadtree.north = [q for q in quadtrees if q.y == quadtree.y + 1]
    quadtree.south = [q for q in quadtrees if q.y == quadtree.y - 1]
    quadtree.east = [q for q in quadtrees if q.x == quadtree.x - 1]
    quadtree.west = [q for q in quadtrees if q.x == quadtree.x + 1]


clock = time.Clock()
timer = 0

while game_running:
    clock.tick(60)
    timer += 1
    print(clock.get_fps())

    events = pg.event.get()
    for event in events:
        if event.type == pg.QUIT:
            game_running = False

    # fill screen with black
    screen.fill((0, 0, 0))

    # visualization
    pg.draw.line(screen, (0, 0, 255), (0, 1100), (2400, 1100))  # Ground
    for q in quadtrees:
        pg.draw.line(screen, (255, 255, 255), (q.x, q.y), (q.x + q.width, q.y))
        pg.draw.line(screen, (255, 255, 255), (q.x, q.y), (q.x, q.y - q.height))

    # timed functions
    if timer > 60:
        block = terrain_gen.gen_terrain(block_list=(1, Sand()), bounds=(0, 2560, 800, 1000),
                                terrain_manager=terrain_manager)[0]
        # terrain_manager.blocks.extend(sand_blocks)
        sand_blocks.append(block)
        terrain_manager.blocks.append(block)
        terrain_manager.block_rects.append(block.rect)


    [q.objects.clear() for q in quadtrees]
    [terrain_manager.add_rect_to_quadtree(block, quadtrees) for block in sand_blocks]
    terrain_manager.update(screen)

    player.update(events, screen)

    pg.display.flip()  # updates the display. Could use display.update() and pass in PARTS of the screen to update

pg.quit()


