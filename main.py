from gui import *
import pygame
from settings import *
from textures import Texture
from functools import partial


class Tester:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode(WINDOW)
        self.clock = pygame.time.Clock()
        self.group = "maker"

        self.mouse = pygame.mouse.get_pos()
        self.pressed = pygame.key.get_pressed()

        Texture(pygame.Rect(0, 0, 5, 5), "RED").bulk("")

        self.initUI()

        self.running = True
        self.loop()

    def initUI(self):
        ov = Overlay((200, 200, 200, 160), self.group, exit_button=False, window_name="Canvas Resolution", movable=True)
        ov.set_color(["WHITE"])
        ov.add(Input((220, 240, 160, 30), self.group, int_only=True, keep_text=True))
        ov.add(Input((220, 270, 160, 30), self.group, int_only=True, keep_text=True))
        ov.add(Button((220, 320, 160, 30), self.group, ov.quit, text="Done"))

        Button((0, 0, 40, 40), self.group, self.quit, text="X")
        Input((100, 100, 100, 40), self.group, int_only=True, keep_text=True)
        Input((100, 140, 100, 40), self.group, keep_text=True).align_text(align="left", offset=(5,0))

    def loop(self):
        while self.running:
            self.window.fill(C["DARKGREY"])

            # Draws all buttons
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

        Group.all_event(self.group, self.mouse, event_list)

    def nothing(self):
        pass

    def quit(self):
        self.running = False


t = Tester()
