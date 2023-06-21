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
blocks = terrain_gen.gen_terrain(block_list=(300, Sand()), bounds=(620, 780, 100, 600),
                                      terrain_manager=terrain_manager)
rocks = terrain_gen.gen_terrain(block_list=(800, Rock()), bounds=(600, 800, 800, 900),
                                      terrain_manager=terrain_manager)
blocks.extend(rocks)
blocks.extend(terrain_gen.gen_terrain(block_list=(100, Rock()), bounds=(580, 599, 760, 800),
                                      terrain_manager=terrain_manager))
blocks.extend(terrain_gen.gen_terrain(block_list=(100, Rock()), bounds=(801, 820, 760, 800),
                                      terrain_manager=terrain_manager))
print(f'length of blocks = {str(len(blocks))}')

terrain_manager.blocks.extend(blocks)
block_rects = [block.rect for block in blocks]
terrain_manager.block_rects.extend(block_rects)

# Initial load time goes up with more cells, but fps is better
y_count = round(display_resolution[1] / 45)  #45) # 72
x_count = round(display_resolution[0] / 50) #50) # 80
# The quadtrees are slowing it down. More quadtrees = slower
width = display_resolution[0] / x_count
height = display_resolution[1] / y_count
quadtrees = []
for y in range(y_count):
    for x in range(x_count):
        # order of appending doesn't matter, what matters is how blocks get added
        quadtrees.append(Quadtree(x * width, y * height, width, height))
for quadtree in quadtrees:
    quadtree.north = next(iter([q for q in quadtrees if q.y == quadtree.y - q.height and q.x == quadtree.x]), None)
    quadtree.south = next(iter([q for q in quadtrees if q.y == quadtree.y + q.height and q.x == quadtree.x]), None)
    quadtree.east = next(iter([q for q in quadtrees if q.x == quadtree.x + q.width and q.y == quadtree.y]), None)
    quadtree.west = next(iter([q for q in quadtrees if q.x == quadtree.x - q.width and q.y == quadtree.y]), None)
[terrain_manager.add_rect_to_quadtree(block, quadtrees) for block in blocks]


clock = time.Clock()
timer = 0
# bliting slowed down by 30%+. Drawing directly on screen faster
# render_image = pg.Surface((display_resolution[0], display_resolution[1]))  # for drawing offscreen first

print('\n\nGame Loaded')
while game_running:
    clock.tick(60)
    timer += 1
    print(f'fps: {str(round(clock.get_fps()))}')


    events = pg.event.get()
    for event in events:
        if event.type == pg.QUIT:
            game_running = False

    # fill screen with black
    # render_image.fill((0, 0, 0))
    screen.fill((0, 0, 0))

    # # visualization
    pg.draw.line(screen, (0, 0, 255), (0, physics.ground), (2400, physics.ground))  # Ground
    for q in quadtrees:
        pg.draw.line(screen, (255, 255, 255), (q.x, q.y), (q.x + q.width, q.y))
        pg.draw.line(screen, (255, 255, 255), (q.x, q.y), (q.x, q.y - q.height))

    # timed functions
    if timer > 60:
        new_blocks = terrain_gen.gen_terrain(block_list=(1, Sand()), bounds=(620, 780, 0, 200),
                                terrain_manager=terrain_manager)
        # terrain_manager.blocks.extend(blocks)
        blocks.extend(new_blocks)
        terrain_manager.blocks.extend(new_blocks)
        [terrain_manager.block_rects.extend(block.rect) for block in new_blocks]
        [terrain_manager.add_rect_to_quadtree(block, quadtrees) for block in new_blocks]



# TODO: Big slowdown occurs from this method:
    # [q.objects.clear() for q in quadtrees if len(q.objects) > 0]
    # [terrain_manager.add_rect_to_quadtree(block, quadtrees) for block in blocks]

    # Updated to this, fixes FPS. No longer have object list being cleared and recreated every frame
    # Only blocks that leave their quadtree look for new ones.
    [terrain_manager.update_block_quadtree(block=block) for block in blocks if block.collision_detection] # and block.quadtree

    terrain_manager.update(screen=screen)
    # render_image.convert()  # optimize image after drawing on it
    # draw_area = render_image.get_rect().move(0, 0)
    # screen.blit(render_image, draw_area)  # blitting was slower

    # player.update(events, screen)

    pg.event.pump()
    pg.display.flip()  # updates the display. Could use display.update() and pass in PARTS of the screen to update

pg.quit()


