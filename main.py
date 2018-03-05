from gui import *
import pygame
from settings import *
from textures import Texture
import random
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

        self.can = Canvas(0, 0)
        self.initUI()

        self.running = True
        self.loop()

    def initUI(self):
        Button((0, 0, 40, 40), self.group, self.quit, text="X")
        g = Button((40, 0, 120, 40), self.group, None, text="Settings")

        ov = Overlay((200, 200, 300, 240), self.group, window_name="Canvas Resolution", movable=True)
        ov.toggle_visible()
        ov.add(Display((220, 240, 180, 30), self.group, outline=-1, text="Width"))
        self.width = Input((400, 240, 80, 30), self.group, int_only=True, keep_text=False)

        ov.add(Display((220, 270, 180, 30), self.group, outline=-1, text="Height"))
        self.height = Input((400, 270, 80, 30), self.group, int_only=True, keep_text=False)

        color = Button((220, 310, 260, 30), self.group, self.can.reset_position, text="Reset position")
        color.set_color(c_font="DARKRED")
        ov.add(color)

        ov.add(Button((220, 400, 260, 30), self.group, self.set_value, text="Edit"))

        ov.add(self.width)
        ov.add(self.height)
        g.set_func(ov.toggle_visible)

        self.islanders()
        Button((160, 0, 120, 40), self.group, self.island.toggle_visible, text="Island")

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

    def islanders(self):
        island = Overlay((100, 100, 600, 400), self.group, window_name="Islanders", movable=True)
        self.island_show = Display((110, 345, 200, 40), self.group)
        self.island_show2 = Display((110, 385, 200, 40), self.group)
        island.add(self.island_show)
        island.add(self.island_show2)
        self.island_new()
        for i in range(6):
            b = Button((110 + i * 40, 135, 40, 40), self.group, self.nothing, text=i+1)
            b2 = Button((110 + i * 40, 175, 40, 40), self.group, self.nothing, text=i+7)
            b.set_func(partial(self.island_func, b))
            b2.set_func(partial(self.island_func, b2))
            island.add(b, b2)
        island.add(Button((110, 220, 200, 40), self.group, self.island_weigh, text="Weigh"))
        island.add(Button((110, 260, 200, 40), self.group, self.island_reset, text="Reset"))
        island.add(Button((110, 300, 200, 40), self.group, self.island_new, text="New"))
        self.island = island
        self.island_reset()

    def island_func(self, b):
        b.set_color(c_font="DARKRED")
        self.island_tbweigh.append(b)

    def island_weigh(self):
        p = []
        n = 0
        m = 0
        for i in self.island_tbweigh:
            p.append(self.island_all[int(i.text)])
        print(p)
        for i in range(len(p)//2):
            n += p[i]
            m += p[i+len(p)//2]
        print(n, m)
        if n < m:
            self.island_show2.set_text("{} lighter".format(3))
        elif n == m:
            self.island_show2.set_text("Same weight")
        else:
            self.island_show2.set_text("First heavier")

    def island_reset(self):
        self.island_tbweigh = []
        for but in Group.group_list(self.island.get_group()):
            but.set_color()

    def island_new(self):
        self.island_all = [1 for i in range(12)]
        g = random.randint(0, 11)
        if random.randint(1, 2):
            self.island_all[g] += 0.1
        else:
            self.island_all[g] -= 0.1
        self.island_show.set_text(g)

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
