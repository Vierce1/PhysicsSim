import pygame as pg

class Quadtree:
    def __init__(self, x: int, y: int, width: int, height: int, branch_count: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.objects = []  # BLOCKS stored inside this cell
        self.branch_count = branch_count  # leaf at 6. 2*4^6 = 8192 leaves
        self.children = []  # 4 quadtree node children upon split


    def create_branches(self, branch_count: int):
        if len(self.children) > 0:
            return self.children  # another block already created the children
        for i in range(2):
            for j in range(2):
                child = Quadtree(x=self.x + j * self.width * 0.5, y=self.y - i * self.height * 0.5,
                                 width=self.width * 0.5, height=self.height * 0.5,
                                 branch_count=branch_count + 1)
                self.children.append(child)
        return self.children




    def get_neighbors(self) -> list:  # list of blocks.
        return self.objects
        # neighbors = []
        # if self.north:
        #     neighbors.extend(self.north.objects)
        # if self.south:
        #     neighbors.extend(self.south.objects)
        # if self.east:
        #     neighbors.extend(self.east.objects)
        # if self.west:
        #     neighbors.extend(self.west.objects)
        # neighbors.extend(self.objects)
        # return neighbors