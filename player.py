import pygame as pg
import random
import world_helpers as help
import Blocks.terrain_manager as tm


class Player:
    def __init__(self, terrain_manager: tm.Terrain_Manager, game, screen_width, screen_height,
                 render_width, render_height, render_image: pg.Surface):
        self.terrain_manager = terrain_manager
        self.game = game
        self.render_image = render_image
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.render_width = render_width
        self.render_height = render_height
        self.position = (200, 200)
        self.size = 10
        self.rect = pg.Rect(self.position[0], self.position[1], self.size, self.size)
        self.move_speed = 18
        self.vertical_speed = 0
        self.manipulation_distance = 500
        self.destroy_distance = 8
        self.button_cooldown = 10
        self.button_timer = 0
        self.particle_spawn_count = 10
        self.base_particle_spawn_count = 10
        self.high_rate_particle_spawn_count = 20

    def set_start_position(self, start_pos: (int, int)):
        self.position = start_pos
        print(f'start at {start_pos}')
        self.rect.x, self.rect.y = start_pos[0], start_pos[1]


    def update(self, events):
        self.accept_input(events=events, render_image=self.render_image)
        grounded = False
        for _ in range(self.vertical_speed):
            grounded = self.fall()
        if not grounded and self.vertical_speed < self.terrain_manager.terminal_velocity:
            # TODO: Need to revamp this for gravity direction changes
            self.vertical_speed += self.terrain_manager.gravity

        pg.draw.rect(surface=self.render_image, color=(255, 255, 255), rect=self.rect)


    def fall(self) -> bool:
        grounded = self.terrain_manager.check_under_player((self.position[0], self.rect.bottom + 1))
        if not grounded:
            [self.game.spaces_to_clear.add_pos(pos) for pos in self.get_covered_pixels()]
            self.position = (self.position[0], self.position[1] + 1)
            self.rect.y = self.position[1]
            self.game.update_plane_shift(change=(0, -1), player_pos=self.position)
            return False
        else:
            self.vertical_speed = 0
            return True

    def get_rect_pos(self, current_pos: (int, int), change: (int, int)):
        # self.position = tuple(map(sum, zip(current_pos, change)))
        self.rect.x = current_pos[0] + change[0]
        self.rect.y = current_pos[1] + change[1]
        return (self.rect.x, self.rect.y)

    def get_covered_pixels(self) -> list[(int, int)]:  # returns all pixels covered by player
        pixels = []
        for x in range(self.size):
            for y in range(self.size):
                pixels.append((self.position[0] + x, self.position[1] + y))
        return pixels


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
        if keys[pg.K_q]:
            self.position = self.get_rect_pos(self.position, (0, -25))
            self.game.update_plane_shift((0, 25), self.position)
            self.vertical_speed = 0
        if keys[pg.K_SPACE] and self.button_timer > self.button_cooldown:
            self.button_timer = 0
            mouse_pos = self.game.get_mouse_pos()
            self.explode(location=mouse_pos, destroy_radius=1, force_radius=15, force=15)

        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos = self.game.get_mouse_pos(scale_for_render=True)
                if event.button == 1 and self.button_timer > self.button_cooldown:  # left click
                    self.button_timer = 0
                    self.left_click(mouse_pos)
            if event.type == pg.MOUSEMOTION:
                dx, dy = event.rel
                if (dx**2 + dy**2) > 5**2:
                    self.particle_spawn_count = self.high_rate_particle_spawn_count
                else:
                    self.particle_spawn_count = self.base_particle_spawn_count
        if pg.mouse.get_pressed(3)[2]:
            mouse_pos = self.game.get_mouse_pos(scale_for_render=True)
            self.right_click(mouse_pos)




        for y in range(self.size):
            for x in range(self.size):
                pos = (self.rect.x + x, self.rect.y + y)
                render_image.set_at(pos, (0, 0, 0))

        if pos_change[0] != 0:
            self.move(pos_change, render_image)

        self.button_timer += 1



    def move(self, direction, render_image):
        change = direction
        # Check if need to go up slope first
        if self.terrain_manager.check_walk_slope(self.position, direction):
            change = (change[0], change[1] - 1)
        [self.game.spaces_to_clear.add_pos(pos) for pos in self.get_covered_pixels()]
        self.position = self.get_rect_pos(current_pos=self.position, change=change)
        # Update the camera position.
        # Alternative way would be to use the player's finite world position.
        self.game.update_plane_shift((-change[0], -change[1]), self.position)



    def check_dist(self, location: (int, int)):
        distance = help.check_dist(self.position, location)
        return distance < self.manipulation_distance


    def right_click(self, mouse_pos: (int, int)):
        self.game.particle_spawner.spawn(x=mouse_pos[0], y=mouse_pos[1], count=self.particle_spawn_count)


    def left_click(self, mouse_pos: (int, int)):
        # Check if a button is covering this spot
        if self.game.ui.check_if_button_in_pos(mouse_pos):
            return
        if self.check_dist(mouse_pos):
            print(f'click at {mouse_pos}')
            self.destroy(mouse_pos)



    def destroy(self, location: (int, int)):
        blocks = self.terrain_manager.destroyable_blocks
        # don't bother inserting location. We just want to get the neighboring objects
        # Now that I save the block ID in the matrix don't really need quadtree... see explode
        quadtree_node = self.terrain_manager.insert_object_quadtree(None, location[0], location[1])
        if not quadtree_node or not quadtree_node.objects:
            return
        in_range_blocks = quadtree_node.objects
        for child in quadtree_node.parent.children:  # go up 1 branch to be safe. May need tweaking
            in_range_blocks.update(child.objects)
        # print(f'neighboring objects: {len(in_range_blocks)}')
        for block in in_range_blocks:
            if not self.game.block_type_list[block.type].destroyable:
                continue
            # get distance
            if help.get_blocks_in_dist(pos=location, block_list={block}, distance=self.destroy_distance):
                self.terrain_manager.destroy_block(block.id)


    def explode(self, location: (int, int), destroy_radius: int, force_radius: int, force: int):
        if not self.check_dist(location):
            return
        print(f'space at {location}')
        # get blocks in radius around location point
        #TODO: Make it a circular radius. Pi?
        location = (round(location[0]), round(location[1]))
        for x in range(location[0]-force_radius, location[0]+force_radius + 1):
            for y in range(location[1]-force_radius, location[1]+force_radius + 1):
                id = (self.terrain_manager.matrix[x, y])
                if id != -1:
                    block = self.terrain_manager.all_blocks[id]
                    if location[0] - destroy_radius < x < location[0] + destroy_radius \
                      and location[1] - destroy_radius < y < location[1] + destroy_radius:
                        self.terrain_manager.destroy_block(id)
                        continue

                    #TODO: Should this be revamped? Currently particles on the edges of the explosion get more force.
                    # horiz = round((location[0] - x) / force_radius * force)
                    # verti = round((location[1] - y) / force_radius * force)
                    # middle gets full force. Doesn't work well.
                    # horiz = round((force_radius - (location[0] - x)) / force_radius * force)
                    # verti = round((force_radius - (location[1] - y)) / force_radius * force)
                    # This is better but need to make it a circle. there needs to be some factor in here.
                    horiz = -force if x < location[0] else force
                    if -force_radius / 2 < location[0] - x < force_radius / 2:
                        horiz = round(horiz / 2)
                    verti = -force if y < location[1] else force
                    if -force_radius / 2 < location[1] - y < force_radius / 2:
                        verti = round(verti / 2)
                    self.terrain_manager.trigger_ungrounding(block.id, block.position)
                    block.collision_detection = True
                    block.horiz_velocity = horiz
                    block.vert_velocity = verti
                    # if block in self.terrain_manager.inactive_blocks:
                    self.terrain_manager.blocks.add(block.id)
                        # self.terrain_manager.inactive_blocks.remove(block)




