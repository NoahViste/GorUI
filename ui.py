import pygame
from settings import *
from texturesOld import Texture
import time


def update_all(group, mouse):
    Message.update()
    Scroll.update(group)
    Button.update(group, mouse)
    Display.update(group, mouse)
    Input.update(group, mouse)
    Slider.update(group, mouse)


class Message:
    pygame.init()
    window = pygame.display.set_mode((1, 1))  # This is suboptimal, but it works
    font = pygame.font.SysFont(FONT, 28)

    maxChars = 30  # This should be tied with width
    x, y = 0, WINDOW[1]-62
    w, h = 400, 32
    distance = 32  # How much each new message moves upwards
    textMargin = 10  # Left margin for text

    # This is for the transparent background
    background = pygame.Surface((w, h), pygame.SRCALPHA, 32)
    background.fill(T_BLACK)  # format: (r, g, b, a)

    manager = []  # Keeps track of all messages

    def __init__(self, text, duration=4, color="RED", limiter=True):
        self.text = str(text)
        self.duration = duration  # Duration in seconds
        self.initialTime = time.time()
        self.color = COLORS[color]

        # If the char length is too long, create a new message with the rest
        if len(self.text) > self.maxChars:
            Message(self.text[self.maxChars::], self.duration)
            self.text = self.text[:self.maxChars]
            self.manager.append(self)

        else:
            self.manager.insert(0, self)  # Puts the newest message at the bottom

    @staticmethod
    def update():
        # We remove at the end
        remove = None
        for i, ele in enumerate(Message.manager):
            if time.time() - ele.initialTime > ele.duration:
                remove = ele

            Message.window.blit(Message.background, (Message.x, Message.y-(Message.distance*i)))
            ele.__text(i)

        if remove is not None:
            Message.manager.remove(remove)

    def __text(self, i):
        txt = self.font.render(self.text, True, self.color)
        self.window.blit(txt, pygame.Rect(self.x+self.textMargin, self.y-(self.distance*i), self.w, self.h))


class Rect:
    def __init__(self):


class Button:
    pygame.init()
    window = pygame.display.set_mode((1, 1))  # This is suboptimal, but it works
    font = pygame.font.SysFont(FONT, 28)
    manager = {}  # Keeps track of all the buttons, required for drawing, and updating them
    hovered = False

    def __init__(self, rect, func, string, group,
                 color=["LIGHTERGREY"], hover=["LIGHTGREY"], stringColor="BLACK",
                 outline=3, outline_color="BLACK", click=["GREY"], hidden=False):
        self.rect = pygame.Rect(rect)

        # Colors
        self.color = Texture((rect[2], rect[3]), *color)  # Default color
        self.hover = Texture((rect[2], rect[3]), *hover)  # Mouse hover color
        self.click = Texture((rect[2], rect[3]), *click)  # Click color
        self.stringColor = COLORS[stringColor]  # Text color
        self.outline_color = COLORS[outline_color]  # Duh

        self.func = func  # What func to run when clicked
        self.group = group
        self.string = str(string)  # Text in button
        self.outline = outline  # Outline width

        self.hidden = hidden  # Bool

        self.returned = None  # What's returned when launching the function
        self.clicked = False  # To stop hold down spam click from happening
        self.hovering = False

        if group in self.manager:
            self.manager[group].append(self)
        else: self.manager[group] = [self]

    def __call__(self):
        return self.returned

    @staticmethod
    def update(group, mouse):
        if group in Button.manager:
            Button.hovered = False
            for but in Button.manager[group]:
                if not but.hidden:
                    pygame.draw.rect(Button.window, but.outline_color, but.rect, but.outline)  # Draws outline

                    if but.rect.collidepoint(mouse):  # Mouse is hovering over a button
                        Button.hovered = True
                        Button.window.blit(but.hover(), but.rect)

                        if pygame.mouse.get_pressed()[0] and but.clicked is False:  # First time clicking
                            but.run()

                        but.hovering = True

                    else:  # If the mouse isn't hovering over anything
                        Button.window.blit(but.color(), but.rect)
                        but.hovering = False
                        but.clicked = False

                    if but.clicked is True:  # The button is being clicked
                        Button.window.blit(but.click(), but.rect)

                    if not pygame.mouse.get_pressed()[0]:
                        but.clicked = False

                    but.__text()

    def __text(self):
        txt = self.font.render(self.string, True, self.stringColor)
        text_rect = txt.get_rect(center=(self.rect[0] + self.rect[2]/2, self.rect[1] + self.rect[3]/2))
        self.window.blit(txt, text_rect)

    def run(self):
        self.returned = self.func()
        self.clicked = True

    def hide(self):
        self.hidden = True

    def show(self):
        self.hidden = False

    def kill(self):
        self.manager[self.group].remove(self)

    @staticmethod
    def killall(group):
        Button.manager[group] = []


