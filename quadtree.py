from Blocks.block import Block

class Quadtree_Node:
    __slots__ = ('x', 'y', 'width', 'height', 'objects', 'branch_count', 'children', 'parent', 'count')
    def __init__(self, x: float, y: float, width: float, height: float, branch_count: int):        
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.objects = set()
        self.branch_count = branch_count  # leaf at 6. 2*4^6 = 8192 leaves
        self.children = set()  # 4 quadtree node children upon split
        self.parent = None
        self.count = 0  # total count of contained objects




class Quadtree:
    def __init__(self, world_width: int, world_height: int):
        self.all_quads = set()        
        self.blocks = set()
        self.max_branches = 15
        self.capacity = 60
        self.root_node = Quadtree_Node(x=0, y=0 + world_height,
                                  width=world_width, height=world_height, branch_count=0)
        self.all_quads.add(self.root_node)
        self.initialized = False



    # @profile
    def create_tree(self, blocks: set[Block]) -> set[Quadtree_Node]:
        self.initialized = True
        self.insert_blocks(blocks=blocks)

        return self.all_quads
        
        # print(f'quadtrees size = {size_checker.total_size(self.all_quads, verbose=False)}')
        # print(f'quadtree size: {sys.getsizeof(self.root_quadtree)}')
        # print(f'blocks size: {sys.getsizeof(self.blocks[0])}')
        # print(f'non-grounded block count: {len([b for b in self.blocks if b.collision_detection])}')
        # print(f'leaf=leaf '
        #       f'{[b for b in self.blocks if [l for l in b.leaves if
        #       len([l2 for l2 in b.leaves if l == l2 and b.leaves.index(l) != b.leaves.index(l2)]) > 0]]}')


        # [self.insert_blocks(block, self.root_quadtree) for block in self.blocks]

        # self.cleanup_tree()

        # print(f'total collision detections: {self.total_col_dets}')
        # print(f'{len(self.all_quads)} all quads')
        # for i, q in enumerate(self.all_quads):
        #     if q.count > 0:
        #         print(f'node index {i}    count: {q.count}  branches: {q.branch_count}')

        # return self.all_quads    # return just for drawing visually




