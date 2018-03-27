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
        init_ui()
        self.initUI()

        self.running = True
        self.loop()

    def initUI(self):
        Button((0, 0, 40, 40), self.group, self.quit, text="X")
        g = Button((40, 0, 120, 40), self.group, None, text="Settings")
        Button((160, 0, 80, 40), self.group, partial(Builder.toggle_visible, "select_widget"), text="Select")
        Display((240, 0, 60, 40), self.group).pointer("text", Builder, "selected_widget")

        ov = Overlay((50, 50, 300, 400), self.group, window_name="Canvas Resolution")
        ov.toggle_visible()
        ov.add(Display((20, 40, 160, 30), self.group, outline=-1, text="Aspect Ratio"))
        self.width = Input((180, 40, 50, 30), self.group, int_only=True, keep_text=False, max_length=3)
        self.height = Input((230, 40, 50, 30), self.group, int_only=True, keep_text=False, max_length=3)

        color = Button((20, 120, 260, 30), self.group, self.can.reset_position, text="Reset position")
        color.set_color(c_font="DARKRED")
        ov.add(color)

        ov.add(Button((20, 360, 260, 30), self.group, self.set_value, text="Edit"))

        ov.add(self.width, self.height)
        g.set_func(ov.toggle_visible)

    def set_value(self):
        self.can.set_ratio((self.width.get_value(), self.height.get_value()))

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

        Group.all_event(self.group, self.mouse, event_list)

        if Group.no_events(): self.can.event(self.mouse, event_list)

        for event in event_list:
            if event.type == pygame.QUIT:
                self.quit()

    def quit(self):
        self.running = False




t = Tester()
