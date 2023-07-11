# import Blocks.block_type as block_type
# from Blocks.block_type import *
import Blocks.block_type
import physics
import pymorton
# import Blocks.block as block
from Blocks import block
from quadtree import Quadtree  #, QuadtreeElement
import pygame as pg
import math
import physics
from pymorton import *
import sys
import size_checker


class Terrain_Manager:
    def __init__(self, screen_width: int, screen_height: int):
        self.all_quads = []# set()
        self.node_count = 1  # for root node
        self.blocks = []
        self.block_rects = []
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.max_branches = 9
        self.capacity = 35
        self.root_quadtree = Quadtree(x=0, y=0 + self.screen_height,
                                 width=self.screen_width, height=self.screen_height, branch_count=0)
        self.all_quads.append(self.root_quadtree)  #add(self.root_quadtree)
        physics.t_m = self
        self.max_collision_dist = 0 # should be about 1.5x diameter of block
        self.total_col_dets = 0
        self.render_image = None
        # print(f'block size: {sys.getsizeof(Blocks.block.Block)}')




    def setup(self, render_image):  # need new method for adding blocks after init
        [self.set_index(block=b, index=self.blocks.index(b)) for b in self.blocks]
        self.max_collision_dist = 2 * self.blocks[0].rect.width
        self.render_image = render_image


    def set_index(self, block, index: int):
        block.id = index



    # @profile
    def update(self, screen) -> list:
        # self.total_col_dets = 0

        # print(f'quadtrees size = {size_checker.total_size(self.all_quads, verbose=False)}')
        # print(f'quadtree size: {sys.getsizeof(self.root_quadtree)}')
        # print(f'blocks size: {sys.getsizeof(self.blocks)}')
        # print(f'non-grounded block count: {len([b for b in self.blocks if b.collision_detection])}')
        # print(f'leaf=leaf '
        #       f'{[b for b in self.blocks if [l for l in b.leaves if
        #       len([l2 for l2 in b.leaves if l == l2 and b.leaves.index(l) != b.leaves.index(l2)]) > 0]]}')

        # self.assign_z_addresses()
        [self.insert_blocks(block, self.root_quadtree) for block in self.blocks]

        # [self.assign_z_addresses(b) for b in self.blocks]
        for block in self.blocks:
            physics.update(block=block, screen=self.render_image)

        self.cleanup_tree()

        # print(f'total collision detections: {self.total_col_dets}')
        # print(f'{len(self.all_quads)} all quads')
        # for i, q in enumerate(self.all_quads):
        #     if q.count > 0:
        #         print(f'node index {i}    count: {q.count}  branches: {q.branch_count}')

        return self.all_quads    # return just for drawing visually


#TODO: Counts are wrong (shows more than the 25 i spawned in some nodes, root node does not equal 25)
# And cleanup tree removes nodes that should not be removed

    # @profile  # Very low memory usage
    def cleanup_tree(self):  # remove empty quadtree nodes i/o deleting all of them every frame
        process_list = [self.root_quadtree]
        deletions = []
        while len(process_list) > 0:
            node = process_list.pop(0)
            empty_count = 0
            for child in node.children:
                if child.count == 0:
                    empty_count += 1
                    deletions.append(child)
                elif child.branch_count < self.max_branches:  # Not empty, go down a level to check again
                    process_list.append(child)


        root_nodes = set() # 2 children can share same parent node, thus eliminate deleting a root twice
        for node in deletions:
            # root_nodes.add(self.get_root_parent_no_count(node))
            # Purpose of below is so not to delete a child of a node that has a count
            # we just want to delete the children (recursively) of a node with 0 count
            # otherwise end up with a node containing 3 children
            root_nodes.update([child for child in node.children if child.count == 0])
            node.children.clear()
        # root_nodes = set(deletions)
        for root in root_nodes:
            self.del_children_recursive(root)



#DON"T THINK I NEED THIS. I work from the root down. Should stop on the first empty node containing all empty children
    # def get_root_parent_no_count(self, node):
    #     eval_node = node
    #     while eval_node.parent and eval_node.parent.count == 0 and eval_node.parent.parent is not None:
    #         eval_node = eval_node.parent
    #     return eval_node  # found the node just under the parent node that has a count > 0

    # @profile  # Low memory usage
    def del_children_recursive(self, root):
        for child in root.children:
            self.del_children_recursive(child)
        self.all_quads.remove(root)



