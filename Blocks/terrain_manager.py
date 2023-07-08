# import Blocks.block_type as block_type
# from Blocks.block_type import *
import Blocks.block_type
import physics
# import Blocks.block as block
from Blocks import block
from quadtree import Quadtree  #, QuadtreeElement
import pygame as pg
import math
import physics

class Terrain_Manager:
    def __init__(self, screen_width: int, screen_height: int):
        self.all_quads = set()
        self.node_count = 1  # for root node
        self.blocks = []
        self.block_rects = []
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.max_branches = 7
        self.capacity = 20
        self.root_quadtree = Quadtree(x=0, y=0 + self.screen_height,
                                 width=self.screen_width, height=self.screen_height, branch_count=0)
        self.all_quads.add(self.root_quadtree)
        physics.t_m = self
        self.total_col_dets = 0


    def assign_block_indices(self):  # need new method for adding blocks after init
        [self.set_index(block=b, index=self.blocks.index(b)) for b in self.blocks]
    def set_index(self, block, index: int):
        block.id = index



    def update(self, screen) -> list:
        self.total_col_dets = 0
        [self.insert_blocks(block, self.root_quadtree) for block in self.blocks]

        for block in self.blocks:
            physics.update(block=block, screen=screen)

        self.cleanup_tree()
        print(f'total collision detections: {self.total_col_dets}')
        # print(f'{len(self.all_quads)} all quads')
        # for i, q in enumerate(self.all_quads):
        #     if q.count > 0:
        #         print(f'node index {i}    count: {q.count}  branches: {q.branch_count}')

        return self.all_quads    # return just for drawing visually


#TODO: Counts are wrong (shows more than the 25 i spawned in some nodes, root node does not equal 25)
# And cleanup tree removes nodes that should not be removed

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
            root_nodes.add(self.get_root_parent_no_count(node))
        for root in root_nodes:
            self.del_children_recursive(root)



    def get_root_parent_no_count(self, node):
        eval_node = node
        while eval_node.parent and eval_node.parent.count == 0 and eval_node.parent.parent is not None:
            eval_node = eval_node.parent
        return eval_node  # found the node just under the parent node that has a count > 0

    def del_children_recursive(self, root):
        for child in root.children:
            self.del_children_recursive(child)
        try:
            self.all_quads.remove(root)
        except:
            # print("fail")
            pass



#TODO: Now collision detection is very efficient, but creating nodes every frame slow
# Need a way to skip this for grounded blocks.
# For grounded blocks can I cache the position of their quadtree and then add them in after the other blocks finish?
    def insert_blocks(self, block, root_quadtree):
        # Check if block is still contained in same leaf(s) as last frame
        block.leaves = self.check_remove_leaf(block)  # will either be blank (if no same leaves contain) or not
        self.add_rects_to_quadtree(block, root_quadtree)


    def check_remove_leaf(self, block) -> list:
        leaves = []
        for leaf in block.leaves:
            contained = self.check_block_in_quad(block=block, quadtree=leaf)
            if not contained:
                leaf.objects.remove(block.id)
                self.set_count_tree(quadtree=leaf, value=-1)

            else:
                leaves.append(leaf)
        return leaves


    def find_leaf(self, block, quadtree):  # recursively move out toward leaves
        if quadtree in block.leaves:  # block already has reference to this leaf
            # if not block.id in quadtree.objects:  # need this?
            #     quadtree.objects.append(block.id)
            return
#TODO: this needs to run through the quadtree's capactiy check every time we add a block to
# take care of prev. added blocks when overflow capacity
        # elif quadtree.branch_count == self.max_branches or quadtree.count <= self.capacity:
        block.leaves.append(quadtree)
        # else:
        #     children = self.create_branches(quadtree)
        #     # determine which child contains the block
        #     for child in children:
        #         contained = self.check_block_in_quad(block, child)
        #         if contained:
        #             self.find_leaf(block, child)



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
                self.all_quads.add(child)
        return quadtree.children


    def get_neighbors(self, quadtree):  # Now returns indices of blocks
        return [self.blocks[id] for id in quadtree.objects]
        # return quadtree.objects


    def check_block_in_quad(self, block, quadtree) -> bool:
        # Updated to have a buffer. Blocks added to multiple quadtree nodes if they are close to the border
        # FPS hit, but better than quadtrees keeping track of their neighbors
        right = block.rect.right + (1 * block.rect.width)
        left = block.rect.left - (1 * block.rect.width)
        top = block.rect.top + (1 * block.rect.height)
        bottom = block.rect.bottom - (1 * block.rect.height)

        # q_width, q_height = self.get_quadnode_dimensions(quadtree.branch_count)
        if (right >= quadtree.x and left <= quadtree.x + quadtree.width) \
            and (bottom <= quadtree.y and top >= quadtree.y - quadtree.height):
                return True
        else: return False




# TODO:  Don't i need to add the block to the node BEFORE checking capacity? Otherwise the block will not
# be added to the quad ever
    def add_rects_to_quadtree(self, block, quadtree: Quadtree):
        # first check if the node is already split
        for child in quadtree.children:
            contained = self.check_block_in_quad(block, child)
            if contained:
                # self.find_leaf(block, child)
                # self.blocks[block_id].leaves.append(child)
                # child.count += 1
                self.add_rects_to_quadtree(block, child)
                # self.set_count_tree(child, 1)

        # reached a leaf. proceed

        # check if reached capacity. If so, split and shuffle blocks to children
        if quadtree.count >= self.capacity and quadtree.branch_count < self.max_branches:
            # split
            children = self.create_branches(quadtree)
#TODO: Slowdown and errors in this function below:
            for block_id in quadtree.objects:
                quadtree.objects.remove(block_id)
                self.set_count_tree(quadtree, -1)  # decrement count, will increment it below
                # try:
                self.blocks[block_id].leaves.remove(quadtree)
                # except: pass
                for child in children:
                    contained = self.check_block_in_quad(self.blocks[block_id], child)
                    if contained:
                        # self.find_leaf(block, child)
                        # self.blocks[block_id].leaves.append(child)
                        # child.count += 1
                        self.add_rects_to_quadtree(block, child)
                        # self.set_count_tree(child, 1) # No need, count will be added when we hit a leaf

        else:  # found leaf w/ under capacity or max branches
            # print(f'{quadtree.count}   {quadtree.branch_count}')
            id = block.id
            if id not in quadtree.objects:
                quadtree.objects.append(id)
                self.set_count_tree(quadtree=quadtree, value=1)
                block.leaves.append(quadtree)


    def set_count_tree(self, quadtree: Quadtree, value: int):
        quadtree.count += value
        node = quadtree
        while node.parent is not None:
            node.parent.count += value
            node = node.parent


    # def get_quadnode_dimensions(self, branch_count):
    #     divisor = 1
    #     if branch_count > 0:
    #         # divisor = math.pow(branch_count + 1, 2) / 2
    #         divisor = (2 ** (branch_count + 1)) / 2
    #
    #     q_width = self.screen_width / divisor
    #     q_height = self.screen_height / divisor
    #     return q_width, q_height