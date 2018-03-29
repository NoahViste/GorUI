from settings import *
from textures import Texture
import pygame
import copy
import time


class Group:
    pygame.init()
    window = pygame.display.set_mode((1, 1))  # This is suboptimal, but it works
    font = pygame.font.SysFont(FONT, FONT_SIZE)  # TODO: implement font sizes
    manager = []  # Keeps track of all the widgets
    collision = False  # If the mouse hovers over a dynamic widget like buttons, input boxes, etc...
    passive_collision = False  # If the mouse hovers over a passive widget like overlays or scrolls

    def __init__(self):
        self.manager.append(self)

    @staticmethod
    def all_event(group, mouse, event_list, include_global=True, reset=True):
        if reset:  # all_event gets called by overlays and scrolls, so we don't want the collisions to reset
            Group.collision = False
            Group.passive_collision = False

        for item in reversed(Group.manager):  # In case you use displays to draw backgrounds, and other stuff
            if item.visible and (item.group == group or (include_global and item.group is "")):
                item.update_vars()  # This gets the pointers value, and gives it to the local variable
                item.event(mouse, event_list)

    @staticmethod
    def all_draw(group, include_global=True):
        for item in Group.manager:
            if item.visible and (item.group == group or (include_global and item.group is "")):
                item.draw()

    @staticmethod
    def group_list(group, include_global=False):
        for item in Group.manager:
            if item.group == group or (include_global and item.group is ""):
                yield item

    @staticmethod
    def hide_group(group, include_global):
        for item in Group.manager:
            if item.group == group or (include_global and item.group is ""):
                item.set_visible(False)

    @staticmethod
    def get_all():
        for obj in copy.copy(Group.manager):
            yield obj

    @staticmethod
    def set_window(window):
        Group.window = window

    @staticmethod
    def get_obj(item_id):
        for obj in Group.manager:
            if obj.get_id() == item_id:
                return obj

    @staticmethod
    def no_events():
        # Use this for non GUI related stuff, returns False if the mouse is hovering a widget
        if Group.passive_collision or Group.collision:
            return False
        return True


class Widget(Group):
    item_id = 0  # Giving every widget a unique ID in case you need it

    def __init__(self, rect, group, func, outline, text):
        super().__init__()
        self.rect = pygame.Rect(rect)
        self.set_color()
        self.func = func
        self.outline = outline
        self.text = text
        self.visible = True
        self.value = None  # Various uses, for buttons is the return value of the function
        self.pointer_dict = {}  # Keeps track of all the pointers used in pointer and update_vars functions
        self.group = group  # The group the widget is in
        self.group_share = None  # If the widget has children this is the group given to them
        self.align = "center"  # Text align
        self.offset = (0, 0)  # Text offset
        self.id = self.item_id
        Widget.item_id += 1

    # Don't try to understand, this is just how the current textures.py implementation works
    def set_color(self, c_main=["main"], c_outline="outline", c_font="font",
                  c_hover=["hover"], c_click=["click"], c_line="line"):
        self.c_main = Texture(self.rect, *c_main)
        self.c_outline = C[c_outline]
        self.c_font = C[c_font]
        self.c_line = C[c_line]
        self.c_hover = Texture(self.rect, *c_hover)
        self.c_click = Texture(self.rect, *c_click)

    def draw_outline(self):
        pygame.draw.rect(self.window, self.c_outline, self.rect, self.outline)

    def align_text(self, align="center", offset=(0, 0)):
        self.align = align
        self.offset = offset

    def pointer(self, current_var, target_class, target_var, current_class=None):
        # current_class is used if you need to change class variables, like self.rect
        def func():
            return getattr(target_class, target_var)
        self.pointer_dict[current_var] = (func, current_class)

    def update_vars(self):
        for var, target in self.pointer_dict.items():
            if target[1] is None:  # If you need to change class variables, like self.rect
                setattr(self, var, target[0]())
            else:
                setattr(target[1], var, target[0]())

    def _text(self, text=None):
        rect = self.rect
        if text is None:
            txt = self.font.render(str(self.text), True, self.c_font)
        else:
            txt = self.font.render(str(text), True, self.c_font)

        if self.align == "center":
            rect = txt.get_rect(center=rect.center)
        else:
            rect = txt.get_rect(midleft=rect.midleft)
        self.window.blit(txt, (rect[0]+self.offset[0], rect[1]+self.offset[1]))

    def toggle_visible(self):
        self.visible = not self.visible

    def set_visible(self, boolean):
        self.visible = boolean

    def set_text(self, new):
        self.text = str(new)

    def set_outline(self, new=1):
        self.outline = new

    def del_outline(self):
        self.outline = -1

    def get_value(self):
        return self.value

    def check_collision(self, mouse, passive=False):
        if self.rect.collidepoint(mouse):
            if passive:  # Passive doesn't hijack, like overlays or scrolls
                Group.passive_collision = True
                return True

            else:
                if not Group.collision:
                    Group.collision = True
                    return True

    def set_func(self, func):
        self.func = func

    def get_id(self):
        return self.id

    def get_text(self):
        return str(self.text)


