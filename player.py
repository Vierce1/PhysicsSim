import pygame as pg
import random
import world_helpers as help
import Blocks.terrain_manager as tm

class Player:
    def __init__(self, terrain_manager: tm.Terrain_Manager, game, screen_width, screen_height,
                 render_width, render_height):
        self.terrain_manager = terrain_manager
        self.game = game
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.render_width = render_width
        self.render_height = render_height
        self.position = (100, 100)
        self.size = 10
        self.move_speed = 10
        self.manipulation_distance = 600
        self.destroy_distance = 8

    def update(self, events, render_image):
        self.accept_input(events=events, render_image=render_image)


    def get_rect_pos(self, current_pos: (int, int), change: (int, int)):
        # self.position = tuple(map(sum, zip(current_pos, change)))
        self.position = (current_pos[0] + change[0], current_pos[1] + change[1])
        return self.position


    def accept_input(self, events, render_image: pg.display):
        pos_change = (0, 0)
        keys = pg.key.get_pressed()
        if keys[pg.K_a]:
            pos_change = (-1 * self.move_speed, pos_change[1])
        if keys[pg.K_d]:
            pos_change = (1 * self.move_speed, pos_change[1])
        if keys[pg.K_w]:
            pos_change = (pos_change[0], -1 * self.move_speed)
        if keys[pg.K_s]:
            pos_change = (pos_change[0], 1 * self.move_speed)

        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos = help.get_scaled_pos(pg.mouse.get_pos(), self.screen_width, self.render_width,
                                                self.screen_height, self.render_height)
                self.mouse_click(mouse_pos)


        for y in range(self.size):
            for x in range(self.size):
                pos = (self.position[0] + x, self.position[1] + y)
                render_image.set_at(pos, (0, 0, 0))

        player_position = self.get_rect_pos(current_pos=self.position, change=pos_change)
        pg.draw.rect(surface=render_image, color=(255, 255, 255),
                     rect=(player_position[0], player_position[1], self.size, self.size))


    def mouse_click(self, mouse_pos: (int, int)):
        distance = help.check_dist(self.position, mouse_pos)
        if distance < self.manipulation_distance:
            self.destroy(mouse_pos, 50)



#TODO: Consider reimplementing quadtree that classifies blocks for 1 frame rather than using all undestroyable blocks
# When dealing with  200k destroyable blocks, see an fps drop (~ 8fps)
    def destroy(self, location: (int, int), force: int):
        blocks = self.terrain_manager.destroyable_blocks
        in_range_blocks = help.get_blocks_in_dist(pos=location, block_list=blocks, distance=self.destroy_distance)
        for block in in_range_blocks:
            if not block.type.destroyable:
                continue
            self.terrain_manager.destroy_block(block)

        # if len(in_range_blocks) > 0:
        self.terrain_manager.trigger_ungrounding(location)



