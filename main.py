# KidsCanCode - Game Development with Pygame video series
# Tile-based game - Part 23
# Lighting Effect
# Video link: https://youtu.be/IWm5hi5Yrvk
from warnings import showwarning
import pygame as pg
import sys
from random import choice, randint
from os import path
from settings import *
from sprites import *
from tilemap import *
from network import *
from menu import *
from inventory import *
from chat_box import *
from monster import ListMobs

# HUD functions
def draw_player_health(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 20
    fill = pct * BAR_LENGTH
    outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
    if pct > 0.6:
        col = GREEN
    elif pct > 0.3:
        col = YELLOW
    else:
        col = RED
    pg.draw.rect(surf, col, fill_rect)
    pg.draw.rect(surf, WHITE, outline_rect, 2)

class Game:
    def __init__(self):
        # port
        self.port=2510
        # network
        self.other_player_list={}
        self.network = Network(self)
        # -----
        pg.mixer.pre_init(44100, -16, 4, 2048)
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.load_data()
        # Option unlimited map, re-do later
        self.do_unlimited_map = False
        self.chat_box = ChatBox(self)
        self.chatting = False
        self.nb_zombies = 0
        # mouse click
        self.is_right_click=False
        self.is_left_click=False
        self.mouse_pos_at_clicked =[0,0]



    def draw_text(self, text, font_name, size, color, x, y, align="topleft"):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(**{align: (x, y)})
        self.screen.blit(text_surface, text_rect)

    def load_data(self):
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'img')
        snd_folder = path.join(game_folder, 'snd')
        music_folder = path.join(game_folder, 'music')
        fonts_folder = path.join(game_folder, 'fonts')
        self.img_folder = img_folder
        self.fonts_folder =fonts_folder
        self.map_folder = path.join(game_folder, 'maps')
        self.title_font = path.join(img_folder, 'ZOMBIE.TTF')
        self.hud_font = path.join(img_folder, 'Impacted2.0.ttf')
        self.map = Map(path.join(self.map_folder, 'map3.txt'))
        self.wall_img = pg.image.load(path.join(img_folder, WALL_IMG)).convert_alpha()
        self.wall_img = pg.transform.scale(self.wall_img, (TILESIZE, TILESIZE))
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 180))
        self.player_img = pg.image.load(path.join(img_folder, PLAYER_IMG)).convert_alpha()
        self.bullet_images = {}
        self.bullet_images['lg'] = pg.image.load(path.join(img_folder, BULLET_IMG)).convert_alpha()
        self.bullet_images['sm'] = pg.transform.scale(self.bullet_images['lg'], (10, 10))
        self.mob_img = pg.image.load(path.join(img_folder, MOB_IMG)).convert_alpha()
        self.splat = pg.image.load(path.join(img_folder, SPLAT)).convert_alpha()
        self.splat = pg.transform.scale(self.splat, (64, 64))
        self.gun_flashes = []
        for img in MUZZLE_FLASHES:
            self.gun_flashes.append(pg.image.load(path.join(img_folder, img)).convert_alpha())
        self.item_images = {}
        for item in ITEM_IMAGES:
            self.item_images[item] = pg.image.load(path.join(img_folder, ITEM_IMAGES[item])).convert_alpha()
        # lighting effect
        self.fog = pg.Surface((WIDTH, HEIGHT))
        self.fog.fill(NIGHT_COLOR)
        self.light_mask = pg.image.load(path.join(img_folder, LIGHT_MASK)).convert_alpha()
        self.light_mask = pg.transform.scale(self.light_mask, LIGHT_RADIUS)
        self.light_rect = self.light_mask.get_rect()

    def master_extend_map(self):
        N = 15
        EXTEND_SIZE = TILESIZE * N
        data_for_sync = []
        if self.player.pos[0] > self.map.width - WIDTH:
            # Extend to the right part of the map EXTEND_SIZE N tiles with EXTEND_SIZE = N * TILESIZE
            self.map.width += EXTEND_SIZE
            self.camera.width += EXTEND_SIZE
            self.camera.camera.width += EXTEND_SIZE
            for ext_col in range(15):
                line = []
                for row in range(self.map.tileheight):
                    if row == 0:
                        # Default the first tile is Wall
                        Wall(self, self.map.tilewidth + ext_col, row)
                        line.append(1)
                        continue
                    else:
                        # 0 -> nothing, 1 -> wall ; prob = 33% Wall
                        if randint(0, 2) % 2:
                            Wall(self, self.map.tilewidth + ext_col, row)
                            line.append(1)
                            continue
                    line.append(0)
                data_for_sync.append(line)
            self.map.tilewidth += N
            print("Extended map to the right: ", self.map.width, "x", self.map.height)
            self.network.sync_resize_map("Right", data_for_sync)

        data_for_sync = []
        if self.player.pos[1] > self.map.height - HEIGHT:
            # Extend to the right part of the map EXTEND_SIZE N tiles with EXTEND_SIZE = N * TILESIZE
            self.map.height += EXTEND_SIZE
            self.camera.height += EXTEND_SIZE
            self.camera.camera.height += EXTEND_SIZE
            for ext_row in range(15):
                line = []
                for col in range(self.map.tilewidth):
                    if col == 0:
                        # Default the first tile is Wall
                        Wall(self, col,self.map.tileheight + ext_row)
                        line.append(1)
                        continue
                    else:
                        # 0 -> nothing, 1 -> wall ; prob = 33% Wall
                        if randint(0, 2) % 2:
                            Wall(self, col,self.map.tileheight + ext_row)
                            line.append(1)
                            continue
                    line.append(0)
                data_for_sync.append(line)
            self.map.tileheight += N
            print("Extended map to the bottom: ", self.map.width, "x", self.map.height)
            self.network.sync_resize_map("Bottom", data_for_sync)
            print(data_for_sync)

    def peer_extend_map(self, direction, N, data):
        EXTEND_SIZE = TILESIZE * N
        if direction == "Right":
            # Extend to the right part of the map EXTEND_SIZE N tiles with EXTEND_SIZE = N * TILESIZE
            self.map.width += EXTEND_SIZE
            self.camera.width += EXTEND_SIZE
            self.camera.camera.width += EXTEND_SIZE
            i = 0
            for ext_col in range(15):
                for row in range(self.map.tileheight):
                    if data[ext_col][row] == 1:
                        Wall(self, self.map.tilewidth + ext_col, row)
            self.map.tilewidth += N
            print("Peer fetched extended map from master: ", self.map.width, "x", self.map.height)

        if direction == "Bottom":
            print(len(data[0]), len(data))
            print(self.map.tilewidth)
            for line in data:
                print(line)
            # Extend to the right part of the map EXTEND_SIZE N tiles with EXTEND_SIZE = N * TILESIZE
            self.map.height += EXTEND_SIZE
            self.camera.height += EXTEND_SIZE
            self.camera.camera.height   += EXTEND_SIZE
            i = 0
            for ext_row in range(15):
                for col in range(self.map.tilewidth):
                    if data[ext_row][col] == 1:
                        Wall(self, col ,self.map.tileheight + ext_row)
            self.map.tileheight += N
            print("Peer fetched extended map from master: ", self.map.width, "x", self.map.height)

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()
        # self.map = TiledMap(path.join(self.map_folder, 'level1.tmx'))
        # self.map_img = self.map.make_map()
        # self.map.rect = self.map_img.get_rect()
        # for tile_object in self.map.tmxdata.objects:
        #     obj_center = vec(tile_object.x + tile_object.width / 2,
        #                      tile_object.y + tile_object.height / 2)
        #     if tile_object.name == 'player':
        #         self.player = Player(self, obj_center.x, obj_center.y)
        #         # # add other_player test version
        #         # self.other_player_list.append(OtherPlayer(self, obj_center.x, obj_center.y))
        #     if tile_object.name == 'zombie':
        #         Mob(self, obj_center.x, obj_center.y)
        #     if tile_object.name == 'wall':
        #         Obstacle(self, tile_object.x, tile_object.y,
        #                  tile_object.width, tile_object.height)
        #     if tile_object.name in ['health', 'shotgun']:
        #         Item(self, obj_center, tile_object.name)
            
        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                if tile == '1':
                    Wall(self, col, row)
                if tile == 'M':
                    self.nb_zombies += 1
                if tile == 'P':
                    self.player = Player(self, int(col*TILESIZE+TILESIZE/2), int(row*TILESIZE+TILESIZE/2))
                if tile == 'h':
                    if self.network.is_master: 
                        Item(self, [int(col*TILESIZE+TILESIZE/2),int(row*TILESIZE+TILESIZE/2)], 'health')
                    else:
                        # receive data and then init items
                        pass
                if tile == 'G':
                    if self.network.is_master:
                        gun=choice(WEAPONS_NAME)
                        Item(self, [int(col*TILESIZE+TILESIZE/2),int(row*TILESIZE+TILESIZE/2)], gun)
                    else:
                        # receive data and then init items
                        pass
                if tile =="H":
                    if self.network.is_master:
                        helmet=choice(HELMETS_NAME)
                        Item(self, [int(col*TILESIZE+TILESIZE/2),int(row*TILESIZE+TILESIZE/2)], helmet)
                    else:
                        # receive data and then init items
                        pass
                if tile =="A":
                    if self.network.is_master:
                        armor=choice(ARMORS_NAME)
                        Item(self, [int(col*TILESIZE+TILESIZE/2),int(row*TILESIZE+TILESIZE/2)], armor)
                    else:
                        # receive data and then init items
                        pass
                if tile =="L":
                    if self.network.is_master:
                        pants=choice(PANTS_NAME)
                        Item(self, [int(col*TILESIZE+TILESIZE/2),int(row*TILESIZE+TILESIZE/2)], pants)
                    else:
                        # receive data and then init items
                        pass
                if tile =="S":
                    if self.network.is_master:
                        shoes=choice(SHOES_NAME)
                        Item(self, [int(col*TILESIZE+TILESIZE/2),int(row*TILESIZE+TILESIZE/2)], shoes)
                    else:
                        # receive data and then init items
                        pass

        self.camera = Camera(self.map.width, self.map.height)
        self.inventory = Inventory(self)
        self.draw_debug = False
        self.paused = False
        self.night = False
        self.inventory_is_activate= False
        # init menu
        self.menu=Menu(self)
        self.menu_is_running=True
        # self.effects_sounds['level_start'].play()
    
    def create_mobs(self):
        self.list_mobs = ListMobs(self)
        self.list_mobs.create_mob_list()

    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        # pg.mixer.music.play(loops=-1)
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000.0  # fix for Python 2.x
            self.events()
            if not self.paused:
                self.update()
            # Extend map to map unlimited
            if self.network.is_master:
                if self.do_unlimited_map:
                    self.master_extend_map()
            self.draw()
            # print(f"player name {self.player.player_name} other player {self.other_player_list}")
            if not self.network.is_master:
                if self.network.first_message:
                    self.network.receive_first_message()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        # update portion of the game loop
        self.all_sprites.update()
        self.camera.update(self.player)
        # game over?
        # if len(self.mobs) == 0:
        #     self.playing = False

        # player hits items
        hits = pg.sprite.spritecollide(self.player, self.items, False)
        for hit in hits:
            if hit.type == 'health' and self.player.health < PLAYER_HEALTH:
                print(hit)
                hit.kill()
                # self.effects_sounds['health_up'].play()
                self.player.add_health(HEALTH_PACK_AMOUNT)
            #pickup items
            if hit.type in WEAPONS_NAME and self.player.number_of_items<14:
                print(hit)
                hit.kill()
                # self.effects_sounds['gun_pickup'].play()
                self.player.back_pack[self.player.number_of_items] = self.player.weapon
                self.player.number_of_items +=1
                self.player.weapon = hit.type
            if hit.type in HELMETS_NAME and self.player.number_of_items<14:
                print(hit)
                hit.kill()
                if self.player.helmet is not None:
                    self.player.back_pack[self.player.number_of_items] = self.player.helmet
                    self.player.number_of_items +=1
                    self.player.helmet = hit.type
                else:
                    self.player.helmet = hit.type
            if hit.type in ARMORS_NAME and self.player.number_of_items<14:
                print(hit)
                hit.kill()
                if self.player.armor is not None:
                    self.player.back_pack[self.player.number_of_items] = self.player.armor
                    self.player.number_of_items +=1
                    self.player.armor = hit.type
                else:
                    self.player.armor = hit.type
            if hit.type in PANTS_NAME and self.player.number_of_items<14:
                print(hit)
                hit.kill()
                if self.player.pants is not None:
                    self.player.back_pack[self.player.number_of_items] = self.player.pants
                    self.player.number_of_items +=1
                    self.player.pants = hit.type
                else:
                    self.player.pants = hit.type
            if hit.type in SHOES_NAME and self.player.number_of_items<14:
                print(hit)
                hit.kill()
                if self.player.shoes is not None:
                    self.player.back_pack[self.player.number_of_items] = self.player.shoes
                    self.player.number_of_items +=1
                    self.player.shoes = hit.type
                else:
                    self.player.shoes = hit.type
            
        # mobs hit player
        # hits_1 = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        # for hit in hits_1:
        #     if random() < 0.7:
        #         # choice(self.player_hit_sounds).play()
        #         pass
        #     self.player.health -= MOB_DAMAGE
        #     hit.vel = vec(0, 0)
        #     if self.player.health <= 0:
        #         self.playing = False
        # if hits_1:
        #     self.player.hit()
        #     self.player.pos += vec(MOB_KNOCKBACK, 0).rotate(-hits_1[0].rot)
        # #other_player
        # hits_2 = pg.sprite.spritecollide(self.other_player_list[0], self.mobs, False, collide_hit_rect)
        # for hit in hits_2:
        #     if random() < 0.7:
        #         # # choice(self.player_hit_sounds).play()
        #         pass
        #     self.other_player_list[0].health -= MOB_DAMAGE
        #     hit.vel = vec(0, 0)
        #     if self.other_player_list[0].health <= 0:
        #         self.playing = False
        # if hits_2:
        #     self.other_player_list[0].hit()
        #     self.other_player_list[0].pos += vec(MOB_KNOCKBACK, 0).rotate(-hits_2[0].rot)

        # bullets hit mobs
        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for mob in hits:
            # hit.health -= WEAPONS[self.player.weapon]['damage'] * len(hits[hit])
            for bullet in hits[mob]:
                mob.health -= bullet.damage
            mob.vel = vec(0, 0)

        self.chat_box.update()
        self.list_mobs.update()

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def render_fog(self):
        # draw the light mask (gradient) onto fog image
        self.fog.fill(NIGHT_COLOR)
        self.light_rect.center = self.camera.apply(self.player).center
        self.fog.blit(self.light_mask, self.light_rect)
        self.screen.blit(self.fog, (0, 0), special_flags=pg.BLEND_MULT)

    def draw(self):
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        self.screen.fill(BGCOLOR)
        # self.screen.blit(self.map_img, self.camera.apply(self.map))
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob) or isinstance(sprite, CloneMob):
                sprite.draw_health()
            self.screen.blit(sprite.image, self.camera.apply(sprite))
            # draw name Player
            if isinstance(sprite, Player):
                font = pg.font.SysFont(None, 20)
                player_name = font.render(sprite.player_name, True, RED)
                self.screen.blit(player_name, self.camera.apply(sprite))
            if isinstance(sprite, OtherPlayer):
                font = pg.font.SysFont(None, 20)
                player_name = font.render(sprite.player_name, True, WHITE)
                self.screen.blit(player_name, self.camera.apply(sprite))

            if self.draw_debug:
                pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(sprite.hit_rect), 1)
        if self.draw_debug:
            for wall in self.walls:
                pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(wall.rect), 1)
        # pg.draw.rect(self.screen, WHITE, self.player.hit_rect, 2)
        if self.night:
            self.render_fog()
        if self.inventory_is_activate:
            self.inventory.display_inventory()
        # HUD functions
        draw_player_health(self.screen, 10, 10, self.player.health / PLAYER_HEALTH)
        self.draw_text('Zombies: {}'.format(len(self.mobs)), self.hud_font, 30, WHITE,
                       WIDTH - 10, 10, align="topright")
        if self.paused:
            self.screen.blit(self.dim_screen, (0, 0))
            self.draw_text("Paused", self.title_font, 105, RED, WIDTH / 2, HEIGHT / 2, align="center")
        self.chat_box.draw()
        pg.display.flip()

    def events(self):
        # catch all events here
        for event in pg.event.get():
            self.chatting = self.chat_box.handle_event(event)
            
            if event.type == pg.QUIT:
                self.quit()
            if not self.chatting:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.quit()
                    if event.key == pg.K_h:
                        self.draw_debug = not self.draw_debug
                    if event.key == pg.K_p:
                        self.paused = not self.paused
                    if event.key == pg.K_n:
                        self.night = not self.night
                    if event.key ==pg.K_i:
                        self.inventory_is_activate = not self.inventory_is_activate
                    if event.key == pg.K_z:
                        self.chat_box.zoom = not self.chat_box.zoom
            if event.type==pg.MOUSEBUTTONDOWN and event.button==3:
                self.is_right_click=True
                self.mouse_pos_at_clicked=pg.mouse.get_pos()
            if event.type==pg.MOUSEBUTTONDOWN and event.button==1:
                self.is_left_click=True
                self.mouse_pos_at_clicked=pg.mouse.get_pos()
            if event.type==pg.MOUSEBUTTONUP:
                self.is_right_click,self.is_left_click=False,False
            if self.menu_is_running:
                self.menu.check_input(event)

    def show_start_screen(self):
        pass

    def show_go_screen(self):
        self.screen.fill(BLACK)
        self.draw_text("GAME OVER", self.title_font, 100, RED,
                       WIDTH / 2, HEIGHT / 2, align="center")
        self.draw_text("Press a key to start", self.title_font, 75, WHITE,
                       WIDTH / 2, HEIGHT * 3 / 4, align="center")
        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        pg.event.wait()
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYUP:
                    waiting = False

# create the game object
g = Game()
g.show_start_screen()
try:
    while True:
        g.new()
        while g.menu_is_running:
            g.menu.display_menu()
        g.create_mobs()
        g.run()
        g.show_go_screen()
except Exception as E:
    print(str(E))
    Cnetwork.close_socket()
    print("Closed!")