class Button(Widget):
    def __init__(self, rect, group, func=None, outline=1, text=""):
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
        if self.check_collision(mouse):
            self.state = "Hover"

            if pygame.mouse.get_pressed()[0]:
                self.state = "Click"

            for event in event_list:
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    try:
                        self.value = self.func()
                    except TypeError:
                        print("None is not a function")

        else:
            self.state = "None"

    def get_pressed(self):
        # If the button is being held down, used by the slider widget for example
        if self.state == "Click":
            return True
        return False


class Display(Widget):
    def __init__(self, rect, group, outline=1, text=""):
        super().__init__(rect, group, None, outline, text)

    def draw(self):
        self.window.blit(self.c_main(), self.rect)
        self.draw_outline()
        self._text()

    def event(self, mouse, event_list):
        self.check_collision(mouse)


class Overlay(Widget):
    unique_counter = 0  # So the overlay children don't share the same group when you have more than 1 overlay

    def __init__(self, rect, group, outline=1, text="", exit_size=(40, 30), movable=True, window_name="",
                 topbar_height=30):
        super().__init__(rect, group, None, outline, text)
        self.set_color(["WHITE"])
        self.movable = movable  # If you can click and drag on the topbar to move the overlay around
        self.window_name = window_name
        self.exit_button = None  # Declared in __ui function
        self.exit_size = exit_size
        self.topbar_height = topbar_height

        self.group_share = group + "_" + str(self.unique_counter) + "overlay"  # Group given to overlay children
        Overlay.unique_counter += 1
        self.child_list = []  # Keeps track of all the children widgets
        self.original_child_list = []  # Keep track of the original position in case you want to reset it

        self.running = False
        self.mouse_move = False  # Used when moving the overlay around
        self.original_rect = pygame.Rect(self.rect)  # Keeps track of the original position in case you want to reset it

        self.__ui()  # Creates the topbar and the exitbutton

    def __ui(self):
        self.topbar = Display((0, 0, self.rect[2]-self.exit_size[0]+1, self.topbar_height),
                              self.group, text=self.window_name)
        self.topbar.set_color(["topbar"])

        if self.topbar_height == 0: self.set_window_name("")

        self.exit_button = Button((self.rect[2] - self.exit_size[0], 0, *self.exit_size),
                                  self.group, self.quit, text="X")
        self.exit_button.set_color(c_font="exit")

        if self.exit_size == (0, 0):
            self.exit_button.set_text("")

        self.add(self.topbar, self.exit_button)

    def add(self, *args, keep_group=False):
        for obj in args:
            if not keep_group: obj.group = self.group_share
            obj.rect.x += self.rect.x  # So you don't need to know where the overlay is, just how much to offset it
            obj.rect.y += self.rect.y
            self.child_list.append(obj)
            self.original_child_list.append(pygame.Rect(obj.rect))

    def add_children(self, *args):
        self.add(*args, keep_group=True)  # I've forgotten why I'm doing this

    def draw(self):
        self.window.blit(self.c_main(), self.rect)
        self.draw_outline()
        self._text()

        Group.all_draw(self.group_share, include_global=False)  # Otherwise if the overlay is global -> recursion

    def event(self, mouse, event_list):
        self.check_collision(mouse, passive=True)

        if self.movable:
            # This is just to make the overlay move
            if self.topbar.check_collision(mouse) or self.mouse_move:
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

        # reset=False, so it doesn't reset the collisions
        Group.all_event(self.group_share, mouse, event_list, include_global=False, reset=False)

    def loop(self):
        self.set_visible(True)
        self.running = True

        # Locks it into a loop so you're forced to interact with the overlay
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

    def set_window_name(self, new):
        self.topbar.set_text(new)

    def reset(self):
        # Resets the position of the overlay, only used if self.movable=True
        for i in range(len(self.child_list)):
            self.child_list[i].rect = pygame.Rect(self.original_child_list[i])
        self.rect = pygame.Rect(self.original_rect)

    def quit(self):
        self.running = False
        self.mouse_move = False  # Otherwise next time it's visible it jumps to your mouse
        self.toggle_visible()


