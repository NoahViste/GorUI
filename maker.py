from gui import *
import pygame
from settings import *
from textures import Texture
from functools import partial


def init_ui():
    pass


class Canvas:
    pygame.init()
    window = pygame.display.set_mode((1, 1))  # This is suboptimal, but it works

    def __init__(self, width, height):
        self.rect = pygame.Rect(0, 0, width, height)
        self.texture = Texture(self.rect, "canvas")
        self.aspect_ratio = (16, 9)
        self.reset_position()
        self.mouse_move = False
        self.grid = self.aspect_ratio
        self.selection = pygame.Rect(0, 0, 0, 0)

    def draw(self):
        self.window.blit(self.texture(), self.rect)
        pygame.draw.rect(self.window, C["RED"], self.selection, 3)
        for i in range(self.grid[0]):
            temp = self.rect[0]+i*(self.rect[2]//self.grid[0])
            pygame.draw.line(self.window, C["BLACK"], (temp, self.rect[1]), (temp, self.rect[1]+self.rect[3]))

        for j in range(self.grid[1]):
            temp = self.rect[1]+j*(self.rect[3]//self.grid[1])
            pygame.draw.line(self.window, C["BLACK"], (self.rect[0], temp), (self.rect[0]+self.rect[2], temp))

    def event(self, mouse, event_list):
        pressed = pygame.key.get_pressed()

        for event in event_list:
            if pressed[pygame.K_SPACE] and pygame.mouse.get_pressed()[0]:
                if not self.mouse_move:
                    self.mouse_move = mouse
                self.rect[0] -= self.mouse_move[0] - mouse[0]
                self.rect[1] -= self.mouse_move[1] - mouse[1]

                self.mouse_move = mouse
            else:
                self.mouse_move = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.selection.topleft = mouse
                    if event.button == 3:
                        self.selection.size = (mouse[0] - self.selection.x, mouse[1] - self.selection.y)
                    if event.button == 4:
                        self.grow((self.aspect_ratio[0], self.aspect_ratio[1]))
                    if event.button == 5:
                        self.grow((-self.aspect_ratio[0], -self.aspect_ratio[1]))

    def set_ratio(self, size):
        self.aspect_ratio = size
        self.grid = size
        self.rect.size = size
        self.check_rect_size()
        self.texture.rescale(self.rect)

    def grow(self, size):
        self.rect.inflate_ip(size)
        self.check_rect_size()
        self.texture.rescale(self.rect)

    def check_rect_size(self):
        for i in self.rect.size:
            if i <= 0:
                self.rect.size = self.aspect_ratio

    def reset_position(self):
        self.rect.center = (WINDOW[0]/2, WINDOW[1]/2)

    def set_aspect_ratio(self, new):
        self.aspect_ratio = new
