import pygame as pg

class Player:
    def __init__(self):
        self.position = (100, 100)


    def get_rect_pos(self, current_pos: (int, int), change: (int, int)):
        self.position = tuple(map(sum, zip(current_pos, change)))
        # print(f'new position = {str(self.position[0])} , {str(self.position[1])}')
        return self.position


    def accept_input(self, events, screen: pg.display):
        pos_change = (0, 0)
        keys = pg.key.get_pressed()
        if keys[pg.K_a]:
            pos_change = (-1, pos_change[1])
        if keys[pg.K_d]:
            pos_change = (1, pos_change[1])
        if keys[pg.K_w]:
            pos_change = (pos_change[0], -1)
        if keys[pg.K_s]:
            pos_change = (pos_change[0], 1)

        player_position = self.get_rect_pos(current_pos=self.position, change=pos_change)
        pg.draw.rect(surface=screen, color=(255, 255, 255), rect=(player_position[0], player_position[1], 10, 10))



# key down example:
        # for event in events:
        #     if event.type == pg.KEYDOWN:
        #         if event.key == pg.K_a:
        #             pos_change = (-1, pos_change[1])