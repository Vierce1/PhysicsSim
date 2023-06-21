import Blocks.block_type as block_type
from Blocks.block_type import *
from Blocks import block
import pygame as pg


gravity = 2
terminal_velocity = 200
display_res = []
ground = 1400
collision_width = 0.25  # how far offset two blocks can be to still collide
frames_til_grounded = 80 # 100  # how many frames a block must be stationary before being grounded

# to improve processing efficiency, divide screen into quadtrees & only pass in blocks in same + neighboring quadtrees
def check_down_collision(block, other_blocks: list):  # -> Block or bool
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
                return oth_block
    if block.rect.y + block.rect.height >= ground:  # block is at ground level, stop detecting collision
        block.collision_detection = None
        return True

    return None


def check_slide(block, collided_block) -> int:  # int -1 for slide left, 1 slide right, 0 no slide
    # get relative x position of block against the collided block
    x_diff = block.rect.centerx - collided_block.rect.centerx
    # incorporate the friction to determine if it slides off
    if x_diff > block.type.friction:
        return 1
    elif x_diff * -1 < block.type.friction:
        return -1
    else:
        return 0


def check_collision(block, other_blocks: list, side: (int, int)) -> bool:








# alternate methods:
  # Every block seeds its position to a master list
  # Run through the positions moving left->right, bottom->top
  # if there is a block in the checked position, check if it has a block beneath it
  # if so, flip a bool in the block