class Overlay:
    pygame.init()
    window = pygame.display.set_mode((1, 1))  # This is suboptimal, but it works
    font = pygame.font.SysFont(FONT, 28)

    def __init__(self, rect, group, color=["WHITE"], outline=2, exitButton=40):
        self.rect = pygame.Rect(rect)
        self.group = group
        self.color = Texture((rect[2], rect[3]), *color)
        self.outline = outline

        self.exitButton = exitButton  # Either 40 or False
        if not exitButton:
            self.button = Button((0, 0, 0, 0), None, "", self.group, hidden=True)
        else:
            self.button = Button((self.rect[0] + self.rect[2] - 40, self.rect[1], exitButton, 30), self.quit, "X",
                                 self.group)

        self.mouse = pygame.mouse.get_pos()
        self.pressed = pygame.key.get_pressed()

    def loop(self):
        self.running = True

        while self.running:
            self.window.blit(self.color(), self.rect)
            pygame.draw.rect(self.window, COLORS["BLACK"], self.rect, 2)

            self.text(self.group, pygame.Rect(self.rect[0], self.rect[1]+5, self.rect[2]-self.exitButton, 30))

            # Draws everything
            update_all(self.group, self.mouse)

            self.events()

            pygame.display.update()

    def events(self):
        self.mouse = pygame.mouse.get_pos()
        self.pressed = pygame.key.get_pressed()
        for event in pygame.event.get():
            if self.exitButton:
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.quit()
            Scroll.events(event, self.group, self.mouse)

    def text(self, string, rect):
        txt = self.font.render(string, True, COLORS["BLACK"])
        text_rect = txt.get_rect(center=(rect[0] + rect[2]/2, rect[1] + rect[3]/2))
        self.window.blit(txt, text_rect)

    def quit(self):
        self.running = False
        Button.killall(self.group)
        Display.killall(self.group)
        Input.killall(self.group)
        return True


class Display:
    pygame.init()
    window = pygame.display.set_mode((1, 1))  # This is suboptimal, but it works
    font = pygame.font.SysFont(FONT, 28)
    manager = {}
    hovered = False

    def __init__(self, rect, group, text=None, func=None, align="l", outline=3,
                 color=["LIGHTERGREY"], oColor="BLACK"):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.align = align  # Can either align "l" for left, or "mid" for middle
        self.group = group
        self.func = func
        self.returned = None
        self.hidden = False
        self.color = Texture((rect[2], rect[3]), *color)

        self.outline = outline
        self.oColor = COLORS[oColor]

        # If a group exists, append it, else create it
        if group in self.manager:
            self.manager[group].append(self)
        else:
            self.manager[group] = [self]

    def __call__(self):
        return self.returned

    @staticmethod
    def update(group, mouse):
        if group in Display.manager:
            Display.hovered = False
            for box in Display.manager[group]:
                if not box.hidden:
                    pygame.draw.rect(Display.window, box.oColor, box.rect, box.outline)  # Outline
                    Display.window.blit(box.color(), box.rect)
                    if box.text is not None:
                        box.__text()
                    if box.rect.collidepoint(mouse):
                        Display.hovered = True
                        if box.func is not None and pygame.mouse.get_pressed()[0]:
                            box.returned = box.func()

    def __text(self):
        if self.align == "m":
            txt = self.font.render(self.text, True, COLORS["BLACK"])
            text_rect = txt.get_rect(center=(self.rect[0] + self.rect[2] / 2, self.rect[1] + self.rect[3] / 2))
            self.window.blit(txt, text_rect)
        elif self.align == "l":
            txt = self.font.render(self.text, True, COLORS["BLACK"])
            self.window.blit(txt, self.rect)

    def hide(self):
        self.hidden = True

    def show(self):
        self.hidden = False

    def kill(self):
        self.manager[self.group].remove(self)

    @staticmethod
    def killall(group):
        Display.manager[group] = []


