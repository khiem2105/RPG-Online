# from random import seed
from sys import setdlopenflags
import pygame as pg
from os import path
from settings import *
import numpy as np

# inventory class, that contains items
class Inventory():
    def __init__(self,game):
        self.game=game
        self.trash_can = pg.image.load(path.join(self.game.img_folder, "Trash_Can.png")).convert_alpha()
        self.trash_can = pg.transform.scale(self.trash_can, (TILESIZE, TILESIZE))
        self.weapon_name=self.game.player.weapon
        self.weapon = pg.image.load(path.join(self.game.img_folder, ITEM_IMAGES[self.weapon_name])).convert_alpha()
        self.weapon = pg.transform.scale(self.weapon, (TILESIZE, TILESIZE))
        self.back_pack_items=[None]*14
        self.picked_item=None
        self.picked_item_number=None
    
    def update_items(self):
        self.weapon_name=self.game.player.weapon
        self.weapon = pg.image.load(path.join(self.game.img_folder, ITEM_IMAGES[self.weapon_name])).convert_alpha()
        self.weapon = pg.transform.scale(self.weapon, (TILESIZE, TILESIZE))
        for i in range(self.game.player.number_of_items):
            self.back_pack_items[i] = pg.image.load(path.join(self.game.img_folder, ITEM_IMAGES[self.game.player.back_pack[i]])).convert_alpha()
            self.back_pack_items[i] = pg.transform.scale(self.back_pack_items[i], (TILESIZE, TILESIZE))

    def draw_item_at_the_mouse(self,image):
        if image is not None:
            self.game.screen.blit(image,(pg.mouse.get_pos()[0]-TILESIZE//2,pg.mouse.get_pos()[1]-TILESIZE//2))
            

    def find_image_at_the_mouse(self):
        clicked_item=int((self.game.mouse_pos_at_clicked[0]+2.5*TILESIZE-WIDTH/2)/TILESIZE) + 5*int((self.game.mouse_pos_at_clicked[1]/TILESIZE-1))
        if clicked_item in range(14):
            self.picked_item_number=clicked_item
            self.picked_item= self.back_pack_items[clicked_item]
        else:
            self.picked_item= None 
            self.picked_item_number=None
    
    def remove_item(self):
        if self.picked_item_number is not None:
            
            self.game.player.back_pack.pop(self.picked_item_number)
            self.game.player.back_pack +=[None]
            self.game.player.number_of_items -=1
            self.picked_item_number=None
            self.picked_item = None
    def use_item(self):
        if self.picked_item_number is not None:
            if self.game.player.back_pack[self.picked_item_number] in WEAPONS_NAME:
                self.game.player.weapon,self.game.player.back_pack[self.picked_item_number]=self.game.player.back_pack[self.picked_item_number],self.game.player.weapon

            
            self.picked_item_number=None
            self.picked_item = None

    def display_stats(self):
        pass

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
        # --- backpack items
        for i in range(self.game.player.number_of_items):
            self.game.screen.blit(self.back_pack_items[i],(WIDTH/2-2.5*TILESIZE +(i%5)*TILESIZE,TILESIZE*(1+i//5)))
        self.game.screen.blit(self.trash_can,(WIDTH/2+1.5*TILESIZE,TILESIZE*3))
        # --- in used items
        self.game.screen.blit(self.weapon,(WIDTH/2-2.5*TILESIZE,TILESIZE*5))
        if self.game.is_left_click:
            self.find_image_at_the_mouse()
            self.draw_item_at_the_mouse(self.picked_item)
        elif self.picked_item_number is not None:
            if int(pg.mouse.get_pos()[0]) in range(int(WIDTH//2+1.5*TILESIZE),int(WIDTH//2+2.5*TILESIZE)) and int(pg.mouse.get_pos()[1]) in range(3*TILESIZE,4*TILESIZE):
                self.remove_item()
            if int(pg.mouse.get_pos()[0]) in range(int(WIDTH//2-2.5*TILESIZE),int(WIDTH//2+2.5*TILESIZE)) and int(pg.mouse.get_pos()[1]) in range(5*TILESIZE,6*TILESIZE) :
                self.use_item()
        # print(self.game.player.number_of_items)