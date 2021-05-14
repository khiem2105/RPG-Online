import pygame
import sys
from pygame.locals import *
from InterfacePackage.Button import *
from settings import *
import Cnetwork

class ChatBox:
    def __init__(self, game):
        self.game = game
        self.width = self.game.screen.get_width()//2
        self.height = self.game.screen.get_height()//5
        self.surface = pygame.Surface((self.width, self.height)).convert()
        self.rect = self.surface.get_rect()
        self.font = pygame.font.Font(None, 24)
        self.log = []
        # self.COLOR_INACTIVE = pygame.Color("lightskyblue3")
        # self.COLOR_ACTIVE = pygame.Color((255, 255, 255))
        # self.active = False
        self.input_box = InputBox(
            self, 0, self.game.screen.get_height() - 32)
        # Position beginning to print the log
        self.y_start = self.game.screen.get_height() - 32 - 32
        self.zoom = False
        #Create a button to hided/ unhided chat's window
        self.chat_button = Button2(self.game,30,HEIGHT - self.rect.height,pygame.image.load('img/arrow_down.png'), pygame.image.load('img/arrow_down.png'))
        
        self.chat_button_down = False

    def update(self):
        self.input_box.update()
        self.rect = self.surface.get_rect()

    def draw(self):
        if self.zoom:
            self.surface = pygame.Surface((self.width*1.5, self.height*3)).convert()
            
        else:
            self.surface = pygame.Surface((self.width, self.height)).convert()
        self.surface.fill((200, 200, 200))

        if self.chat_button_down:
            self.rect.bottomleft = (0, self.game.screen.get_height()+ self.rect.height)
            self.chat_button = Button2(self.game,20,HEIGHT - 25, pygame.image.load('img/arrow_up.png'), pygame.image.load('img/arrow_up.png'))
        else:
            self.rect.bottomleft = (0, self.game.screen.get_height())
            self.chat_button = Button2(self.game,20,HEIGHT - 25 - self.rect.height,pygame.image.load('img/arrow_down.png'), pygame.image.load('img/arrow_down.png'))
            self.print_log()
        self.game.screen.blit(self.surface, self.rect,
                            special_flags=BLEND_MULT)
        self.input_box.draw(self.game.screen)

        self.chat_button.display_button()

    def handle_event(self, event):
        active = self.input_box.handle_event(event)
        if self.chat_button.is_clicked(event):
            self.chat_button_down = not self.chat_button_down
        return active

    def print_log(self):
        y = self.y_start
        sp = max(0, len(self.log) - 8)
        offset = min(self.input_box.camera, sp)
        for i in range(offset, len(self.log)):
            if self.log[i][1] ==1:            # self.log[i][1] indicate the text from another person send to me or not
                x =5
            else:
                x = self.rect.width//2
            #type(text) == str
            #print(self.log[i])
            if (self.log[i][0] != ""):
                if self.log[i][0] == "combat":
                    txt_surface = self.font.render(self.log[i][1], True, (255, 0, 0))
                if self.log[i][0] == "info":
                    txt_surface = self.font.render(self.log[i][1], True, (255, 255, 255))
                if (self.log[i][0][0] == "@") and (self.log[i][1] == 1):
                    txt_surface = self.font.render(self.log[i][0], True, (255, 255, 0))
                else:
                    txt_surface = self.font.render(self.log[i][0], True, (255, 255, 255))
                        
                self.game.screen.blit(txt_surface, (x, y))
                y -= 25
            if y < self.rect.top:
                break

    def write_log(self, text):
        if (type(text) != tuple) and (type(text) != list):
            texts = []
            while len(text) > 41:
                head = text[:41] + '-'
                text = text[41:]
                texts.append(head)
            texts.append([text,0])
            for t in texts:
                self.log.insert(0,t)
        else:
            self.log.insert(0, text)
        self.input_box.camera = 0


class InputBox:

    def __init__(self, chat_box, x, y, text='Chat here ...'):
        self.chat_box = chat_box
        self.COLOR_INACTIVE = pygame.Color((150, 150, 150))
        self.COLOR_ACTIVE = pygame.Color((255, 255, 255))
        self.FONT = pygame.font.Font(None, 25)

        self.x = x
        self.y = y
        self.width = self.chat_box.rect.width
        self.height = 32
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.color = self.COLOR_INACTIVE
        self.text = text
        self.txt_surface = self.FONT.render(text, True, self.color)
        self.active = False
        self.first = True
        self.camera = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.text = ""
                self.active = not self.active
                if self.first:
                    self.first = False
                    self.text = ''
            else:
                self.active = False
            self.color = self.COLOR_ACTIVE if self.active else self.COLOR_INACTIVE
        if event.type == KEYDOWN:
            if self.active:
                if event.key == K_RETURN:
                    self.chat_box.write_log([self.text,0])
                    if (self.text != ""):
                        self.chat_box.game.network.add_message_to_data(self.text)
                    self.text = ''
                    self.camera = 0
                elif event.key == K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = self.FONT.render(
                    self.text, True, self.color)
        if not self.first and not self.active:
            self.text = "Use mouse's wheel to scroll!!!!"
            self.txt_surface = self.FONT.render(
                self.text, True, self.color)
        # Mouse wheel
        if event.type == MOUSEWHEEL:
            pos = pygame.mouse.get_pos()
            if 0 < pos[0] < self.chat_box.surface.get_width() and self.chat_box.game.screen.get_height() > pos[1] > self.chat_box.game.screen.get_height() - self.chat_box.surface.get_height():
                self.camera += event.y
                self.camera = 0 if self.camera < 0 else self.camera

        return self.active

    def update(self):
        self.width = self.chat_box.rect.width
        self.rect = pygame.Rect(self.chat_box.rect.bottomleft[0], self.chat_box.rect.bottomleft[1]-32, self.width, self.height)

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+10))
        pygame.draw.rect(screen, self.color, self.rect, 2)