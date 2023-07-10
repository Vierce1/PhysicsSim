class Quadtree:
    def __init__(self, x: int, y: int, width: int, height: int, branch_count: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.objects =  []  # indices of blocks stored inside this cell
        self.branch_count = branch_count  # leaf at 6. 2*4^6 = 8192 leaves
        self.children = []  # 4 quadtree node children upon split
        self.parent = None
        self.count = 0  # total count of contained objects



# # # Could use this if need to keep track of x/y of the agent contained
# class QuadtreeElement:  # a block or whatever stored inside a leaf
#     def __init__(self, x: int, y: int, id: int):
#         self.x = x
#         self.y = y
#         self.id = id  # the id of the block in terrain_manager.blocks