import Blocks.block_type as block_type
from Blocks.block_type import *
from Blocks import block
import pygame as pg


gravity = 2
terminal_velocity = 200
display_res = []
ground = 1400
collision_width = 0.25  # how far offset two blocks can be to still collide
frames_til_grounded = 100  # how many frames a block must be stationary before being grounded

# to improve processing efficiency, divide screen into quadtrees & only pass in blocks in same + neighboring quadtrees
def check_collision(block, other_blocks: list) -> bool:
    for oth_block in other_blocks:
        if oth_block == block:
            continue
        if block.rect.bottom - oth_block.rect.top >= 0 and block.rect.centery < oth_block.rect.centery \
            and -1 * (oth_block.rect.width + block.rect.width) * collision_width <= \
                oth_block.rect.centerx - block.rect.centerx \
                <= (oth_block.rect.width + block.rect.width) * collision_width:
                # move the block back 1 frame so they aren't occluded. Grid system will also help with this
        # had to remove this because it was bouncing blocks out of their quadtree
                # block.rect.bottom = oth_block.rect.top
                block.grounded_timer += 1
                return True
    if block.rect.y + block.rect.height >= ground:  # block is at ground level, stop detecting collision
        block.collision_detection = False
        return True

    return False


# def check_slide(block, collided_block) -> int:  # int -1 for slide left, 1 slide right, 0 no slide
#     # get relative x position of block
#     x_diff = block.rect.centerx - collided_block.rect.centerx
#     # incorporate the friction
#     if block.type.friction









# alternate methods:
  # Every block seeds its position to a master list
  # Run through the positions moving left->right, bottom->top
  # if there is a block in the checked position, check if it has a block beneath it
  # if so, flip a bool in the block

