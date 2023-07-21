from multiprocessing import Pool
import random


class MP_Physics:
    def __int__(self, blocks, terrain_manager):
        self.blocks = blocks
        self.tm = terrain_manager


    async def update(self, blocks):
        self.blocks = blocks
        pool = Pool(4)
        # pool.map(self.update_blocks, self.blocks)
        pool.map(self.do_nothing, self.blocks)
        pool.close()
        pool.join()

    def do_nothing(self, block):
        pass


    def check_pos_collide(self, position: (int, int)) -> bool:
        if position[1] == self.tm.ground:
            return True
        return self.tm.matrix[position] != -1


    #TODO: Remove and change player to use check_pos_collide
    def check_under(self, position: (int, int)) -> bool:
        if position[1] == self.tm.ground:
            return True
        return self.tm.matrix[(position[0], position[1] + 1)] != -1


    #TODO: Somehow sand can overwrite dirt when flowing down a slope and hitting the sloped ceiling
    def check_slide(self, block) -> (int, int):  # int -1 for slide left, 1 slide right, 0 no slide
        if block.type.name == 'sand':
            return self.tm.solid_slide(block)
        elif block.type.name == 'water':
            return self.tm.water_slide(block)

    def solid_slide(self, block) -> (int, int):
        dir = 1 if random.random() < 0.5 else -1
        if self.tm.matrix[(block.position[0] + dir, block.position[1] + 1)] == -1:  # EMPTY:
            return (dir, 1)
        elif self.tm.matrix[(block.position[0] - dir, block.position[1] + 1)] == -1:  # EMPTY:
            return (-dir, 1)
        return (0,0)

    def water_slide(self, block) -> (int, int): # int -1 for slide left, 1 slide right, 0 no slide
        dir = 1 if random.random() < 0.5 else -1
        if block.vert_velocity > 0:
            return (0,0)
        under_block_id = self.tm.matrix[(block.position[0]), block.position[1] + 1]
        side_block_id = self.tm.matrix[(block.position[0] + dir, block.position[1])]
        while under_block_id != -1 and side_block_id == -1:
            #  more than 1 deep. try to spread out. Do it all in 1 frame to sim water
            block.position = (block.position[0] + dir, block.position[1])
            under_block_id = self.tm.matrix[(block.position[0]), block.position[1] + 1]
            side_block_id = self.tm.matrix[(block.position[0] + dir, block.position[1])]
        # Found a spot where there isn't water beneath
        block.position = (block.position[0] + dir, block.position[1] + 1)
        return (0, 0)


    def check_slope(self, position: (int, int), direction: int) -> bool:
        if self.tm.matrix[(position[0] + direction[0], position[1])] != -1 \
                and self.tm.matrix[(position[0] + direction[0], position[1] - 1)] == -1:  # EMPTY:
            return True
        return False





    # Particle functions
    def update_blocks(self, block):
        if block.collision_detection:
            if block.grounded_timer >= 320:
                block.collision_detection = False
                self.tm.inactive_blocks.add(block)
                self.tm.blocks.remove(block)

            # update velocities
            if block.vert_velocity < self.tm.terminal_velocity:
                block.vert_velocity += self.tm.gravity
            if block.horiz_velocity != 0:
                block.horiz_velocity -= int(block.horiz_velocity / abs(block.horiz_velocity))

            # move through all spaces based on velocity
            total_x = block.horiz_velocity
            total_y = block.vert_velocity
            for _ in range(0, max(abs(block.vert_velocity), abs(block.horiz_velocity))):
                next_x, next_y = self.tm.get_step_velocity(total_x, total_y)
                collided = self.move(block, next_x, next_y)
                if collided:
                    break
                total_x -= total_x / abs(total_x) if total_x != 0 else 0  # decrement by 1 in correct direction
                total_y -= total_y / abs(total_y) if total_y != 0 else 0  # but stop if it gets to zero


            if block.vert_velocity == 0:
                block.grounded_timer += 1  # Increment grounded timer to take inactive blocks out of set

        elif block in self.tm.blocks:
            self.tm.blocks.remove(block)

        # tm.render_image.set_at(block.position, block.type.color)



    def move(self, block, x_step: int, y_step: int) -> bool:  # returns collided, to end the movement loop
        if block.position[1] == self.tm.ground - 1:
            block.horiz_velocity = 0
            block.vert_velocity = 0
            return True
        next_pos = (block.position[0] + x_step, block.position[1] + y_step)
        collision = self.check_pos_collide(next_pos)

        if collision:  # collided. Check if it should slide to either side + down 1
            block.horiz_velocity = 0  # Ideally both axes would not necessarily go to zero
            block.vert_velocity = 0
            slide = self.check_slide(block)
            if slide != (0,0):
                self.slide(block, slide)
            return True
        # Did not collide. Mark prev position empty & mark to fill with black
        self.tm.matrix[block.position[0], block.position[1]] = -1
        if self.tm.game.spaces_to_clear.add_pos(block.position):
            block.collision_detection = False   # went out of bounds. Could just draw a square around map to avoid this
            self.tm.inactive_blocks.add(block)
            self.tm.blocks.remove(block)
            block.grounded_timer = 9999
        block.position = next_pos
        self.tm.matrix[block.position[0], block.position[1]] = block.id  # OCCUPIED
        return False


    def get_step_velocity(self, total_x: int, total_y: int) -> (int, int):
        # returns a position based on velocity, trimmed down to -1 to +1 in any direction
        x = total_x
        y = total_y
        if x < 0:
            x = -1
        elif x > 0:
            x = 1
        if y < 0:
            y = -1
        elif y > 0:
            y = 1
        return int(x), int(y)



    def slide(self, block, slide: (int, int)) -> None:
        block.horiz_velocity = slide[0]  # don't add velocity. Don't need it and it causes issues
        self.tm.matrix[block.position[0], block.position[1]] = -1  # EMPTY
        self.tm.game.spaces_to_clear.add_pos(block.position)  # Slower with more particles updating
        block.position = (block.position[0] + slide[0], block.position[1] + slide[0])
        self.tm.matrix[block.position[0], block.position[1]] = block.id
        return

    # def flow(tm, block: Block, flow: (int, int))-> None:



    def destroy_block(self, block) -> None:
        self.tm.matrix[block.position[0], block.position[1]] = -1  # EMPTY
        self.tm.game.spaces_to_clear.add_pos(block.position)
        # Now check all spaces around this block for ungroundable blocks. Note this will be called for all
        # blocks in the destruction zone
        self.trigger_ungrounding(block)



    #TODO: There may be more finetuning to reduce checks on same positions
    def trigger_ungrounding(self, block) -> None:
        # Ungrounding should start from the lowest block so don't bother checking y > 0
        for x in range(-1, 2):
            for y in range(-1, 1):  # Updated from 2. Theoretically shouldn't need to check down
                pos = (block.position[0] + x, block.position[1] + y)
                # add the position to the set to check if there's an ungroundable block at end of sequence
                if pos not in self.tm.current_unground_chain_checks:  # did we check it already this chain?
                    self.tm.unground_pos_checks.add(pos)
                self.tm.current_unground_chain_checks.add(pos)


    def end_frame_unground(self) -> None:
        unground_frame_blocks = self.get_unground_blocks()
        if not unground_frame_blocks:
            self.tm.current_unground_chain_checks.clear()  # Flush set, chain is complete.
            # tm.unground_count = 0
            return
        next_frame_ungrounds = set()
        for block in unground_frame_blocks:
            block.grounded_timer = 0
            self.tm.blocks.add(block)
            if block in self.tm.inactive_blocks:
                self.tm.inactive_blocks.remove(block)
            next_frame_ungrounds.add(block)
        # if len(unground_frame_blocks) > 0:
        #     print(f'unground this frame block count: {len(unground_frame_blocks)}')
        for block in next_frame_ungrounds:  # now add the blocks to check next frame
            self.trigger_ungrounding(block)
        # if tm.unground_count != 0:  # now only checking each block 1x
        #     print(f'unground count: {tm.unground_count}')


    #TODO: A block becomes ungrounded. Then grounded. Then another one next to it turns it back to ungrounded.#
    # Does this happen, and if so do I want it to happen?
    def get_unground_blocks(self):
        if len(self.tm.unground_pos_checks) == 0:
            return None
        unground_blocks = set()
        for pos in self.tm.unground_pos_checks:
            # tm.unground_count += 1
            block_id = self.tm.matrix[(pos)]
            if block_id == -1:
                continue
            block = self.tm.all_blocks[block_id]
            # print(f'pos to CHECK {pos}.    Block id = {tm.matrix.get_val(pos)}')
            if not block.type.rigid and not block.collision_detection:
                block.collision_detection = True
                unground_blocks.add(block)
        self.tm.unground_pos_checks.clear()
        return unground_blocks



    # Quadtree structure used for destroyable particles only, to find particles within destroy radius
    def initialize_quadtree(self) :
        if self.tm.quadtree.initialized:
            return self.tm.quadtree.all_quads, False
        else:
            insert_blocks = {b for b in self.tm.blocks if b.type.destroyable}  # only insert destroyable blocks
            print(f'quadtree particle insert count: {len(insert_blocks)}')
            # as blocks are always active upon load, then switch to inactive.
            return self.tm.quadtree.create_tree(insert_blocks), True

    def insert_object_quadtree(tm, obj, x: int, y: int) :  # use to put specific position in tree
        return tm.quadtree.insert_object(obj=obj, x=x, y=y, start_node=tm.quadtree.root_node)
        # now can access node.children to get neighboring objects
