"""A class to display a text"""
import pygame as pg


class Text(object):
    """A Text Class that contains the tools to display a text at the screen"""

    def __init__(self, surface, px, py, text, font, text_color, font_size, center=True):
        font_size=int(font_size) # avoid future bug ( when font size is a float)

        self.surface = surface 
        self.px = px
        self.py = py

        #Text color, size and font
        self.text = text
        self.font = font
        self.text_color = text_color
        self.font_size = font_size

        #Creating our surface
        self.font_obj = pg.font.Font(font, font_size)
        self.text_surface = self.font_obj.render(self.text, True, pg.Color(self.text_color))
        self.rectText = self.text_surface.get_rect()
        if center: self.rectText.center = (self.px, self.py)
        else: self.rectText.x,self.rectText.centery = (self.px, self.py)


    def display_text(self):
        """Displays the text"""
        self.surface.blit(self.text_surface, self.rectText)


    def update(self, text):
        """Update the current text with a specified text"""
        self.text = text
        self.text_surface = self.font_obj.render(self.text, True, pg.Color(self.text_color))
        self.rectText = self.text_surface.get_rect()
        self.rectText.center = (self.px, self.py)

    def get_width(self):
        return self.rectText.width

    def get_height(self):
        return self.rectText.height
    
    def get_center(self):
        return self.rectText.center

    

    

    