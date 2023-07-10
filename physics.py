import Blocks.block_type as block_type
from Blocks.block_type import *
from Blocks import block
import pygame as pg


gravity = 2
terminal_velocity = 200
display_res = []
ground = 1008
collision_width = 0.25  # how far offset two blocks can be to still collide
frames_til_grounded = 120 # 100  # how many frames a block must be stationary before being grounded
slide_factor = .20  # how fast blocks slide horizontally
t_m = None


# @profile  # Massive memory hit
def check_down_collision(block, other_blocks: list):  # -> Block or bool
    other_blocks.remove(block)  # faster than checking block==other_block every iteration
    for oth_block in other_blocks:
        # t_m.total_col_dets += 1
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
    elif x_diff < block.type.friction * -1:
        return -1
    else:
        return 0


def check_side_collision(block, other_blocks: list, left_side: bool) -> bool:
    for oth_block in other_blocks:
        if left_side:
            return oth_block.rect.right == block.rect.left
        else:
            return oth_block.rect.left == block.rect.right




# Block functions
def update(block, screen):
    # print(f'# of leaves: {block.leaves}')
    if block.grounded_timer == frames_til_grounded:
        block.collision_detection = False
    neighboring_blocks = move(block)
    slide(block, neighboring_blocks)
    pg.draw.rect(surface=screen, color=block.type.color, rect=block.rect)


# @profile
def move(block) -> list:
    if not block.collision_detection: # or len(block.quadtrees) == 0:  #not block.quadtree:
        block.horiz_velocity = 0
        return []

    block.bottom_collide_block = None
    neighboring_blocks = []
    for quadtree in block.leaves:
        neighboring_blocks = t_m.get_neighbors(quadtree)
    collision = check_down_collision(block, neighboring_blocks)

    if collision:  # collided. Check if it should slide to either side
        block.vert_velocity = 0
        if collision != True:  # true means ground
            block.bottom_collide_block = collision

        if type(collision) is not bool and collision.vert_velocity == 0:
            slide = check_slide(block, collision)
            # check if there is a block in the way to stop sliding that direction
            block.horiz_velocity = slide * block.rect.width * slide_factor
        return neighboring_blocks
    if block.vert_velocity < terminal_velocity:
        block.vert_velocity += (gravity * block.move_speed)
    position = (block.rect.x, block.rect.y + block.vert_velocity)
    # block.rect = block.rect.move(position[0] - block.rect.x, position[1] - block.rect.y)
#TODO: Which is more efficient?
    block.rect.left = position[0]
    block.rect.top = position[1]
    # block.position = position
    return neighboring_blocks

def slide(block, neighboring_blocks) -> None:
    if block.vert_velocity > 0 or block.grounded_timer > frames_til_grounded \
            or (block.bottom_collide_block and block.bottom_collide_block.vert_velocity > 0):
        return
    if check_side_collision(block, neighboring_blocks, block.horiz_velocity < 0):
        block.horiz_velocity = 0
        return
    # not blocked to the side trying to slide
    position = (block.rect.x + block.horiz_velocity, block.rect.y)
    block.rect.left = position[0]
    block.rect.top = position[1]
    # block.position = position
    return