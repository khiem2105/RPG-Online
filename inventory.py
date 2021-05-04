import pygame as pg
from os import path
from settings import *

# inventory class, that contains items
class Inventory():
    def __init__(self,game):
        self.game=game
        self.trash_can = pg.image.load(path.join(self.game.img_folder, "Trash_Can.png")).convert_alpha()
        self.trash_can = pg.transform.scale(self.trash_can, (TILESIZE, TILESIZE))
        self.weapon_name=self.game.player.weapon
        self.weapon = pg.image.load(path.join(self.game.img_folder, self.weapon_name+".png")).convert_alpha()
        self.weapon = pg.transform.scale(self.weapon, (TILESIZE, TILESIZE))
    
    def update_items(self):
        self.weapon_name=self.game.player.weapon
        self.weapon = pg.image.load(path.join(self.game.img_folder, self.weapon_name+".png")).convert_alpha()
        self.weapon = pg.transform.scale(self.weapon, (TILESIZE, TILESIZE))
    def display_inventory(self):
        # display inventory
        pg.draw.rect(self.game.screen,(80,150,150),(WIDTH/2-2.5*TILESIZE,TILESIZE,TILESIZE*5,TILESIZE*3))
        pg.draw.rect(self.game.screen,(200,60,100),(WIDTH/2-2.5*TILESIZE,TILESIZE*5,TILESIZE*5,TILESIZE))
        for i in range(6):
            pg.draw.line(self.game.screen, (0,0,0), (WIDTH/2-2.5*TILESIZE+i*TILESIZE,TILESIZE), (WIDTH/2-2.5*TILESIZE+i*TILESIZE,TILESIZE*4), 2)
            pg.draw.line(self.game.screen, (0,0,0), (WIDTH/2-2.5*TILESIZE+i*TILESIZE,TILESIZE*5), (WIDTH/2-2.5*TILESIZE+i*TILESIZE,TILESIZE*6), 2)
        for j in range(1,7):
            pg.draw.line(self.game.screen, (0,0,0), (WIDTH/2-2.5*TILESIZE,TILESIZE*j), (WIDTH/2+2.5*TILESIZE,TILESIZE*j), 2)
        
        # display items
        self.update_items()
        self.game.screen.blit(self.trash_can,(WIDTH/2+1.5*TILESIZE,TILESIZE*3))
        self.game.screen.blit(self.weapon,(WIDTH/2-2.5*TILESIZE,TILESIZE*5))