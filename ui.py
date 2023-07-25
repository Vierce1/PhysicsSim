import pygame as pg
from Blocks.block_type import *


class User_Interface:
    def __init__(self, particle_button_types: [], game):
        self.particle_buttons = []
        self.game = game
        for i in range(len(particle_button_types)):
            width, height = 100, 40
            button = Particle_Button(block_type=particle_button_types[i], x=i * round(width * 1.2), y=20,
                                            width=width, height=height, ui=self)
            self.particle_buttons.append(button)

    def render_buttons(self, screen: pg.Surface):
        for button in self.particle_buttons:
            # Blit the text surface onto the button surface
            mouse_pos = self.game.get_mouse_pos(scale_for_render=False)
            if button.rect.collidepoint(mouse_pos):
                if pg.mouse.get_pressed(num_buttons=3)[0]:
                    button.surface.fill(button.colors['pressed'])
                    if not button.already_pressed:
                        button.pressed = True
                        button.on_click()
                else:
                    button.surface.fill(button.colors['hover'])
            else:
                button.surface.fill(button.colors['normal'])

            button.surface.blit(button.text_surface, [button.rect.width / 2 - button.text_surface.get_rect().width / 2,
                                                  button.rect.height / 2 - button.text_surface.get_rect().height / 2])
            screen.blit(button.surface, button.rect)


    def on_click(self, button, particle_type: int):
        if button.already_pressed:
            return
        print(f'Changing Particle type = {particle_type}')
        [b.set_pressed() for b in self.particle_buttons]
        button.already_pressed = True
        self.game.particle_spawner.particle_type = particle_type


    def check_if_button_in_pos(self, pos: (int, int)):
        for button in self.particle_buttons:
            if button.rect.collidepoint(pos):
                return True
        return False

class Particle_Button:
    def __init__(self, block_type: int, x: int, y: int, width: int, height: int,  ui: User_Interface):
        self.font = pg.font.Font('freesansbold.ttf', 24)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        def on_click(): ui.on_click(self, block_type)
        self.on_click = on_click
        self.pressed = False
        self.already_pressed = False
        self.colors = self.get_colors(block_type)
        self.surface = pg.Surface((self.width, self.height))
        self.rect = pg.Rect(self.x, self.y, self.width, self.height)
        text = Block_Type().get_block_type(block_type).name.split('_')[0].capitalize()
        self.text_surface = pg.font.Font.render(self.font, text, True, (255,255,255))


    def get_colors(self, block_type: int) -> {}:
        colors = {'normal':'#ffffff', 'hover':'#28eaf3', 'pressed':'#063399'}
        b_type = Block_Type().get_block_type(block_type)
        if b_type.name == 'sand':
            colors['normal'] = '#bfb106'
            colors['hover'] = '#d3c51e'
            colors['pressed'] = '#756300'
        elif b_type.name == 'gravel':
            colors['normal'] = '#5d5d5d'
            colors['hover'] = '#8f8f8f'
            colors['pressed'] = '#424242'
        elif b_type.name == 'rock':
            colors['normal'] = '#a2a2a2'
            colors['hover'] = '#bbbbbb'
            colors['pressed'] = '#2a2a2a'
        elif b_type.name == 'water':
            colors['normal'] = '#2a71f6'
            colors['hover'] = '#76c0ea'
            colors['pressed'] = '#001e56'
        elif b_type.name == 'mud':
            colors['normal'] = '#382716'
            colors['hover'] = '#827160'
            colors['pressed'] = '#1f1104'
        elif b_type.name == 'magma':
            colors['normal'] = '#cf4311'
            colors['hover'] = '#d68060'
            colors['pressed'] = '#80290a'
        return colors

    def set_pressed(self):
        self.already_pressed = False

