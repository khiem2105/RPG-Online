import pygame as pg
from .Text import Text


class Button(object):
    """This class aims to create buttons that the user can click. 
    Notice that you need to handle what to do when the button is clicked oustide this class !"""

    def __init__(self, game, px, py, text, font, text_color, font_size, background=pg.image.load('img/large_button.png'), \
            background_hover=pg.image.load('img/large_button_over.png')):
        self.game = game
        #resize the button
        background = pg.transform.scale(background, (int(background.get_width() ), int(background.get_height() ))).convert_alpha()
        background_hover = pg.transform.scale(background_hover, (int(background_hover.get_width() ), int(background_hover.get_height() ))).convert_alpha()

        #Text and fonts of our button
        self.text = text
        self.font = font 
        self.text_color = text_color 
        self.font_size = int(font_size )

        #Background of the Button
        self.button_background = background.convert_alpha()
        self.x=px-self.button_background.get_width()//2 #Centering our coords
        self.y=(py-self.button_background.get_height()//2)  
        self.rect = self.button_background.get_rect(x=self.x, y=self.y)  # Create rectangle surface the same size as the button
        self.button_background_hover = background_hover.convert_alpha()

        #Creating the text display of the button
        self.font_obj = pg.font.Font(font, self.font_size)
        self.text_surface = self.font_obj.render(text, True, pg.Color(text_color))
        self.rectText = self.text_surface.get_rect()
        self.rectText.center = self.rect.center


    def display_button(self):
        """This functions displays the button"""
        #Adding the background to the canvas
        self.game.screen.blit(self.button_background, (self.x, self.y))
        #Adding the text surface to the canvas
        self.game.screen.blit(self.text_surface, self.rectText)

    def selected_display(self, new_color):
        "This fonction display another version of the button when selected (same as when color on mouse)"
        self.game.screen.blit(self.button_background_hover, (self.x,self.y)) #Changing the button color
        self.hover_text_surface = self.font_obj.render(self.text, True, pg.Color(new_color))
        self.game.screen.blit(self.hover_text_surface, self.rectText)

    def color_on_mouse(self, new_color) :
        'Changing button color when mouse is passing on it'
        #Testing if the button is pressed
        if self.rect.collidepoint(pg.mouse.get_pos()) :
            self.game.screen.blit(self.button_background_hover, (self.x,self.y)) #Changing the button color
            self.hover_text_surface = self.font_obj.render(self.text, True, pg.Color(new_color))
            self.game.screen.blit(self.hover_text_surface, self.rectText)
    

    def is_clicked(self, event):
        """Returns true if the button is clicked"""
        if event.type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint(pg.mouse.get_pos()) and event.button == 1: #left clicked only
            return True
    

    def set_position(self, x, y):
        """Moves the buttons to new coords"""
        self.x = x-self.button_background.get_width()//2
        self.y = y-self.button_background.get_height()//2
        self.rect = self.button_background.get_rect(x=self.x, y=self.y)
        self.rectText.center = self.rect.center