#     def cleanup_tree(self):  # remove empty quadtree nodes i/o deleting all of them every frame
#         process_list = [self.root_quadtree]
#         deletions = []
#         while len(process_list) > 0:
#             node = process_list.pop(0)
#             empty_count = 0
#             for child in node.children:
#                 if child.count == 0:
#                     empty_count += 1
#                     deletions.append(child)
#                 elif child.branch_count < self.max_branches:  # Not empty, go down a level to check again
#                     process_list.append(child)
# 
# 
#         root_nodes = set() # 2 children can share same parent node, thus eliminate deleting a root twice
#         for node in deletions:
#             # root_nodes.add(self.get_root_parent_no_count(node))
#             # Purpose of below is so not to delete a child of a node that has a count
#             # we just want to delete the children (recursively) of a node with 0 count
#             # otherwise end up with a node containing 3 children
#             root_nodes.update([child for child in node.children if child.count == 0])
#             node.children.clear()
#         # root_nodes = set(deletions)
#         for root in root_nodes:
#             self.del_children_recursive(root)
    
    # def del_children_recursive(self, root):
    #     for child in root.children:
    #         self.del_children_recursive(child)
    #     self.all_quads.remove(root)



    def insert_blocks(self, blocks: set[Block]):
        # Check if block is still contained in same leaf(s) as last frame
        # change, left_leaves = False, []
        # if block.collision_detection:
        #     change, left_leaves = self.check_remove_leaf(block)
        # if change is True or len(block.leaves) == 0:  # search if no leaves, or changed leaves
        #     root = root_node
        #     if len(left_leaves) > 0:
        #         root = self.get_common_root(left_leaves)
        for block in blocks:
            self.add_rects_to_node(block, self.root_node)



    # def check_remove_leaf(self, block) -> (bool, list[Quadtree_Node]):
    #     change = False
    #     left_leaves = []  # we will start searching for a new leaf from this list's common root
    #     for leaf in block.leaves:
    #         # this check happens large number of times.
    #         # Reducing would help.
    #         contained = self.check_block_in_quad(block=block, quadtree=leaf)
    #         if contained == -1:
    #             # block completely outside leaf
    #             leaf.objects.remove(block)
    #             block.leaves.remove(leaf)
    #             self.set_count_tree(quadtree=leaf, value=-1)
    #             change = True
    #             left_leaves.append(leaf)
    #         elif contained == 0:  # on the edge of the leaf. Process change but don't remove it
    #             change = True
    #     return change, left_leaves


    # def get_common_root(self, leaves: list[Quadtree]):
    #     # Need to take branch count into effect. First eval'd parent should be the lowest branch count shared
    #     if self.root_quadtree in leaves:
    #         return leaves[0]
    #     leaves = self.match_branches(leaves)
    #     parents = [leaf.parent for leaf in leaves]
    #     if self.root_quadtree == parents[0]:
    #         return self.root_quadtree
    # 
    #     for i in range(1, len(parents)):
    #         if parents[i] != parents[0]:
    #             return self.get_common_root(parents)
    #     # no mismatches. Found the common root
    #     return parents[0]
    # 
    # def match_branches(self, leaves: list[Quadtree]):
    #     biggest_branch = max(leaf.branch_count for leaf in leaves)
    #     for leaf in leaves:
    #         while leaf.branch_count > biggest_branch:
    #             leaf = leaf.parent
    #     return leaves



    # @profile
    def create_branches(self, node: Quadtree_Node):
        if len(node.children) > 0:
            return node.children  # another block already created the children

        # node children not created yet. Make them.
        for i in range(2):
            for j in range(2):
                child = Quadtree_Node(x=node.x + j * node.width * 0.5, y=node.y - i * node.height * 0.5,
                                 width=node.width * 0.5, height=node.height * 0.5,
                                 branch_count=node.branch_count + 1)
                child.parent = node
                node.children.add(child)                
                self.all_quads.add(child)
        return node.children

    
    def get_neighbors(self, block, quadtree): 
        all_neighbors = {obj for obj in quadtree.objects if obj != block}
        return all_neighbors
        # all_neighbors =[]
        # all_neighbors.extend(quadtree.objects)
        # if block in all_neighbors:
        #     all_neighbors.remove(block)
        # all_neighbors = [b for b in quadtree.objects if b != block] # SLower
        # return all_neighbors
        # close_neighbors = self.exclude_blocks_z_address(block, all_neighbors)
        # close_neighbors = self.exclude_blocks_limit(block, all_neighbors)
        # print(f'all neighbors: {len(all_neighbors)}')
        # print(f'    close neighbors: {len(close_neighbors)}')
        # print('\n')
        # return close_neighbors


    # def assign_z_addresses(self):
    #     for block in self.blocks:
    #         block.z_address = pymorton.interleave2(round(block.rect.x), round(block.rect.y))
    #     # now sort them. When inserting into quadtree leaves, they should remain sorted.
    #     self.blocks = sorted(self.blocks, key=lambda x: x.z_address)  # slower 1 fps
    # 
    # 
    # 
    # def exclude_blocks_limit(self, block, others: list):
    #     min_x, min_y = block.rect.x - self.max_collision_dist, block.rect.y - self.max_collision_dist
    #     max_x, max_y = block.rect.x + self.max_collision_dist, block.rect.y + self.max_collision_dist
    #     neighbors = []
    #     for b in others:  # can't sort unless you put them in 1d
    #         if min_x < b.rect.x < max_x and min_y < b.rect.y < max_y:
    #             neighbors.append(b)
    #     return neighbors


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



    def check_block_in_quad(self, block, node) -> bool: 
        # Updated to have a buffer. Blocks added to multiple quadtree nodes if they are close to the border
        # This allows inter-leaf collision
        right = block.position[0] + block.type.width + (1 * block.type.width)
        # left = block.rect.left - (1 * block.type.width)
        top = block.position[1] - block.type.height + (1 * block.type.height)
        # bottom = block.rect.bottom - (1 * block.rect.height)

        #TODO: Vett this formula
        top_dist = node.y - (block.position[1] - block.type.height + block.type.height)

        if node.y >= top >= (node.y - node.height - block.type.height) \
          and node.x <= right <= node.x + node.width:
                # and (right >= quadtree.x and left <= quadtree.x + quadtree.width):
            # if top_dist < block.type.height:  # in multiple leaves vertically
            #     return 0
            return True
        return False


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





    def add_rects_to_node(self, block, node: Quadtree_Node):
        # first check if the node is already split
        if len(node.children) > 0:
            for child in node.children:
                contained = self.check_block_in_quad(block, child)
                if contained:
                    self.add_rects_to_node(block, child)

        # reached a leaf. proceed
        # check if reached capacity. If so, split and shuffle blocks to children
        elif node.count >= self.capacity and node.branch_count < self.max_branches:
            # split
            children = self.create_branches(node)
            objs = []
            objs.extend(node.objects)
            node.objects.clear()
            for b in objs:
                self.set_count_tree(branch=node, value=-1)  # decrement count, will increment it below
                # b.leaves.remove(node)

                for child in children:
                    contained = self.check_block_in_quad(b, child)
                    if contained:
                        self.add_rects_to_node(b, child)
                        # self.set_count_tree(child, 1) # No need, count will be added when we hit a leaf

            for child in children:  # check if original block is in each child
                contained = self.check_block_in_quad(block, child)
                if contained:
                    self.add_rects_to_node(block, child)
        elif block not in node.objects:  # found leaf w/ under capacity or max branches
            node.objects.add(block)
            self.set_count_tree(branch=node, value=1)
            # block.leaves.append(node)


    def set_count_tree(self, branch: Quadtree_Node, value: int):
        branch.count += value
        node = branch
        while node.parent is not None:
            node.parent.count += value
            node = node.parent