class Input:
    pygame.init()
    window = pygame.display.set_mode((1, 1))  # This is suboptimal, but it works
    font = pygame.font.SysFont(FONT, 28)
    manager = {}

    def __init__(self, rect, text, group, color=["LIGHTERGREY"], selected=["GREY"], onetime=False, outline=3, keep=False):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.group = group
        self.onetime = onetime  # If this is enabled, deletes the inputbox after
        self.outline = outline
        self.keep = keep  # If True keeps string when you want to type
        self.hidden = False
        self.color = Texture((rect[2], rect[3]), *color)
        self.selected = Texture((rect[2], rect[3]), *selected)

        self.inputString = ""

        # If a group exists, append it, else create it
        if group in self.manager:
            self.manager[group].append(self)
        else:
            self.manager[group] = [self]

        self.running = True

    # Only returns strings
    def __call__(self):
        return self.inputString

    # Tries to return int
    def intCall(self):
        try:
            return int(self.inputString)
        except:
            return None

    def run(self):
        self.update(self.group, None)  # So it draws all the boxes, before going into typing mode

        if self.keep: inputString = self.inputString
        else: inputString = ""

        while self.running:
            # We draw before input, cause when it's inside infinite wait loop we want everything drawn
            pygame.draw.rect(self.window, "BLACK", self.rect, self.outline)  # Outline
            self.window.blit(self.selected(), self.rect)
            self.__text(inputString)
            self.message.update()
            pygame.display.update()

            pressed = self.__get_key()
            if pressed is not None:
                if pressed == pygame.K_BACKSPACE:
                    inputString = inputString[0:-1]
                # Ugly as all hell, but oh well
                elif pressed == pygame.K_RETURN or pressed == pygame.K_KP_ENTER or pressed == pygame.K_ESCAPE:
                    self.running = False
                elif 31 < pressed < 127:  # Letters, numbers, and special characters
                    inputString += chr(pressed)
                elif 255 < pressed < 266:  # Numpad numbers
                    inputString += chr(pressed - 208)

        self.running = True

        if self.onetime:
            self.manager[self.group].remove(self)

        self.inputString = inputString
        return self.inputString

    @staticmethod
    def update(group, mouse):
        if group in Input.manager:
            clicked = None  # So it draws them all before going into the one you clicked on
            for box in Input.manager[group]:
                if not box.hidden:
                    pygame.draw.rect(Input.window, COLORS["BLACK"], box.rect, box.outline)  # Outline
                    Input.window.blit(box.color(), box.rect)
                    box.__text(box.inputString)

                    if mouse is not None:
                        if box.rect.collidepoint(mouse):
                            if pygame.mouse.get_pressed()[0]:
                                clicked = box

            if clicked is not None:
                clicked.run()

    def __get_key(self):
        # Infinite loop until a key/mouse is pressed
        while True:
            event = pygame.event.poll()
            if event.type == pygame.KEYDOWN:
                return event.key
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.running = False
                return

    def __text(self, string):
        txt = self.font.render(self.text + str(string), True, "BLACK")
        self.window.blit(txt, self.rect)

    def changeText(self, new):
        self.inputString = str(new)

    def hide(self):
        self.hidden = True

    def show(self):
        self.hidden = False

    def kill(self):
        self.manager[self.group].remove(self)

    @staticmethod
    def killall(group):
        Input.manager[group] = []


