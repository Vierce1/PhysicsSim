class Quadtree:
    def __init__(self, id: int, x: int, y: int,
                 width: int, height: int,
                 branch_count: int):
        self.id = id
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.objects = []  # indices of QuadtreeElements stored inside this leaf (if it is a leaf)
        self.branch_count = branch_count  # leaf at 6. 2*4^6 = 8192 leaves
        self.first_child = -1  # index of the first child node




# Could use this if need to keep track of x/y of the agent contained
# class QuadtreeElement:  # a block or whatever stored inside a leaf
#     def __init__(self, x: int, y: int, id: int):
#         self.x = x
#         self.y = y
#         self.id = id  # the id of the block in terrain_manager.blocks