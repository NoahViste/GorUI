from gui import *
import pygame
from settings import *
from textures import Texture
from functools import partial


def init_ui():
    Builder("select_widget", select_widget)
    Builder("search_widget", search_widget)
    Builder.build_all()


def select_widget():
    ov = Overlay((100, 100, 400, 400), "", window_name="Select Object")

    id_box = Display((10, 40, 380, 100), "", outline=1)
    id_box.set_color(["LIGHTESTGREY"])
    id_text = Display((20, 50, 360, 30), "", text="Input object ID:", outline=-1)
    id_text.align_text("left", (5, 0))
    id_text.set_color(["LIGHTGREY"])
    by_id = Input((310, 50, 70, 30), "", int_only=True)
    id_load = Button((150, 100, 100, 30), "", func=partial(searched_widget, by_id.get_value, ov), text="Load")
    ov.add(id_box, id_text, by_id, id_load)

    search_box = Display((10, 160, 380, 100), "", outline=1)
    search_box.set_color(["LIGHTESTGREY"])
    search_text = Display((20, 170, 360, 30), "", text="Filter group:", outline=-1)
    search_text.align_text("left", (5, 0))
    search_text.set_color(["LIGHTGREY"])
    search_group = Input((240, 170, 140, 30), "", text="Maker")
    search_start = Button((150, 220, 100, 30), "", func=partial(Builder.show, "search_widget"), text="Search")
    ov.add(search_box, search_text, search_group, search_start)

    paste_box = Display((10, 280, 380, 50), "", outline=1)
    paste_box.set_color(["LIGHTESTGREY"])
    paste_text = Display((20, 290, 360, 30), "", text="Use selected:", outline=-1)
    paste_text.align_text("left", (5, 0))
    paste_text.set_color(["LIGHTGREY"])
    paste_button = Button((320, 290, 60, 30), "", text="Load")
    ov.add(paste_box, paste_text, paste_button)

    return ov


def search_widget():
    ov = Overlay((100, 100, 400, 460), "", window_name="Search")

    scroll = Scroll((10, 40, 380, 410), "")
    scroll.set_color(["LIGHTESTGREY"])

    for obj in Group.get_all():
        scroll.add_line(Display((0, 0, 260, 30), "", text=obj.get_text()),
                        Display((0, 0, 70, 30), "", text=obj.get_id()),
                        Button((0, 0, 30, 30), "", func=partial(searched_widget, obj.get_id(), ov), text=">"))

    ov.add(scroll)
    ov.add_children(*scroll.loop_all())

    return ov


def searched_widget(obj_id, overlay):
    Builder.selected_widget = obj_id
    overlay.quit()


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