class Input(Widget):
    def __init__(self, rect, group, outline=1, text="", keep_text=False, int_only=False, default_int=0, max_length=99):
        super().__init__(rect, group, None, outline, text)
        self.value = text
        if int_only: self.value = default_int
        self.state = "None"  # None, Clicked
        self.keep_text = keep_text  # Next time you click the input box it either keeps the text or resets it
        self.int_only = int_only  # Only allows integers
        self.default_int = default_int
        self.max_length = max_length  # Todo: Implement scrolling function if the text goes outside the box

    def draw(self):
        if self.state == "None":
            self.window.blit(self.c_main(), self.rect)
        elif self.state == "Clicked":
            self.window.blit(self.c_click(), self.rect)

        self.draw_outline()
        self._text(self.value)  # We use the self.value as text and not self.text like default

    def event(self, mouse, event_list):
        for event in event_list:
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.check_collision(mouse):
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
                    # If the user presses ENTER
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        self.state = "None"
                        return

                    # If the user presses BACKSPACE
                    elif event.key == pygame.K_BACKSPACE:
                        if self.int_only:
                            try:
                                self.value = int(str(self.value)[:-1])  # We convert it into a string then back to int
                            except ValueError:  # If the length < 0, we set the value to 0
                                self.value = 0
                        else:
                            self.value = self.value[:-1]
                        return

                    if len(str(self.value)) < self.max_length:
                        if self.int_only:
                            try:
                                self.value = int(str(self.value) + event.unicode)
                            except ValueError:
                                print("Expected int")

                        else:
                            self.value += event.unicode  # event.unicode is a godsend


class Scroll(Widget):
    unique_counter = 0  # So the scroll children don't share the same group when you have more than 1 scroll

    def __init__(self, rect, group, outline=1, scroll_speed=30, margin=10):
        super().__init__(rect, group, None, outline, "")
        self.scroll_speed = scroll_speed  # It's recommended having this the same as the height of 1 element
        self.margin = margin
        self.elements = [[]]
        self.displace = 0  # Keeps track of the height of all elements stacked on top of each other

        self.group_share = group + "_" + str(self.unique_counter) + "scroll"
        Scroll.unique_counter += 1

    def add_line(self, *args, auto_align=True):
        total_width = 0  # Keeps track of the width when you use auto align
        for obj in args:
            obj.group = self.group_share
            obj.rect.x += self.rect.x + self.margin + total_width
            obj.rect.y = self.rect.y + self.margin + self.displace
            if auto_align: total_width += obj.rect.width

            self.calc_visible(obj)

        # Using last element height, so don't add different heights on the same line
        self.displace += obj.rect.height
        self.elements.append(list(args))

    def add_column(self, *args, auto_align=True):
        while len(args) > len(self.elements):
            self.elements.append([])
        total_height = 0
        total_width = 0
        if auto_align:
            for obj in self.elements[0]:
                total_width += obj.rect.width

        for i, obj in enumerate(args):
            obj.group = self.group_share
            obj.rect.x += self.rect.x + self.margin + total_width
            obj.rect.y = self.rect.y + self.margin + self.displace + total_height
            total_height += obj.rect.height

            self.calc_visible(obj)
            self.elements[i].append(obj)

    def loop_all(self):
        for i in self.elements:
            for j in i:
                yield j

    def draw(self):
        self.window.blit(self.c_main(), self.rect)
        self.draw_outline()
        self._text()

        Group.all_draw(self.group_share, include_global=False)

    def event(self, mouse, event_list):
        if self.check_collision(mouse, passive=True):
            for event in event_list:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:
                        for obj in self.loop_all():
                            obj.rect.y += self.scroll_speed
                            self.calc_visible(obj)

                    elif event.button == 5:
                        for obj in self.loop_all():
                            obj.rect.y -= self.scroll_speed
                            self.calc_visible(obj)

        Group.all_event(self.group_share, mouse, event_list, include_global=False, reset=False)

    def calc_visible(self, obj):
        # If the element is within the rect - margin, we draw it
        # TODO: Add partial drawing, if half the rect is outside, draw half the rect
        if self.rect.y <= obj.rect.y and obj.rect.y + obj.rect.height <= self.rect.y + self.rect.height - self.margin:
            obj.set_visible(True)

        else:
            obj.set_visible(False)


