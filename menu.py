# the interface of the game (GUI)
from sys import displayhook
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
        # init buttons
        self.start_button = Button(self.game,WIDTH//2,HEIGHT//3,"Start Game",ENCHANT_FONT,BLACK_HEX,50)
        self.join_button = Button(self.game,WIDTH//2,2*HEIGHT//3,"Join Game",ENCHANT_FONT,BLACK_HEX,50)
        

    def display_menu(self):
        # checking for user inputs
        self.game.events()
        #Updating the bkackground
        self.game.screen.blit(self.menu_background,(0,0))
        # Displaying button
        self.start_button.display_button()
        self.join_button.display_button()
        # changing the color of the button when detect the mouse
        self.start_button.color_on_mouse(WHITE_HEX)
        self.join_button.color_on_mouse(WHITE_HEX)
        # updating the whole screen
        pg.display.flip()
        
        
    def check_input(self,event):
        if self.start_button.is_clicked(event) or self.join_button.is_clicked(event):
            self.game.menu_is_running=False