#TODO: Major memory usage functions:
    # get_neighbors, check_down_collisions, check_block_in_quad (called from check_remove_leaf)



#TODO: For grounded blocks can I cache position of their quadtree and then add them in after the other blocks finish?

    # @profile
    def insert_blocks(self, block, root_quadtree):
        # Check if block is still contained in same leaf(s) as last frame
        change, left_leaves = self.check_remove_leaf(block)
        if change is True or len(block.leaves) == 0:  # search if no leaves, or changed leaves
            root = self.get_common_root(left_leaves) if len(left_leaves) > 0 else root_quadtree
            self.add_rects_to_quadtree(block, root)


    # @profile
    def check_remove_leaf(self, block) -> (bool, list[Quadtree]):
        if not block.collision_detection:
            return False, []  # block is grounded. If block has not been added to any leaves yet it will still proces
        change = False
        left_leaves = []  # we will start searching for a new leaf from this list's common root
        for leaf in block.leaves:
            # this check happens large number of times.
            # Reducing would help.
            contained = self.check_block_in_quad(block=block, quadtree=leaf)
            if contained == -1:
                # block completely outside leaf
                leaf.objects.remove(block)
                block.leaves.remove(leaf)
                self.set_count_tree(quadtree=leaf, value=-1)
                change = True
                left_leaves.append(leaf)
            elif contained == 0:  # on the edge of the leaf. Process change but don't remove it
                change = True
        return change, left_leaves


    def get_common_root(self, leaves: list[Quadtree]):
        # Need to take branch count into effect. First eval'd parent should be the lowest branch count shared
        leaves = self.match_branches(leaves)
        parents = [leaf.parent for leaf in leaves]
        if self.root_quadtree == parents[0]:
            return self.root_quadtree

        for i in range(1, len(parents)):
            if parents[i] != parents[0]:
                return self.get_common_root(parents)
        # no mismatches. Found the common root
        # print(f'{parents[0].x}  {parents[0].y}')
        return parents[0]

    def match_branches(self, leaves: list[Quadtree]):
        biggest_branch = max(leaf.branch_count for leaf in leaves)
        for leaf in leaves:
            while leaf.branch_count > biggest_branch:
                if not leaf.parent:
                    leaves[0] = self.root_quadtree
                    return leaves
                leaf = leaf.parent
        return leaves



    # @profile
    def create_branches(self, quadtree: Quadtree):
        if len(quadtree.children) > 0:
            return quadtree.children  # another block already created the children

        # node children not created yet. Make them.
        for i in range(2):
            for j in range(2):
                child = Quadtree(x=quadtree.x + j * quadtree.width * 0.5, y=quadtree.y - i * quadtree.height * 0.5,
                                 width=quadtree.width * 0.5, height=quadtree.height * 0.5,
                                 branch_count=quadtree.branch_count + 1)
                child.parent = quadtree
                quadtree.children.append(child)
                # self.all_quads.add(child)
                self.all_quads.append(child)
        return quadtree.children


    # @profile  # large memory cost Every non-grounded block calls this every frame
    def get_neighbors(self, block, quadtree):  # Now returns indices of blocks
        # all_neighbors = [self.blocks[id] for id in quadtree.objects if id != block.id]
        all_neighbors =[]
        all_neighbors.extend(quadtree.objects)
        if block in all_neighbors:
            all_neighbors.remove(block)
        # all_neighbors = [b for b in quadtree.objects if b != block] # SLower
        # return all_neighbors
        # close_neighbors = self.exclude_blocks_z_address(block, all_neighbors)
        close_neighbors = self.exclude_blocks_limit(block, all_neighbors)
        # print(f'all neighbors: {len(all_neighbors)}')
        # print(f'    close neighbors: {len(close_neighbors)}')
        # print('\n')
        return close_neighbors


    def assign_z_addresses(self):
        for block in self.blocks:
            block.z_address = pymorton.interleave2(round(block.rect.x), round(block.rect.y))
        # now sort them. When inserting into quadtree leaves, they should remain sorted.
        self.blocks = sorted(self.blocks, key=lambda x: x.z_address)  # slower 1 fps



    def exclude_blocks_limit(self, block, others: list):
        min_x, min_y = block.rect.x - self.max_collision_dist, block.rect.y - self.max_collision_dist
        max_x, max_y = block.rect.x + self.max_collision_dist, block.rect.y + self.max_collision_dist
        neighbors = []
        for b in others:  # can't sort unless you put them in 1d
            if min_x < b.rect.x < max_x and min_y < b.rect.y < max_y:
                neighbors.append(b)
        return neighbors





    # @profile
    # def exclude_blocks_z_address(self, block, otherblocks: list):
    #     min = pymorton.interleave2(round(block.rect.x) - round(self.max_collision_dist),
    #                                round(block.rect.y) - round(self.max_collision_dist))
    #     max = pymorton.interleave2(round(block.rect.x) + round(self.max_collision_dist),
    #                                      round(block.rect.y) + round(self.max_collision_dist))
    #     neighbors = []
    #     for b in otherblocks:
    #         if min < b.z_address < max:
    #             neighbors.append(b)
    #         elif b.z_address >= max:
    #             break
    #     return neighbors



    # @profile  # Massive memory consumption because it is called many times (from check_remove_leaf)
    def check_block_in_quad(self, block, quadtree) -> int: # return: outside=-1 , inside=1, on_edge=0
        # Updated to have a buffer. Blocks added to multiple quadtree nodes if they are close to the border
        # This allows inter-leaf collision
        right = block.rect.right + (1 * block.rect.width)
        left = block.rect.left - (1 * block.rect.width)
        top = block.rect.top + (1 * block.rect.height)
        # bottom = block.rect.bottom - (1 * block.rect.height)

        top_dist = quadtree.y - (block.rect.top + block.rect.height)

        if quadtree.y >= top >= (quadtree.y - quadtree.height - block.rect.height) \
                and quadtree.x <= right <= quadtree.x + quadtree.width:
                # and (right >= quadtree.x and left <= quadtree.x + quadtree.width):
            if top_dist < block.rect.height:  # in multiple leaves
                return 0
            return 1
        return -1


        # if quadtree.y >= top >= (quadtree.y - quadtree.height - block.rect.height) \
        #         and (right >= quadtree.x and left <= quadtree.x + quadtree.width):
        #     return True
        # return False  # Slightly slower
        #
        # # q_width, q_height = self.get_quadnode_dimensions(quadtree.branch_count)
        # # horiz = right - quadtree.x
        # if (right >= quadtree.x and left <= quadtree.x + quadtree.width) \
        #     and (bottom <= quadtree.y and top >= quadtree.y - quadtree.height):
        #         return True
        # else: return False





    def add_rects_to_quadtree(self, block, quadtree: Quadtree):
        # first check if the node is already split
        if len(quadtree.children) > 0:
            for child in quadtree.children:
                contained = self.check_block_in_quad(block, child)
                if contained != -1:
                    self.add_rects_to_quadtree(block, child)

        # reached a leaf. proceed
        # check if reached capacity. If so, split and shuffle blocks to children
        elif quadtree.count >= self.capacity and quadtree.branch_count < self.max_branches:
            # split
            children = self.create_branches(quadtree)
            objs = []
            objs.extend(quadtree.objects)
            quadtree.objects.clear()
            for b in objs:
                self.set_count_tree(quadtree=quadtree, value=-1)  # decrement count, will increment it below
                b.leaves.remove(quadtree)

                for child in children:
                    contained = self.check_block_in_quad(b, child)
                    if contained != -1:
                        self.add_rects_to_quadtree(b, child)
                        # self.set_count_tree(child, 1) # No need, count will be added when we hit a leaf

            for child in children:  # check if original block is in each child
                contained = self.check_block_in_quad(block, child)
                if contained != -1:
                    self.add_rects_to_quadtree(block, child)
        elif block not in quadtree.objects:  # found leaf w/ under capacity or max branches
            quadtree.objects.append(block)
            self.set_count_tree(quadtree=quadtree, value=1)
            block.leaves.append(quadtree)


    def set_count_tree(self, quadtree: Quadtree, value: int):
        quadtree.count += value
        node = quadtree
        while node.parent is not None:
            # print(f'adding {value} to node index {self.all_quads.index(quadtree)}')
            node.parent.count += value
            node = node.parent

# Alternate method: Quadtree branches don't store their positions, calc on the fly. FPS drop
    # def get_quadnode_dimensions(self, branch_count):
    #     divisor = 1
    #     if branch_count > 0:
    #         # divisor = math.pow(branch_count + 1, 2) / 2
    #         divisor = (2 ** (branch_count + 1)) / 2
    #
    #     q_width = self.screen_width / divisor
    #     q_height = self.screen_height / divisor
    #     return q_width, q_height