class Scroll:
    pygame.init()
    window = pygame.display.set_mode((1, 1))  # This is suboptimal, but it works
    manager = {}

    def __init__(self, rect, elements, group, color=["WHITE"], movespeed=32, margin=10):
        self.rect = pygame.Rect(rect)
        self.elements = []
        self.group = group
        self.movespeed = movespeed
        self.margin = margin
        self.color = Texture((rect[2], rect[3]), *color)

        displace = 0
        # We're dealing with a list of lists
        for line in elements:
            for obj in line:
                obj.rect.y = self.rect.y + displace + margin
                obj.rect.x += self.rect.x + margin
                obj.group = self.group
                obj.hide()
            displace += obj.rect.height
            self.elements.append(line)

        self.manager[self.group] = self

    @staticmethod
    def update(group):
        if group in Scroll.manager:
            current = Scroll.manager[group]
            Scroll.window.blit(current.color(), current.rect)
            pygame.draw.rect(Scroll.window, COLORS["BLACK"], current.rect, 2)

            for line in current.elements:
                for obj in line:
                    if current.rect.y <= obj.rect.y < current.rect.y + current.rect.height - obj.rect.height:
                        obj.show()
                    else:
                        obj.hide()

    @staticmethod
    def events(event, group, mouse):
        try:
            if Scroll.manager[group].rect.collidepoint(mouse):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:
                        if Scroll.manager[group].elements[0][0].rect.y <= Scroll.manager[group].rect.y:
                            Scroll.manager[group].move(Scroll.manager[group].movespeed)
                    elif event.button == 5:
                        Scroll.manager[group].move(-Scroll.manager[group].movespeed)
        except KeyError:
            pass

    def move(self, amount):
        current = self.manager[self.group]
        for ui in current.elements:
            for thing in ui:
                thing.rect.y += amount


class Slider:
    pygame.init()
    window = pygame.display.set_mode((1, 1))  # This is suboptimal, but it works
    font = pygame.font.SysFont(FONT, 28)
    manager = {}

    def __init__(self, rect, elements, group, outline=3, pull_size=(15, 25), pull_outline=3,
                 outline_color="BLACK", color="LIGHTERGREY", pull_color="LIGHTGREY", pull_outline_color="BLACK"):
        self.rect = pygame.Rect(rect)
        self.elements = elements
        self.group = group
        self.x = 0

        self.ratio = rect[3] // len(elements)
        self.pull_size = pull_size
        self.pull = pygame.Rect(rect[0]+10, rect[1]+(rect[3]//2 - pull_size[1]//2), pull_size[0], pull_size[1])

        self.outline = outline
        self.outline_color = outline_color
        self.color = color
        self.pull_color = pull_color
        self.pull_outline = pull_outline
        self.pull_outline_color = pull_outline_color

        # If a group exists, append it, else create it
        if group in self.manager:
            self.manager[group].append(self)
        else:
            self.manager[group] = [self]

    def __call__(self):
        return self.elements[self.x]

    @staticmethod
    def update(group, mouse):
        if group in Slider.manager:
            for slide in Slider.manager[group]:
                pygame.draw.rect(Slider.window, slide.outline_color, slide.rect, slide.outline)  # Outline
                pygame.draw.rect(Slider.window, slide.color, slide.rect)
                pygame.draw.line(Slider.window, COLORS["BLACK"], (slide.rect[0]+10, slide.rect[1]+slide.rect[3]/2),
                                 (slide.rect[0]+slide.rect[2]-10, slide.rect[1]+slide.rect[3]/2), 1)
                pygame.draw.rect(Slider.window, slide.pull_outline_color, slide.pull, slide.pull_outline)
                pygame.draw.rect(Slider.window, slide.pull_color, slide.pull)


