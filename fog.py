# from settings.screen import screen
# from settings.color import NIGHT_COLOR,LIGHT_RADIUS
# from settings.load_img import light_mask
import pygame
# from personnage import Perso
from settings import NIGHT_COLOR,LIGHT_RADIUS
# from settings.load_img import light_mask
from pygame.locals import BLEND_MULT

class Fog:
    def __init__(self, game):
        self.game = game
        self.player = game.player
        self.screen = self.game.screen
        self.surface = pygame.Surface((self.game.map.width, self.game.map.height)).convert()
        self.surface.fill(NIGHT_COLOR)
        # self.surface.set_colorkey(BLACK)
        self.light_img = self.game.light_img
        self.light_img = pygame.transform.scale(
            self.game.light_img, (LIGHT_RADIUS , LIGHT_RADIUS ))
        self.light_rect = self.light_img.get_rect()

    def draw_fog(self):
        offset = self.game.camera.camera.topleft
        self.screen.blit(self.surface, offset, special_flags=BLEND_MULT)
        self.light_rect.center = (self.player.pos[0], self.player.pos[1])
        self.surface.blit(self.light_img, self.light_rect)
        for other in self.game.other_player_list.values():
            self.light_rect.center = (other.pos[0], other.pos[1])
            self.surface.blit(self.light_img, self.light_rect)


