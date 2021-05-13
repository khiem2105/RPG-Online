from random import seed
import pygame as pg
from os import path
vec = pg.math.Vector2

# fonts
game_folder = path.dirname(__file__)
fonts_folder= path.join(game_folder,"fonts") 
ENCHANT_FONT = path.join(fonts_folder, "enchanted_land.otf")
ALEGREYA = path.join(fonts_folder, "alegreya.ttf")
ALEGREYA_ITALIC = path.join(fonts_folder, "alegreya_italic.ttf")

# Image
WALL_IMG = 'tileGreen_39.png'

# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BROWN = (106, 55, 5)
CYAN = (0, 255, 255)

BLACK_HEX = '#000000'
WHITE_HEX = '#FFFFFF'

# game settings
WIDTH = 800 #1024   # 16 * 64 or 32 * 32 or 64 * 16
HEIGHT = 500# 768  # 16 * 48 or 32 * 24 or 64 * 12
FPS = 60
TITLE = "Tilemap Demo"
BGCOLOR = BROWN

TILESIZE = 64
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

# Player settings
PLAYER_HEALTH = 100
PLAYER_SPEED = 280
PLAYER_ROT_SPEED = 200
PLAYER_IMG = 'manBlue_gun.png'
PLAYER_HIT_RECT = pg.Rect(0, 0, 35, 35)
BARREL_OFFSET = vec(30, 10)

# Weapon settings
BULLET_IMG = 'bullet.png'
WEAPONS_NAME=["pistol","uzi","shotgun"]
WEAPONS = {}
WEAPONS['pistol'] = {'bullet_speed': 500,
                     'bullet_lifetime': 1000,
                     'rate': 250,
                     'kickback': 200,
                     'spread': 5,
                     'damage': 10,
                     'bullet_size': 'lg',
                     'bullet_count': 1}
WEAPONS['shotgun'] = {'bullet_speed': 400,
                      'bullet_lifetime': 500,
                      'rate': 900,
                      'kickback': 300,
                      'spread': 20,
                      'damage': 5,
                      'bullet_size': 'sm',
                      'bullet_count': 12}
WEAPONS['uzi'] = {'bullet_speed': 700,
                      'bullet_lifetime': 500,
                      'rate': 50,
                      'kickback': 300,
                      'spread': 7,
                      'damage': 3,
                      'bullet_size': 'sm',
                      'bullet_count': 1}
# Helmets setting
HELMETS_NAME=["helmet1","helmet2"]
HELMETS = {}
HELMETS["helmet1"]={'health':10 }
HELMETS["helmet2"]={'health':15 }
# Armor settings
ARMORS_NAME =["armor1","armor2"]
ARMORS = {}
ARMORS["armor1"]={"health":20}
ARMORS["armor2"]={"health":30}

# pants settings
PANTS_NAME=["pants1","pants2"]
PANTS = {}
PANTS["pants1"]={'health':10,
                'speed':10}
PANTS["pants2"]={'health':15,
                'speed':15}
# shoes settings
SHOES_NAME =["shoes1","shoes2"]
SHOES ={}
SHOES["shoes1"]={'health':10,
                'speed':10}
SHOES["shoes2"]={'health':15,
                'speed':15}
# Mob settings
MOB_IMG = 'zombie1_hold.png'
MOB_SPEEDS = [150, 100, 75, 125]
MOB_HIT_RECT = pg.Rect(0, 0, 30, 30)
MOB_HEALTH = 100
MOB_DAMAGE = 10
MOB_KNOCKBACK = 20
AVOID_RADIUS = 50
DETECT_RADIUS = 400

# Effects
MUZZLE_FLASHES = ['whitePuff15.png', 'whitePuff16.png', 'whitePuff17.png',
                  'whitePuff18.png']
SPLAT = 'splat green.png'
FLASH_DURATION = 50
DAMAGE_ALPHA = [i for i in range(0, 255, 55)]
NIGHT_COLOR = (20, 20, 20)
LIGHT_RADIUS = (500, 500)
LIGHT_MASK = "light_350_soft.png"

# Layers
WALL_LAYER = 1
PLAYER_LAYER = 2
BULLET_LAYER = 3
MOB_LAYER = 2
EFFECTS_LAYER = 4
ITEMS_LAYER = 1

# Items
ITEM_IMAGES = {'health': 'health_pack.png',
               'shotgun': 'shotgun.png',
               'uzi':'uzi.png',
               'pistol':'pistol.png',
               'helmet1':'helmet1.png',
               'helmet2':'helmet2.png',
               'armor1':'armor1.png',
               'armor2':'armor2.png',
               'pants1':'pants1.png',
               'pants2':'pants2.png',
               'shoes1':'shoes1.png',
               'shoes2':'shoes2.png',}
HEALTH_PACK_AMOUNT = 20
BOB_RANGE = 10
BOB_SPEED = 0.3

# Sounds
BG_MUSIC = 'espionage.ogg'
PLAYER_HIT_SOUNDS = ['pain/8.wav', 'pain/9.wav', 'pain/10.wav', 'pain/11.wav']
ZOMBIE_MOAN_SOUNDS = ['brains2.wav', 'brains3.wav', 'zombie-roar-1.wav', 'zombie-roar-2.wav',
                      'zombie-roar-3.wav', 'zombie-roar-5.wav', 'zombie-roar-6.wav', 'zombie-roar-7.wav']
ZOMBIE_HIT_SOUNDS = ['splat-15.wav']
WEAPON_SOUNDS = {'pistol': ['pistol.wav'],
                 'shotgun': ['shotgun.wav']}
EFFECTS_SOUNDS = {'level_start': 'level_start.wav',
                  'health_up': 'health_pack.wav',
                  'gun_pickup': 'gun_pickup.wav'}


#Send data
TIME_GAPS = 0.1