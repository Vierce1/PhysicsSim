# import Blocks.block_type as block_type
# from Blocks.block_type import *
import Blocks.block_type
import physics
# import Blocks.block as block
from Blocks import block
from quadtree import Quadtree  #, QuadtreeElement
import pygame as pg
import math

class Terrain_Manager:
    def __init__(self, screen_width: int, screen_height: int):
        self.all_nodes = []
        self.node_count = 1  # for root node
        self.blocks = []
        self.block_rects = []
        # 2d array representing the spatials organization of the quadtrees. Used to quickly assess block location
        # self.tree_org = []
        # New idea: first block that builds quadtree nieghbors sends the list here
        # self.q_neighbors = dict()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.max_branches = 6
        self.capacity = 16
        physics.terrain_manager = self
        self.root_quadtree = Quadtree(id=0, x=0, y=0 + self.screen_height,
                                 width=self.screen_width, height=self.screen_height,
                                 branch_count=0)
        self.all_nodes.append(self.root_quadtree)


    def assign_block_indices(self):  # need new method for adding blocks after init
        [b.set_index(self.blocks.index(b)) for b in self.blocks]
        # for i in range(len(self.blocks)):
        #     self.blocks[i].set_index = i



#TODO: Instead of quadtrees keeping track of their neighbors, blocks that cross multiple quadtrees can
# give themselves to both leaves, so they are detected in collisions for either leaf
# this will be lower cost since many fewer blocks in collision detection

    def update(self, screen) -> list:
        # self.all_nodes.clear()
        # self.node_count = 1
        [q.objects.clear() for q in self.all_nodes]  # clear all objects
        [self.insert_blocks(block, self.root_quadtree) for block in self.blocks]

        for block in self.blocks:
            block.update(screen=screen)

        self.cleanup_tree()
        print(f'{len(self.all_nodes)} all quads')
        return self.all_nodes


    def cleanup_tree(self):
        # to_process = [self.all_nodes[0]]
        to_process = [n for n in self.all_nodes if len(n.objects) > 0]
        for n in to_process:
            del n
        # while len(to_process) > 0:
        #     node = to_process.pop(-1)  # take the last entry & remove it
        #     # iterate through children
        #     # print(f'processing index {node_index}')
        #     empty_leaf_count = 0
        #     for i in range(4):
        #         child_node = node.children[i]
        #         # child_node = self.all_nodes[child_index]
        #         # print(f'processing child index {child_index}')
        #         if len(child_node.objects) == 0:  # need to remove objects from node as they leave
        #             empty_leaf_count += 1
        #         # elif len(child_node.children > 0):
        #         #     to_process.append(child_node)
        #
        #     if empty_leaf_count == 4:  # all children empty, deallocate them
        #         print('empty')
        #         self.node_count -= 4
        #         [self.all_nodes.remove(c) for c in node.children]
        #         node.children.clear()
                # for i in range(4):
                #     self.all_nodes.pop(node.children[i])
                #     node.first_child = -1  # make the node a leaf since all children deleted



    def insert_blocks(self, block, root_quadtree):
        # for node in block.leaves:
        #     # self.all_nodes[leaf].objects.remove(block.index)
        #     node.objects = [o for o in node.objects if o != block.index]
        block.leaves = []
        # for
        # [quadtree]
        # block.quadtrees = []
        # leaf = self.find_leaf(block, root_quadtree)
        self.find_leaf(block, root_quadtree)
        for leaf in block.leaves:
            self.add_rects_to_quadtree(block, leaf)



    def find_leaf(self, block, quadtree: Quadtree):  # recursively move out toward leaves
        if quadtree.branch_count == self.max_branches: # \
            block.leaves.append(quadtree)
        else:
            children = self.create_branches(quadtree=quadtree, branch_count=quadtree.branch_count,
                                            next_id=self.node_count)
            # determine which child(s) contains the block
            for i in range(4):
                node = quadtree.children[i]
                contained = self.check_block_in_quad(block, node)
                if contained:
                    # return self.find_leaf(block, child)
                    self.find_leaf(block, node)


    def create_branches(self, quadtree: Quadtree, branch_count: int, next_id: int):
        if len(quadtree.children) > 0:
            return quadtree.children  # another block already created the children

        # node children not created yet. Make them.
        # quadtree.first_child = next_id
        for i in range(2):
            for j in range(2):
                child = Quadtree(id=next_id,
                                 x=quadtree.x + j * quadtree.width * 0.5, y=quadtree.y - i * quadtree.height * 0.5,
                                 width=quadtree.width * 0.5, height=quadtree.height * 0.5,
                                 branch_count=branch_count + 1)
                quadtree.children.append(child)
                self.all_nodes.append(child)
                next_id += 1
        self.node_count += 4
        return quadtree.children


    def get_neighbors(self, quadtree):  # Now returns indices of blocks
        # return [element.id for element in quadtree.objects]
        return quadtree.objects


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
        # Single node method:
        # if quadtree.x <= block.rect.centerx <= quadtree.x + quadtree.width \
        #     and quadtree.y >= block.rect.centery >= quadtree.y - quadtree.height:
        #         return True
        else: return False


    def add_rects_to_quadtree(self, block, quadtree):
        # Could just do the block id and not build a new object
        # element = QuadtreeElement(x=block.rect.x, y=block.rect.y, id=block.index)
        quadtree.objects.append(block.index)


    # def get_quadnode_dimensions(self, branch_count):
    #     divisor = 1
    #     if branch_count > 0:
    #         # divisor = math.pow(branch_count + 1, 2) / 2
    #         divisor = (2 ** (branch_count + 1)) / 2
    #
    #     q_width = self.screen_width / divisor
    #     q_height = self.screen_height / divisor
    #     return q_width, q_height