class Slider(Widget):
    def __init__(self, rect, group, func=0, outline=1, margin=10, line_width=1, pull_w=15, pull_h=0):
        super().__init__(rect, group, None, outline, "")
        # This is pretty bad, TODO: fix the pull button size
        self.pull = Button((self.rect.x + margin, self.rect.y + margin - pull_h // 2, pull_w, self.rect.height-2*margin+pull_h),
                           self.group)
        self.func = func  # The type of func determines what's returned
        self.margin = margin
        self.line_width = line_width
        self.pulling = False
        self.pull.rect.centerx = self._line_start[0]

    @property
    def current_value(self):  # TODO: Fix function name (if we create a value property -> conflict with init method)
        if type(self.func) is int:
            return self.percent

        if type(self.func) is list:
            try:
                return self.func[self.percent//(100//len(self.func))]  # Translates percent into list position
            except IndexError:
                return self.func[len(self.func)-1]  # Issue with extremities where it goes outside the list

        if callable(self.func):
            return self.func(self.percent)  # Calls the function given with the percent as argument

    @property
    def percent(self):
        # Translates the pull position to percent
        return int((self.pull.rect.centerx - self._line_start[0]) / (self._line_end[0] - self._line_start[0]) * 100)

    @property
    def _line_start(self):
        # In case the pull gets moved (for example if inside an overlay)
        return self.rect.x + 2*self.margin, self.rect.centery

    @property
    def _line_end(self):
        # Same idea as above
        return self.rect.x + self.rect.width - 2*self.margin, self.rect.centery

    def draw(self):
        self.window.blit(self.c_main(), self.rect)
        self.draw_outline()
        pygame.draw.line(self.window, self.c_line, self._line_start, self._line_end, self.line_width)
        self._text()

    def event(self, mouse, event_list):
        self.current_value  # If it's a func the property never gets called, and so the function never gets called

        if self.pull.get_pressed():  # Checks if the button is being pressed
            self.pulling = True

        # This is done because the mouse moves too fast for the button to catch up
        if pygame.mouse.get_pressed()[0] and self.pulling:
            self.pull.rect.centerx = mouse[0]
            if self.pull.rect.centerx < self._line_start[0]:
                self.pull.rect.centerx = self._line_start[0]

            elif self.pull.rect.centerx > self._line_end[0]:
                self.pull.rect.centerx = self._line_end[0]
        else:
            self.pulling = False


class Tick(Widget):
    def __init__(self, rect, group, func=None, outline=1, text="√"):
        super().__init__(rect, group, func, outline, text)
        self.ticked = False
        self.hover = False
        self.set_color(c_font="tick", c_click=["tick_click"])

    def draw(self):
        self.window.blit(self.c_main(), self.rect)

        if self.hover:
            self.window.blit(self.c_hover(), self.rect)

        if self.ticked:
            self._text()

        self.draw_outline()

    def event(self, mouse, event_list):
        if self.check_collision(mouse):
            self.hover = True
            for event in event_list:
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.ticked = not self.ticked

        else:
            self.hover = False

    def get_value(self):
        return self.ticked


class Dropdown(Widget):
    def __init__(self, rect, group, outline=1, text=""):
        super().__init__(rect, group, None, outline, text)

    def draw(self):
        pass

    def event(self):
        pass


class Builder:
    manager = []
    selected_widget = 0

    def __init__(self, name, builder_func, hide=True):
        self.name = name
        self.builder_func = builder_func
        self.ov = None
        self.hide = hide
        self.manager.append(self)

    @staticmethod
    def build_all():
        for obj in Builder.manager:
            obj.ov = obj.builder_func()
            if obj.hide: obj.ov.quit()

    @staticmethod
    def get(name):
        for obj in Builder.manager:
            if obj.name == name:
                return obj.ov
        return None

    @staticmethod
    def show(name):
        Builder.get(name).set_visible(True)

    @staticmethod
    def toggle_visible(name):
        Builder.get(name).toggle_visible()




