from gui import *
import pygame
from settings import *
from textures import Texture
import random
from functools import partial
import copy


class Tester:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode(WINDOW)
        self.clock = pygame.time.Clock()
        self.group = "maker"

        self.mouse = pygame.mouse.get_pos()
        self.pressed = pygame.key.get_pressed()

        Texture(pygame.Rect(0, 0, 5, 5), "RED").bulk("")

        self.can = Canvas(0, 0)
        self.initUI()

        self.running = True
        self.loop()

    def initUI(self):
        Button((0, 0, 40, 40), self.group, self.quit, text="X")
        g = Button((40, 0, 120, 40), self.group, None, text="Settings")



        ov = Overlay((50, 50, 300, 400), self.group, window_name="Canvas Resolution", movable=True)
        ov.toggle_visible()
        ov.add(Display((20, 40, 180, 30), self.group, outline=-1, text="Width"))
        self.width = Input((200, 40, 80, 30), self.group, int_only=True, keep_text=False)

        ov.add(Display((20, 70, 180, 30), self.group, outline=-1, text="Height"))
        self.height = Input((200, 70, 80, 30), self.group, int_only=True, keep_text=False)

        color = Button((20, 110, 260, 30), self.group, self.can.reset_position, text="Reset position")
        color.set_color(c_font="DARKRED")
        ov.add(color)

        ov.add(Button((20, 360, 260, 30), self.group, self.set_value, text="Edit"))

        z = Scroll((20, 150, 260, 200), self.group)
        q = []
        k = []
        for i in range(10):
            q.append(Button((0, 0, 100, 30), self.group, self.nothing, text="tg{}".format(i)))
            k.append(Button((0, 0, 100, 30), self.group, None, text="tg{}".format(i-1)))
        z.add_column(*q)
        z.add_line(*k)
        ov.add(z)
        ov.add_children(*z.loop_all())
        s = Slider((300, 100, 100, 40), self.group)
        ov.add(s)
        ov.add_children(s.pull)
        y = Display((400, 100, 60, 40), self.group, text=s.percent)
        ov.add(y)

        ov.add(self.width, self.height)
        g.set_func(ov.toggle_visible)

    def set_value(self):
        self.can.set_size(self.width.get_value(), self.height.get_value())

    def loop(self):
        while self.running:
            self.window.fill(C["DARKGREY"])

            self.can.draw()
            Group.all_draw(self.group)

            self.events()

            pygame.display.set_caption(str(self.clock.get_fps()))
            pygame.display.update()

    def events(self):
        self.mouse = pygame.mouse.get_pos()
        self.pressed = pygame.key.get_pressed()

        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                self.quit()

        self.can.event(self.mouse)
        Group.all_event(self.group, self.mouse, event_list)

    def nothing(self):
        pass

    def quit(self):
        self.running = False


class Canvas:
    pygame.init()
    window = pygame.display.set_mode((1, 1))  # This is suboptimal, but it works

    def __init__(self, width, height):
        self.rect = pygame.Rect(0, 0, width, height)
        self.reset_position()
        self.mouse_move = False

    def draw(self):
        pygame.draw.rect(self.window, C["canvas"], self.rect)

    def event(self, mouse):
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_SPACE] and pygame.mouse.get_pressed()[0]:
            if not self.mouse_move:
                self.mouse_move = mouse
            self.rect[0] -= self.mouse_move[0] - mouse[0]
            self.rect[1] -= self.mouse_move[1] - mouse[1]

            self.mouse_move = mouse
        else:
            self.mouse_move = False

    def set_size(self, width, height):
        self.rect.size = (width, height)

    def reset_position(self):
        self.rect.center = (WINDOW[0]/2, WINDOW[1]/2)

t = Tester()
