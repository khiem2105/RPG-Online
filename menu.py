# the interface of the game (GUI)
import pygame as pg
from InterfacePackage import Text,TextEntry,Button
from settings import *
from os import path

class Menu:
    def __init__(self,game):
        self.game=game
        self.run_display = True 
        self.menu_background = pg.image.load(path.join(self.game.img_folder, "menu_background.jpg")).convert() 
        self.menu_background = pg.transform.scale(self.menu_background,(WIDTH,HEIGHT))
        self.clock = pg.time.Clock()
        self.start_button = Button(self.game,WIDTH//2,HEIGHT//3,"Start Game",ENCHANT_FONT,BLACK_HEX,50)
        self.join_button = Button(self.game,WIDTH//2,2*HEIGHT//3,"Join Game",ENCHANT_FONT,BLACK_HEX,50)
    
    def display_menu(self):
        pass

    def check_input(self,event):
        pass

class Join_menu():
    pass