from gui import *
import pygame
from settings import *
from textures import Texture
from functools import partial
import math


def init_ui():
    Builder("select_widget", select_widget)
    Builder("search_widget", search_widget)
    Builder("create_widget", create_widget)
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


def create_widget():
    ov = Overlay((100, 100, 400, 400), "", window_name="Create Widget")
    box = Display((10, 40, 380, 200), "")
    box.set_color(["LIGHTESTGREY"])
    group_dis = Display((20, 50, 150, 30), "", text="Group:", outline=-1)
    group_dis.align_text("left", (5, 0))
    group_dis.set_color(["LIGHTGREY"])
    group_in = Input((170, 50, 210, 30), "")
    outline_dis = Display((20, 90, 150, 30), "", text="Outline:", outline=-1)
    outline_dis.align_text("left", (5, 0))
    outline_dis.set_color(["LIGHTGREY"])
    outline_in = Slider((170, 90, 180, 30), "", func=[0, 1, 2, 3, 4, 5], pull_h=10)
    outline_cou = Display((349, 90, 31, 30), "")
    outline_cou.pointer("text", outline_in, "current_value")
    outline_cou.pointer("value", outline_in, "current_value")
    text_dis = Display((20, 130, 150, 30), "", text="Text:", outline=-1)
    text_dis.align_text("left", (5, 0))
    text_dis.set_color(["LIGHTGREY"])
    text_in = Input((170, 130, 210, 30), "")
    dropdown = Dropdown((20, 170, 210, 30), "", text="Tester")
    dropdown.add(Display((0, 0, 210, 30), "", text="eyyy"),
                 Display((0, 0, 210, 30), "", text="adssadl"),
                 Display((0, 0, 210, 30), "", text="poooasd"))

    ov.add(box, group_dis, group_in, outline_dis, outline_in, outline_in.pull, outline_cou, text_dis, text_in, dropdown)
    ov.add_children(*dropdown.elements)

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
        self.grid = self.aspect_ratio
        self.reset_position()
        self.mouse_move = False
        self.start_select = [0, 0]
        self.end_select = [0, 0]

    def draw(self):
        pygame.draw.rect(self.window, C["canvas"], self.rect)
        self.draw_grid()
        start = self.from_grid(self.start_select)
        end = self.from_grid(self.end_select)
        end = self.to_width(start, end)
        pygame.draw.rect(self.window, C["RED"], (start, end), 3)

    def event(self, mouse, event_list):
        pressed = pygame.key.get_pressed()
        self.mouse = mouse
        print(self.grid_mouse)

        for event in event_list:
            if pressed[pygame.K_SPACE] and pygame.mouse.get_pressed()[0]:
                if not self.mouse_move:
                    self.mouse_move = mouse
                self.rect.x -= self.mouse_move[0] - mouse[0]
                self.rect.y -= self.mouse_move[1] - mouse[1]

                self.mouse_move = mouse
            else:
                self.mouse_move = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.start_select = self.grid_mouse
                    if event.button == 4:
                        self.grow((self.aspect_ratio[0], self.aspect_ratio[1]))
                    if event.button == 5:
                        self.grow((-self.aspect_ratio[0], -self.aspect_ratio[1]))

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.end_select = self.grid_mouse

            if pressed[pygame.K_RETURN]:
                Builder.toggle_visible("create_widget")

    def set_ratio(self, size):
        self.aspect_ratio = size
        self.grid = size
        self.rect.size = size
        self.check_rect_size()
        self.texture.rescale(self.rect)

    def draw_grid(self):
        for i in range(self.grid[0]):
            temp = self.rect[0]+i*(self.rect[2]//self.grid[0])
            pygame.draw.line(self.window, C["BLACK"], (temp, self.rect[1]), (temp, self.rect[1]+self.rect[3]))

        for j in range(self.grid[1]):
            temp = self.rect[1]+j*(self.rect[3]//self.grid[1])
            pygame.draw.line(self.window, C["BLACK"], (self.rect[0], temp), (self.rect[0]+self.rect[2], temp))

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

    @property
    def grid_mouse(self):
        # Tests whether or not the mouse is within the grid
        if self.rect.x <= self.mouse[0] < self.rect.x + self.tile_size[0] * self.grid[0] and \
                self.rect.y <= self.mouse[1] < self.rect.y + self.tile_size[1] * self.grid[1]:
            return math.trunc((self.mouse[0] - self.rect.x) / self.tile_size[0]), \
                   math.trunc((self.mouse[1] - self.rect.y) / self.tile_size[1])

    def from_grid(self, coord):
        return [self.rect.x + (coord[0] * self.tile_size[0]), self.rect.y + (coord[1] * self.tile_size[1])]

    def to_width(self, start, end):
        end[0] -= start[0]
        end[1] -= start[1]
        return end

    @property
    def tile_size(self):
        return self.rect[2] // self.grid[0], self.rect[3] // self.grid[1]