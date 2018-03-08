from gui import *
from maker import *
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
        init_ui()

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
            q.append(Button((0, 0, 100, 30), self.group, text="tg{}".format(i)))
            k.append(Button((0, 0, 100, 30), self.group, None, text="tg{}".format(i-1)))
        z.add_column(*q)
        z.add_line(*k)
        ov.add(z)
        ov.add_children(*z.loop_all())
        s = Slider((300, 100, 160, 40), self.group)
        ov.add(s)
        ov.add(s.pull)
        y = Display((460, 100, 60, 40), self.group, text=s)
        ov.add(y)
        d = Tick((460, 200, 30, 30), self.group)
        y = Display((490, 200, 60, 40), self.group, text=d)
        ov.add(d, y)

        ov.add(self.width, self.height)
        g.set_func(ov.toggle_visible)

    def set_value(self):
        self.can.set_size((self.width.get_value(), self.height.get_value()))

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

        self.can.event(self.mouse, event_list)
        Group.all_event(self.group, self.mouse, event_list)

    def nothing(self, i):
        print(i)

    def quit(self):
        self.running = False




t = Tester()
