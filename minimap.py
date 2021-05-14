from settings import *
import pygame

class Minimap:
    def __init__(self, game):
        self.game = game
        self.fog = game.fog
        self.screen = game.screen
        # self.tile_to_map = 
        # self.map_height = len(self.map)
        # self.map_width = len(self.map[0])
        self.TOP_LEFT_X = WIDTH - MINIMAP_SCALE
        self.TOP_LEFT_Y = HEIGHT - MINIMAP_SCALE
        self.surface = pygame.Surface((MINIMAP_SCALE,  MINIMAP_SCALE))
        self.surface.set_alpha(50)                # alpha level
        self.surface.fill(BLUE)
        self.rect = self.surface.get_rect()
        self.rect.bottomright = self.screen.get_rect().bottomright
        self.create_surface()
        self.player = self.game.player

    def create_surface(self):
        self.extra_surface = pygame.Surface((5*MINIMAP_SCALE,  5*MINIMAP_SCALE))
        RATE = 20
        self.RATE = RATE
        for row, tiles in enumerate(self.game.map.data):
            for col, tile in enumerate(tiles):
                if tile == '1':
                    color = GREEN
                else:
                    color = BLACK
                pygame.draw.rect(self.extra_surface, color, (RATE*col, RATE*row, RATE, RATE))


    def draw_minimap(self):
        offset_x =  self.game.camera.camera.left * WIDTH / self.game.map.width / 1.5
        offset_y =  self.game.camera.camera.top * HEIGHT / self.game.map.height / 1
        self.surface.blit(self.extra_surface, (offset_x, offset_y) )
        pos_x, pos_y = self.player.pos
        pos_x = pos_x / TILESIZE * self.RATE + offset_x
        pos_y = pos_y / TILESIZE * self.RATE + offset_y
        pygame.draw.rect(self.surface, RED, (pos_x, pos_y, 10, 10))
        self.screen.blit(self.surface, self.rect)
