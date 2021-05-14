# from settings.screen import screen
# from settings.color import NIGHT_COLOR,LIGHT_RADIUS
# from settings.load_img import light_mask
# import pygame
# from personnage import Perso
from settings import NIGHT_COLOR,LIGHT_RADIUS
# from settings.load_img import light_mask

class Fog:
    def __init__(self, game):
        self.game = game
        self.player = game.player
        self.screen = self.game.screen
        self.surface = pygame.Surface(map_display.get_size()).convert()
        self.surface.fill(NIGHT_COLOR)
        # self.surface.set_colorkey(BLACK)
        self.light_img = self.game.light_img
        self.light_img = pygame.transform.scale(
            self.game.light_img, (LIGHT_RADIUS , LIGHT_RADIUS ))
        self.light_rect = self.light_img.get_rect()

    def draw_fog(self):
        self.light_rect.center = (self.player.pos_x+self.player.img.get_width() //
                                  2, self.player.pos_y+self.player.img.get_height()//2)
        self.surface.blit(self.light_img, self.light_rect)


