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
        # print(str(self.x) + " .  " + str(self.y))

    def get_neighbors(self) -> list:  # list of blocks
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