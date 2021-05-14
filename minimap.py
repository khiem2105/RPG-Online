# from settings.screen import screen
# from settings.color import BLUE,WHITE
# from map import Map
# from personnage import Perso
import pygame
# import pickle
from settings import WIDTH, HEIGHT, MINIMAP_SCALE

class Minimap:
    def __init__(self, map, fog, display_with_nature,list_entity,player):
        #self.game = game
        self.list_mooving_entity = list_entity
        self.player = player
        self.display_with_nature = display_with_nature
        self.screen = screen
        self.map = map
        self.fog = fog
        self.map_height = len(self.map)
        self.map_width = len(self.map[0])
        self.TOP_LEFT_X = WIDTH - MINIMAP_SCALE
        self.TOP_LEFT_Y = HEIGHT - MINIMAP_SCALE
        self.surface = pygame.Surface((MINIMAP_SCALE,  MINIMAP_SCALE))
        self.surface.set_alpha(50)                # alpha level
        self.surface.fill(BLUE)
        SCALE = 10*MINIMAP_SCALE
        self.SCALE = SCALE
        self.scale = SCALE / 2
        self.rect = pygame.Rect(0, 0, SCALE, SCALE)
        self.size_big_map = self.display_with_nature.get_size()
        self.zoom_x, self.zoom_y = self.screen.get_size()
        self.rect_zoom = pygame.Rect(
            0, 0, (self.zoom_x-MINIMAP_SCALE) * 4, (self.zoom_y-MINIMAP_SCALE) * 4)
        self.zoom_map = self.display_with_nature.subsurface(self.rect_zoom)
        self.zoom_map_fog = fog.surface.subsurface(self.rect_zoom)
        # Screen_Square in minimap
        self.mini_screen_width = self.zoom_x / self.rect.width * MINIMAP_SCALE
        self.mini_screen_height = self.zoom_y / self.rect.height * MINIMAP_SCALE
        self.mini_screen_rect = pygame.Rect(
            0, 0, self.mini_screen_width, self.mini_screen_height)

    def draw_minimap(self):
        self.draw_surface()
        self.draw_white_square()
        self.check_entity()
        self.draw_entity(self.player, True)
        self.screen_square()

    def draw_white_square(self):
        minimap_rect = pygame.Rect(
            self.TOP_LEFT_X, self.TOP_LEFT_Y, MINIMAP_SCALE, MINIMAP_SCALE)
        pygame.draw.rect(self.screen, WHITE, minimap_rect, width=3)

    def draw_white_square_zoom(self):
        minimap_rect = pygame.Rect(
            MINIMAP_SCALE / 2, MINIMAP_SCALE * 3/4, self.zoom_x - MINIMAP_SCALE, self.zoom_y - MINIMAP_SCALE)
        pygame.draw.rect(self.screen, WHITE, minimap_rect, width=3)

    def draw_surface(self):
        """ 
        L'algo de cette partie est le suivant : utiliser pygame.transform.scale pour minimiser 
        la grande carte a une petite carte (minimap) puis blit sur screen 
        # Il reste des problemes a regler : self.map_sp est parfois dehors le surface display_with_nature
        # a cause de method  subsurface() 
        === > Probleme resolu!
        """

        """ Create les regles pour le Rectangle est toujours dans le surface"""
        if self.player.pos_x - self.scale < 0:
            self.rect.left = 0
            
        elif self.player.pos_x + self.scale > self.size_big_map[0]:  # width
            self.rect.right = self.size_big_map[0]
            
        else:
            
            self.rect.centerx = self.player.pos_x

        if self.player.pos_y - self.scale < 0:
            self.rect.top = 0
        elif self.player.pos_y + self.scale > self.size_big_map[1]:
            self.rect.bottom = self.size_big_map[1]
        else:
            self.rect.centery = self.player.pos_y

        # try pour etre sur que le programme marche toujours bien
        try:
            self.map_sp = self.display_with_nature.subsurface(self.rect)
            self.map_sp_fog = self.fog.surface.subsurface(self.rect)
        except:

            pass

        # self.map_sp.blit(
        #     ava_perso, (self.player.pos_x, self.player.pos_y))
        minimap = pygame.transform.scale(
            self.map_sp, (MINIMAP_SCALE, MINIMAP_SCALE))
        self.screen.blit(minimap, (self.TOP_LEFT_X, self.TOP_LEFT_Y))
        minimap_fog = pygame.transform.scale(
            self.map_sp_fog, (MINIMAP_SCALE, MINIMAP_SCALE))
        self.screen.blit(minimap_fog, (self.TOP_LEFT_X,
                                       self.TOP_LEFT_Y), special_flags=pygame.BLEND_MULT)

    def zoom_minimap(self):
        if self.player.pos_x - self.zoom_x < 0:
            self.rect_zoom.right = 0
        elif self.player.pos_x + self.zoom_x > self.size_big_map[0]:  # width
            self.rect_zoom.left = self.size_big_map[0]
        else:
            self.rect_zoom.centerx = self.player.pos_x

        if self.player.pos_y - self.zoom_y < 0:
            self.rect_zoom.top = 0
        elif self.player.pos_y + self.zoom_y > self.size_big_map[1]:
            self.rect_zoom.bottom = self.size_big_map[1]
        else:
            self.rect_zoom.centery = self.player.pos_y
        # try pour etre sur que le programme marche toujours bien
        try:
            self.zoom_map = self.display_with_nature.subsurface(self.rect_zoom)
            self.zoom_map_fog = self.fog.surface.subsurface(
                self.rect_zoom)
        except:
            pass
        minimap = pygame.transform.scale(
            self.zoom_map, (self.zoom_x - MINIMAP_SCALE, self.zoom_y - MINIMAP_SCALE))
        self.screen.blit(minimap, (MINIMAP_SCALE / 2, MINIMAP_SCALE * 3/4))
        minimap_fog = pygame.transform.scale(
            self.zoom_map_fog, (self.zoom_x - MINIMAP_SCALE, self.zoom_y - MINIMAP_SCALE))
        self.screen.blit(minimap_fog, (MINIMAP_SCALE/2,
                                       MINIMAP_SCALE * 3/4), special_flags=pygame.BLEND_MULT)
        self.draw_white_square_zoom()
        # Not work proprely now
        # self.check_entity_zoom()
       # self.zoom_draw_perso()

    # draw position of player or show monsters, NPCs in minimaps
    def draw_entity(self, entity, real):
        if real:
            x_real = entity.pos_x - self.rect.left
            y_real = entity.pos_y - self.rect.top
            x_mini = x_real / self.rect.width * MINIMAP_SCALE
            y_mini = y_real / self.rect.height * MINIMAP_SCALE
            self.screen.blit(entity.avata, (self.TOP_LEFT_X +
                                            x_mini, self.TOP_LEFT_Y + y_mini))
        else:
            x_real = entity.last_know_pos[0] - self.rect.left
            y_real = entity.last_know_pos[1] - self.rect.top
            x_mini = x_real / self.rect.width * MINIMAP_SCALE
            y_mini = y_real / self.rect.height * MINIMAP_SCALE
            mini_shadow = pygame.transform.scale(entity.shadow, (30, 30))
            self.screen.blit(mini_shadow, (self.TOP_LEFT_X +
                                           x_mini, self.TOP_LEFT_Y + y_mini))

    def draw_entity_zoom(self, entity):
        x_real = entity.pos_x - self.rect.left
        y_real = entity.pos_y - self.rect.top
        x_mini = x_real / self.rect.width * (self.zoom_x - MINIMAP_SCALE)
        y_mini = y_real / self.rect.height * (self.zoom_y - MINIMAP_SCALE)
        bigger_ava = pygame.transform.scale(entity.avata, (50, 50))
        self.screen.blit(bigger_ava, (MINIMAP_SCALE/2 +
                                      x_mini, MINIMAP_SCALE * 3/4 + y_mini))

    # Verify if a monster in the view of the player => draw it on minimap
    def check_entity(self):
        for entity in self.list_mooving_entity:
            # Check color , it's mean, if the monster is in the fog, he is hidden
            if not entity.is_hidden:
                # Check position
                if self.rect.left < entity.pos_x < self.rect.right and self.rect.top < entity.pos_y < self.rect.bottom:
                    self.draw_entity(entity, True)

            elif entity.seen:
                self.draw_entity(entity, False)

    def check_entity_zoom(self):
        for entity in self.list_mooving_entity:
            if self.rect.left < entity.pos_x < self.rect.right and self.rect.top < entity.pos_y < self.rect.bottom:
                self.draw_entity_zoom(entity)

    # Not nessary for this moment

    def screen_square(self):
        # print(self.game.center_x, self.game.center_y)
        # print(self.player.pos_x, self.player.pos_y)
        x_real = self.player.pos_x - self.rect.left
        y_real = self.player.pos_y - self.rect.top
        x_mini = x_real / self.rect.width * MINIMAP_SCALE
        y_mini = y_real / self.rect.height * MINIMAP_SCALE
        self.mini_screen_rect.center = (
            x_mini + self.TOP_LEFT_X, y_mini + self.TOP_LEFT_Y)
        # print(self.mini_screen_rect)
        pygame.draw.rect(self.screen, WHITE, self.mini_screen_rect, width=1)

    # Not work in this moment
    def zoom_draw_perso(self):
        x_real = self.player.pos_x - self.rect_zoom.left
        y_real = self.player.pos_y - self.rect_zoom.top
        # ==> Talet
        x_mini = x_real / self.rect_zoom.width * (self.zoom_x - MINIMAP_SCALE)
        y_mini = y_real / self.rect_zoom.height * (self.zoom_y - MINIMAP_SCALE)
        self.screen.blit(
            ava_perso, (MINIMAP_SCALE + x_mini, MINIMAP_SCALE + y_mini))

