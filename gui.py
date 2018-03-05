from settings import *
from textures import Texture
import pygame
import copy


class Group:
    pygame.init()
    window = pygame.display.set_mode((1, 1))  # This is suboptimal, but it works
    font = pygame.font.SysFont(FONT, FONT_SIZE, False)
    manager = []

    def __init__(self):
        self.manager.append(self)

    @staticmethod
    def all_event(group, mouse, event_list):
        for item in reversed(Group.manager):
            if item.visible and item.group == group:
                item.event(mouse, event_list)

    @staticmethod
    def all_draw(group):
        for item in Group.manager:
            if item.visible and item.group == group:
                item.draw()

    @staticmethod
    def group_list(group):
        for item in Group.manager:
            if item.group == group:
                yield item

    @staticmethod
    def hide_group(group):
        for item in Group.manager:
            if item.group == group:
                item.set_visible(False)

    @staticmethod
    def set_window(window):
        Group.window = window


class Object(Group):
    def __init__(self, rect, group, func, outline, text):
        super().__init__()
        self.rect = pygame.Rect(rect)
        self.set_color()
        self.func = func
        self.outline = outline
        self.text = str(text)
        self.visible = True
        self.value = None
        self.group = group
        self.align = "center"  # Text align
        self.offset = (0, 0)  # Offsets text

    def set_color(self, c_main=["main"], c_outline="outline", c_font="font",
                  c_hover=["hover"], c_click=["click"]):
        self.c_main = Texture(self.rect, *c_main)
        self.c_outline = C[c_outline]
        self.c_font = C[c_font]
        self.c_hover = Texture(self.rect, *c_hover)
        self.c_click = Texture(self.rect, *c_click)

    def draw_outline(self):
        pygame.draw.rect(self.window, self.c_outline, self.rect, self.outline)

    def align_text(self, align="center", offset=(0, 0)):
        self.align = align
        self.offset = offset

    def _text(self, text=None):
        rect = self.rect
        if text is None:
            txt = self.font.render(self.text, True, self.c_font)
        else:
            txt = self.font.render(str(text), True, self.c_font)

        if self.align == "center":
            rect = txt.get_rect(center=(rect[0] + rect[2] / 2, rect[1] + rect[3] / 2))
        else:
            rect = txt.get_rect(midleft=(rect[0], rect[1] + rect[3] / 2))
        self.window.blit(txt, (rect[0]+self.offset[0], rect[1]+self.offset[1]))

    def toggle_visible(self):
        self.visible = not self.visible

    def set_visible(self, boolean):
        self.visible = boolean

    def set_text(self, new):
        self.text = str(new)

    def get_value(self):
        return self.value

    def check_focus(self, mouse):
        if self.rect.collidepoint(mouse):
            return True

    def set_func(self, func):
        self.func = func


class Button(Object):
    def __init__(self, rect, group, func, outline=1, text=""):
        super().__init__(rect, group, func, outline, text)
        self.state = "None"  # None, Hover, Click

    def draw(self):
        if self.state == "None":
            self.window.blit(self.c_main(), self.rect)

        elif self.state == "Hover":
            self.window.blit(self.c_hover(), self.rect)

        elif self.state == "Click":
            self.window.blit(self.c_click(), self.rect)

        self.draw_outline()
        self._text()

    def event(self, mouse, event_list):
        if self.rect.collidepoint(mouse):
            self.state = "Hover"

            if pygame.mouse.get_pressed()[0]:
                self.state = "Click"

            for event in event_list:
                if event.type == pygame.MOUSEBUTTONUP:
                    self.value = self.func()

        else:
            self.state = "None"


class Display(Object):
    def __init__(self, rect, group, outline=1, text=""):
        super().__init__(rect, group, None, outline, text)

    def draw(self):
        self.window.blit(self.c_main(), self.rect)
        self.draw_outline()
        self._text()

    def event(self, mouse, event_list):
        pass


