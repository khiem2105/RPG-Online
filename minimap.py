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
        # self.surface.convert_alpha()
        # self.surface.set_alpha(150)                # alpha level
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

    def calculate(self, x, y, offset_x, offset_y):
        x = x / TILESIZE * self.RATE + offset_x
        y = y / TILESIZE * self.RATE + offset_y
        return x, y

    def draw_minimap(self):
        offset_x =  self.game.camera.camera.left * WIDTH / self.game.map.width / 1.5
        offset_y =  self.game.camera.camera.top * HEIGHT / self.game.map.height / 1
        self.surface.blit(self.extra_surface, (offset_x, offset_y) )
        pos_x, pos_y = self.player.pos
        pos_x, pos_y = self.calculate(pos_x, pos_y, offset_x, offset_y)
        pygame.draw.circle(self.surface, RED, (pos_x, pos_y), 10)
        for other in self.game.other_player_list.values():
            x, y = other.pos
            x, y = self.calculate(x, y , offset_x, offset_y)
            pygame.draw.circle(self.surface, BLUE, (x, y), 10)

        for mob in self.game.list_mobs.list.values():
            if mob is None or mob.is_hidden : continue
            x, y = mob.pos
            x, y = self.calculate(x, y , offset_x, offset_y)
            pygame.draw.circle(self.surface, YELLOW, (x, y) , 10)
        self.screen.blit(self.surface, self.rect)



