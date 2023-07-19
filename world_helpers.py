import math

def check_dist(pos_1: (int, int), pos_2: (int, int)) -> int:
    return round(math.dist(pos_1, pos_2))

def get_blocks_in_dist(pos: (int, int), block_list: set, distance: int) -> set:
    blocks = set()
    for block in block_list:
        # dist = (block.position[0] - pos[0])**2 + (block.position[1] - pos[1])**2 < distance**2
        dist = math.sqrt((block.position[0] - pos[0])**2 + (block.position[1] - pos[1])**2)
        if dist < distance:
            blocks.add(block)
    return blocks

def get_scaled_pos(position: (int, int), world_offset: (int, int), screen_width: int, render_width: int,
                   screen_height: int, render_height: int) -> (int, int):
    print(f'unscaled position: {position}')
    # If change the resolution will need to mess with this
    ratio_x = (screen_width / render_width)
    ratio_y = (screen_height / render_height)
    print(f'screen size: {screen_width} / {screen_height}    render size : {render_width} / {render_height}')
    print(f'world offset: {world_offset}')
    converted_pos = (round(position[0] / ratio_x + world_offset[0]), round(position[1] / ratio_y + world_offset[1]))
    print(f'converted position: {converted_pos}')
    return converted_pos
    # return (position[0] - world_offset[0], position[1] - world_offset[1])