class Overlay(Object):
    unique_counter = 0

    def __init__(self, rect, group, outline=1, text="", exit_button=40, movable=False, window_name=""):
        super().__init__(rect, group, None, outline, text)
        self.set_color(["WHITE"])
        self.movable = movable
        self.window_name = window_name
        self.exit_button = exit_button

        self.group_share = group + str(self.unique_counter)
        Overlay.unique_counter += 1
        self.child_list = []
        self.original_child_list = []

        self.running = False
        self.mouse_move = False
        self.original_rect = pygame.Rect(self.rect)

        self.__ui()

    def __ui(self):
        self.topbar = Display((self.rect[0], self.rect[1], self.rect[2], FONT_SIZE),
                              self.group, text=self.window_name)
        self.topbar.set_color(["LIGHTGREY"])
        self.add(self.topbar)

        if self.exit_button is not False:
            self.add(Button((self.rect[0]+self.rect[2]-self.exit_button, self.rect[1], self.exit_button, FONT_SIZE),
                            self.group, self.quit, text="X"))

    def add(self, *args):
        for obj in args:
            obj.group = self.group_share
            self.child_list.append(obj)
            self.original_child_list.append(pygame.Rect(obj.rect))

    def draw(self):
        self.window.blit(self.c_main(), self.rect)
        self.draw_outline()
        self._text()

        Group.all_draw(self.group_share)

    def event(self, mouse, event_list):
        if self.movable:
            if self.topbar.rect.collidepoint(mouse) or self.mouse_move:
                if pygame.mouse.get_pressed()[0]:
                    if not self.mouse_move:
                        self.mouse_move = mouse
                    self.rect[0] -= self.mouse_move[0] - mouse[0]
                    self.rect[1] -= self.mouse_move[1] - mouse[1]

                    for i in range(len(self.child_list)):
                        self.child_list[i].rect[0] -= self.mouse_move[0] - mouse[0]
                        self.child_list[i].rect[1] -= self.mouse_move[1] - mouse[1]

                    self.mouse_move = mouse
                else:
                    self.mouse_move = False

        Group.all_event(self.group_share, mouse, event_list)

    def loop(self):
        self.set_visible(True)
        self.running = True

        while self.running:
            self.draw()

            mouse = pygame.mouse.get_pos()

            event_list = pygame.event.get()
            for event in event_list:
                if event.type == pygame.QUIT:
                    pygame.quit()

            self.event(mouse, event_list)

            pygame.display.update()

    def get_group(self):
        return self.group_share

    def reset(self):
        for i in range(len(self.child_list)):
            self.child_list[i].rect = pygame.Rect(self.original_child_list[i])
        self.rect = pygame.Rect(self.original_rect)

    def quit(self):
        self.running = False
        self.mouse_move = False  # Otherwise next time it's visible it jumps to your mouse
        self.toggle_visible()


class Input(Object):
    def __init__(self, rect, group, outline=1, text="", keep_text=False, int_only=False, default_int=0):
        super().__init__(rect, group, None, outline, text)
        self.value = ""
        if int_only: self.value = default_int
        self.state = "None"  # None, Clicked
        self.keep_text = keep_text
        self.int_only = int_only
        self.default_int = default_int

    def draw(self):
        if self.state == "None":
            self.window.blit(self.c_main(), self.rect)
        elif self.state == "Clicked":
            self.window.blit(self.c_click(), self.rect)
        self.draw_outline()
        self._text(self.value)

    def event(self, mouse, event_list):
        if pygame.mouse.get_pressed()[0]:
            if self.rect.collidepoint(mouse):
                self.state = "Clicked"
                if not self.keep_text:
                    if self.int_only:
                        self.value = self.default_int
                    else:
                        self.value = ""

            else:
                self.state = "None"

        if self.state == "Clicked":
            for event in event_list:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        self.state = "None"
                        return
                    elif event.key == pygame.K_BACKSPACE:
                        if self.int_only:
                            try:
                                self.value = int(str(self.value)[:-1])
                            except ValueError:
                                self.value = 0
                        else:
                            self.value = self.value[:-1]
                        return

                    if self.int_only:
                        try:
                            self.value = int(str(self.value) + event.unicode)
                        except ValueError:
                            print("Expected int")

                    else:
                        self.value += event.unicode


class Scroll(Object):
    def __init__(self, rect, group, outline=1, scroll_speed=30, margin=10):
        super().__init__(rect, group, None, outline, "")
        self.elements = [[]]

    def add_line(self, *args):
        while len(args) < len(self.elements):
            self.elements.append([])
        for i in range(len(args)):
            self.elements[i] += args[i]

    def add_column(self, element_list, position=0):
        self.elements[position] += element_list

    def draw(self):
        self.window.blit(self.c_main(), self.rect)
        self.draw_outline()
        self._text()

    def event(self, mouse, event_list):
        if self.rect.collidepoint(mouse):
            for event in event_list:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:
                        pass
                    elif event.button == 5:
                        pass









