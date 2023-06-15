import pygame as pg
from player import Player



pg.init()
screen = pg.display.set_mode([1920, 1080])
player = Player()

game_running = True
while game_running:
    events = pg.event.get()
    for event in events:
        if event.type == pg.QUIT:
            game_running = False

    # fill screen with black
    screen.fill((0, 0, 0))

    # player movement
    player.accept_input(events=events, screen=screen)

    pg.display.flip()  # updates the display. Could use display.update() and pass in PARTS of the screen to update

pg.quit()



