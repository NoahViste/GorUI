from gui import *
import pygame
from settings import *
from textures import Texture
from functools import partial


def init_ui():
    set_color()


def set_color():
    ov = Overlay((50, 50, 440, 440), GROUP, window_name="Set color", movable=True)

    s = Scroll((10, 40, 420, 140), GROUP)
    p = []
    for i in Group.get_all():
        x = Button((0, 0, 400, 30), GROUP)
        x.set_text(str(i))
        p.append(x)
    s.add_column(*p)

    y = 195

    a1 = Display((10, y, 80, 30), GROUP, text="Main")
    a2 = Input((90, y, 160, 30), GROUP)

    b1 = Display((10, y+30, 80, 30), GROUP, text="Outline")
    b2 = Input((90, y+30, 160, 30), GROUP)

    c1 = Display((10, y+60, 80, 30), GROUP, text="Font")
    c2 = Input((90, y+60, 160, 30), GROUP)

    d1 = Display((10, y+90, 80, 30), GROUP, text="Line")
    d2 = Input((90, y+90, 160, 30), GROUP)

    e1 = Display((10, y+120, 80, 30), GROUP, text="Hover")
    e2 = Input((90, y+120, 160, 30), GROUP)

    f1 = Display((10, y+150, 80, 30), GROUP, text="Click")
    f2 = Input((90, y+150, 160, 30), GROUP)

    sub = Button((10, 390, 420, 40), GROUP, text="Apply")

    ov.add(a1, a2, b1, b2, c1, c2, d1, d2, e1, e2, f1, f2, s, sub)
    ov.add_children(*s.loop_all())


class Canvas:
    pygame.init()
    window = pygame.display.set_mode((1, 1))  # This is suboptimal, but it works

    def __init__(self, width, height):
        self.rect = pygame.Rect(0, 0, width, height)
        self.texture = Texture(self.rect, "canvas")
        self.aspect_ratio = (16, 9)
        self.reset_position()
        self.mouse_move = False

    def draw(self):
        self.window.blit(self.texture(), self.rect)
        for i in range(self.grid_width)

    def event(self, mouse, event_list):
        pressed = pygame.key.get_pressed()

        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    self.grow((self.aspect_ratio[0], self.aspect_ratio[1]))
                if event.button == 5:
                    self.grow((-self.aspect_ratio[0], -self.aspect_ratio[1]))

        if pressed[pygame.K_SPACE] and pygame.mouse.get_pressed()[0]:
            if not self.mouse_move:
                self.mouse_move = mouse
            self.rect[0] -= self.mouse_move[0] - mouse[0]
            self.rect[1] -= self.mouse_move[1] - mouse[1]

            self.mouse_move = mouse
        else:
            self.mouse_move = False

    def set_size(self, size):
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