import Blocks.block_type as block_type
from Blocks.block_type import *
from Blocks import block
import pygame as pg
import random


gravity = 1
terminal_velocity = 1
display_res = []
ground = 1008
frames_til_grounded = 120  # how many frames a block must be stationary before being grounded
slide_factor = 1  # how fast blocks slide horizontally
t_m = None



def check_under(block):
    if block.position[1] == ground:
        return True
    return t_m.matrix[block.position[0], block.position[1] + block.height] == 1

# def check_side()



def check_slide(block) -> int:  # int -1 for slide left, 1 slide right, 0 no slide
    dir = 1 if random.random() < 0.5 else -1
    if t_m.matrix[block.position[0] + block.width * dir, block.position[1] + block.height] == 0:
        return 1
    elif t_m.matrix[block.position[0] + block.width * -dir, block.position[1] + block.height] == 0:
        return -1
    return 0





# Block functions
def update(block, screen):
    if block.collision_detection:
        if block.grounded_timer == frames_til_grounded:
            block.collision_detection = False
        move(block)
    screen.set_at(block.position, block.type.color)


# @profile
def move(block):
    if block.position[1] == ground - 1:
        block.horiz_velocity = 0
        return

    collision = check_under(block)

    if collision:  # collided. Check if it should slide to either side + down 1
        block.vert_velocity = 0

        # May need to check if block under it is going to move this frame?
        slide = check_slide(block)
        block.horiz_velocity = slide * 1 * slide_factor
        t_m.matrix[block.position[0], block.position[1]] = 0
        block.position = (block.position[0] + block.horiz_velocity, block.position[1])
        # block.rect.left = position[0]
        # block.rect.top = position[1]
        t_m.matrix[block.position[0], block.position[1]] = 1
        return
        #     # check if there is a block in the way to stop sliding that direction

        # return neighboring_blocks

    if block.vert_velocity < terminal_velocity:
        block.vert_velocity += gravity

    # mark prev position empty
    t_m.matrix[block.position[0], block.position[1]] = 0
    block.position = (block.position[0], block.position[1] + block.vert_velocity)
    # block.rect.left = position[0]
    # block.rect.top = position[1]
    t_m.matrix[block.position[0], block.position[1]] = 1
    return


def slide(block) -> None:
    if block.vert_velocity > 0 or block.grounded_timer > frames_til_grounded \
            or (block.bottom_collide_block and block.bottom_collide_block.vert_velocity > 0):
        return
    # not blocked to the side trying to slide
    position = (block.position[0] + block.horiz_velocity, block.position[1])
    return