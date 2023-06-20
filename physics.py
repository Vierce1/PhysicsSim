import Blocks.block_type as block_type
from Blocks.block_type import *
from Blocks import block
import pygame as pg


gravity = .3  # 9.8
terminal_velocity = 10 # 26
display_res = []
ground = 1400

# to improve processing efficiency, divide screen into grid & only pass in blocks in same + neighboring grids
# or, pass in any blocks that are within x distance of the block. WOuld involve looping thorugh all blocks
def check_collision(block, other_blocks: list) -> bool:
    for oth_block in other_blocks:
        if oth_block == block:
            continue
            #  and block.rect.centery < oth_block.rect.centery \
        if block.rect.bottom - oth_block.rect.top <= 0 \
            and -1 * oth_block.rect.width <= oth_block.rect.centerx - block.rect.centerx <= oth_block.rect.width:
            # and -1 * oth_block.rect.width <= oth_block.rect.centerx - block.rect.centerx <= oth_block.rect.width:
                # move the block back 1 frame so they aren't occluded. Grid system will also help with this
        # had to remove this because it was bouncing blocks out of their quadtree
                # block.rect.bottom = oth_block.rect.top
                block.grounded_timer += 1
                # print(f'collission timer {str(block.grounded_timer)}.')
                return True
    if block.rect.y + block.rect.height >= ground:  # block is at ground level, stop detecting collision
        block.collision_detection = False
        return True

    return False


def update_block_quadtree(block):
    x_change = block.rect.centerx - block.quadtree.x
    y_change = block.rect.centery - block.quadtree.y
    if x_change < 0 or x_change > block.quadtree.width \
        or y_change < 0 or y_change > block.quadtree.height:
        # no longer inside the quadtree. assign it to the new one
        block.quadtree.objects.remove(block)
        # block.quadtree.objects = [b for b in block.quadtree.objects if b != block]

        if y_change > 0 :  # assign south
            print("assigning south. Quadtree origin = " + str(block.quadtree.x / block.quadtree.width) + "  /  " \
                  + str(block.quadtree.y / block.quadtree.height))
            block.quadtree.south.objects.append(block)
            block.quadtree = block.quadtree.south
            print('new block quadtree at ' + str(block.quadtree.y) + '  '
                        '(position ' + str(block.quadtree.y / block.quadtree.height) + ')\n')
        elif x_change < 0 and block.quadtree.west:  # assign west
            block.quadtree.west.objects.append(block)
            block.quadtree = block.quadtree.west
        elif x_change > 0 and block.quadtree.east:  # assign east
            block.quadtree.east.objects.append(block)
            block.quadtree = block.quadtree.east
        elif y_change < 0 and block.quadtree.north:  # assign north
            block.quadtree.north.objects.append(block)
            block.quadtree = block.quadtree.north









# alternate methods:
  # Every block seeds its position to a master list
  # Run through the positions moving left->right, bottom->top
  # if there is a block in the checked position, check if it has a block beneath it
  # if so, flip a bool in the block

