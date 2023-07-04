import pygame as pg

class Quadtree:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.objects = []  # BLOCKS stored inside this cell
        self.north = None
        self.south = None
        self.east = None
        self.west = None
        # self.neighbors = []
        # print(str(self.x) + " .  " + str(self.y))

    def get_neighbors(self) -> list:  # list of blocks.
#TODO  Increasing efficency here should help allow for more quadtrees, therefor better collision detection speeds
#  because we iterate through every collision block & it's quadtrees objects + it's neighbors objects every frame
#  What if I can only iterate through a quadtree once and save its neighbors list?
        # Blocks already have their new tree (if applicable) so build neighbors only for first call on this tree
        # if len(self.neighbors) > 0:  # already built this frame
        #     return self.neighbors
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