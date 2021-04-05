# the interface of the game (GUI)
from sys import displayhook
from typing import Sized
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
        self.start_button = Button(self.game,WIDTH//4,HEIGHT//2,"Start Game",ENCHANT_FONT,BLACK_HEX,50)
        self.join_button = Button(self.game,3*WIDTH//4,HEIGHT//2,"Join Game",ENCHANT_FONT,BLACK_HEX,50)
        # text entry for the port
        self.port=str(self.game.port)
        self.port_text_entry=TextEntry(self.game, WIDTH//2, 50, 300, 50, ENCHANT_FONT, 40, 25,self.port )


    def display_menu(self):
        # checking for user inputs
        self.game.events()
        #Updating the bkackground
        self.game.screen.blit(self.menu_background,(0,0))
        # display text entry
        self.port_text_entry.display_box()
        # Displaying button
        self.start_button.display_button()
        self.join_button.display_button()
        # changing the color of the button when detect the mouse
        self.start_button.color_on_mouse(WHITE_HEX)
        self.join_button.color_on_mouse(WHITE_HEX)
        # updating the whole screen
        pg.display.flip()


    def check_input(self,event):
        if self.start_button.is_clicked(event):
            self.game.network.is_master=True
            self.game.network.init_master()
            self.game.menu_is_running=False
        if self.join_button.is_clicked(event):
            self.game.network.is_master=False
            self.game.network.init_peer()
            self.game.menu_is_running=False
        self.port_text_entry.handle_events(event)
        self.game.port=int(self.port_text_entry.text)
