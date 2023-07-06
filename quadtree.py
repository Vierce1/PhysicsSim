import pygame as pg

class Quadtree:
    def __init__(self, x: int, y: int, width: int, height: int, branch_count: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.objects = []  # BLOCKS stored inside this cell
        self.north = None
        self.south = None
        self.east = None
        self.west = None
        self.branch_count = branch_count  # leaf at 4. 2*4^4 = 512 leaves
        self.neighbors = []
        self.children = []  # 4 quad children


    def create_branches(self, branch_count: int):
        for i in range(2):
            for j in range(2):
                child = Quadtree(x=self.x + j * self.width * 0.5, y=self.y - i * self.height * 0.5,
                                 width=self.width * 0.5, height=self.height * 0.5,
                                 branch_count=branch_count + 1)
                self.children.append(child)



    def get_neighbors(self) -> list:  # list of blocks.
        neighbors = []
        if self.north:
            neighbors.extend(self.north.objects)
        if self.south:
            neighbors.extend(self.south.objects)
        if self.east:
            neighbors.extend(self.east.objects)
        if self.west:
            neighbors.extend(self.west.objects)
        neighbors.extend(self.objects)
        return neighbors