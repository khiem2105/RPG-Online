import pygame as pg
from Settings import RESOLUTION_COEFF
from .Text import Text


class Button(object):
    """This class aims to create buttons that the user can click. 
    Notice that you need to handle what to do when the button is clicked oustide this class !"""

    def __init__(self, game, px, py, text, font, text_color, font_size, background=pg.image.load('graphics/menu/large_button.png'), \
            background_hover=pg.image.load('graphics/menu/large_button_over.png')):
        self.game = game
        #resize the button
        background = pg.transform.scale(background, (int(background.get_width()*RESOLUTION_COEFF), int(background.get_height()*RESOLUTION_COEFF))).convert_alpha()
        background_hover = pg.transform.scale(background_hover, (int(background_hover.get_width()*RESOLUTION_COEFF), int(background_hover.get_height()*RESOLUTION_COEFF))).convert_alpha()

        #Text and fonts of our button
        self.text = text
        self.font = font 
        self.text_color = text_color 
        self.font_size = int(font_size*RESOLUTION_COEFF)

        #Background of the Button
        self.button_background = background.convert_alpha()
        self.x=px-self.button_background.get_width()//2 #Centering our coords
        self.y=(py-self.button_background.get_height()//2)*RESOLUTION_COEFF 
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
        self.game.display.blit(self.button_background, (self.x, self.y))
        #Adding the text surface to the canvas
        self.game.display.blit(self.text_surface, self.rectText)

    def selected_display(self, new_color):
        "This fonction display another version of the button when selected (same as when color on mouse)"
        self.game.display.blit(self.button_background_hover, (self.x,self.y)) #Changing the button color
        self.hover_text_surface = self.font_obj.render(self.text, True, pg.Color(new_color))
        self.game.display.blit(self.hover_text_surface, self.rectText)

    def color_on_mouse(self, new_color) :
        'Changing button color when mouse is passing on it'
        #Testing if the button is pressed
        if self.rect.collidepoint(pg.mouse.get_pos()) :
            self.game.display.blit(self.button_background_hover, (self.x,self.y)) #Changing the button color
            self.hover_text_surface = self.font_obj.render(self.text, True, pg.Color(new_color))
            self.game.display.blit(self.hover_text_surface, self.rectText)
    

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



class IncrementStructure(object):
    """A structure composed of buttons and text for the character menu"""
    
    def __init__(self, game, px, py, text, text_color, font_size,font='graphics/fonts/enchanted_land.otf', background=pg.image.load('graphics/menu/small_button.png'), background_hover=pg.image.load('graphics/menu/small_button_hover.png'),  value=0):
        font_size=int(font_size) #avoid future bug when font size is a float

        self.game = game
        self.px, self.py = px, py
        self.value = value

        #Text of our IncrementStructure
        self.original_text = text
        self.text = f'{text} : {self.value}'
        self.font = font 
        self.text_color = text_color 
        self.font_size = font_size 

        #Background of our IncrementStructure
        self.background = background
        self.background_hover = background_hover
        self.background_hover_surface = self.background_hover.convert() #background_hover = background displayed on mouse
        self.background_surface = self.background.convert()

        #The text that is in the middle
        self.increment_text = Text(self.game.display, self.px, self.py, self.text, self.font, self.text_color, self.font_size)
        #Our two '+' and '-' buttons
        self.p_button = Button(self.game, (self.px+self.increment_text.get_width()//2+20+self.background_surface.get_width()//2), self.py, "+", 'graphics/fonts/enchanted_land.otf', '#000000', self.font_size, self.background, self.background_hover)
        self.l_button = Button(self.game, (self.px-self.increment_text.get_width()//2-20-self.background_surface.get_width()//2), self.py, "-", 'graphics/fonts/enchanted_land.otf', '#000000', self.font_size, self.background, self.background_hover)

        #Resizing
        if len(self.text) <len("Constitution : xy"):
            self.text = "Constitution : 3"
            self.increment_text.update(self.text)
            self.p_button.set_position(self.px+self.increment_text.get_width()//2+20+self.background_surface.get_width()//2, self.py)
            self.l_button.set_position(self.px-self.increment_text.get_width()//2-20-self.background_surface.get_width()//2, self.py)

    def display_increment(self):
        """Displays the IncrementStructure"""
        
        #Calling the display of the text
        self.text = f"{self.original_text} : {self.value}"
        self.increment_text.update(self.text)
        self.increment_text.display_text()
        self.p_button.display_button()
        self.l_button.display_button()
        #For the moment, we put here our color changes
        self.p_button.color_on_mouse('#FFFFFF')
        self.l_button.color_on_mouse('#FFFFFF')

    def get_value(self):
        """Getter of value to ensure we don't modify it"""
        return self.value 