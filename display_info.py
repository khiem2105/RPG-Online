from os import pardir
from settings import BLACK
import pygame as pg
from pygame.constants import BLEND_MULT
from settings import *

class InfoDisplay:
    def __init__(self, game, player):
        self.game = game
        self.width = 120
        self.height = 75
        self.player = player
        self.surface = pg.Surface((self.width, self.height)).convert()
        self.surface.fill(VERY_LIGHT_GREY)
        self.rect = self.surface.get_rect()
        player_rect = self.game.camera.apply(player)
        self.rect.center = (player_rect.centerx, player_rect.centery - self.height)
        self.font = pg.font.Font(None, 24)
        self.info = {"Name": player.player_name, "Health": player.health, "Weapon": player.weapon}
    
    def display_information(self):
        (x, y) = self.rect.topleft
        y = y + 10
        for info, content in self.info.items():
            text = info + ": " + str(content)
            txt_surface = self.font.render(text, True, (105, 165, 131))
            self.game.screen.blit(txt_surface, (x, y))
            y += 25

    def draw(self):
        print("Drawing to the screen")
        self.game.screen.blit(self.surface, self.rect)
        self.display_information()


def detect_mouse_over_player(player, camera):
    x_in = False
    y_in = False
    player_rect = camera.apply(player)
    if player_rect.centerx - player_rect.width / 2 < pg.mouse.get_pos()[0] < player_rect.centerx + player_rect.width / 2:
        x_in = True
    if player_rect.centery - player_rect.height / 2 < pg.mouse.get_pos()[1] < player_rect.centery + player_rect.height / 2:
        y_in = True
    
    return x_in and y_in