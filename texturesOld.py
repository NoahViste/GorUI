import pygame
import os
from settings import *
import time


class Texture:
    window = pygame.display.set_mode((1, 1))

    os.chdir(os.getcwd()+"/images")
    supportedFormats = ".png"

    path = os.getcwd()
    path += "/"

    native = {}  # Keeps a copy of all the unscaled images
    scaled = {}  # Keeps track of all the scaled images, so it only loads them once
    data = {}  # Keeps track of all spritesheets tile width and height and animations fps

    tick = time.time()
    animationSpeed = 10

    def __init__(self, resolution, name, position=0, add=True):
        self.name = name
        if self.name in C:
            self.color = True
        else:
            self.color = False
        self.resolution = (resolution[2], resolution[3])
        self.s_resolution = str(resolution)
        self.position = position

        if add:
            self.image = self.__add()

    def __call__(self):
        return self.image

    def rescale(self, resolution):
        self.resolution = resolution
        self.s_resolution = str(resolution)
        self.image = self.__add()

    def rename(self, name, position=0):
        self.name = name
        if self.name in C:
            self.color = True
        else:
            self.color = False
        self.image = self.__add()

    def __add(self):
        # If the resolution doesn't exist add it to dict
        if self.s_resolution not in self.scaled:
            self.scaled[self.s_resolution] = {}

        # If the name doesn't exist add an empty list
        if self.name not in self.scaled[self.s_resolution]:
            self.scaled[self.s_resolution][self.name] = [None]

        # If the position you're looking for is outside existing ones, extend the list to fit it
        while len(self.scaled[self.s_resolution][self.name]) < self.position+1:
            self.scaled[self.s_resolution][self.name].append(None)

        # If the texture doesn't exist in the scaled dict, we make it
        if self.scaled[self.s_resolution][self.name][self.position] is None:
            self.__addScaled(self.name, self.resolution, self.position, self.color)

        return self.scaled[self.s_resolution][self.name][self.position]

    def bulk(self, folder="images"):
        # Loads everything in the textures folder
        for filename in os.listdir(self.path+folder):
            self.load(filename)

    def load(self, filename):
        if self.supportedFormats in filename:
            # Sheet format <name_tilesize_sheet.png>
            if "_sheet" in filename: self.loadSheet("s_", filename)

            # Animation format <name_tilesize_anim.png>
            if "_anim" in filename: self.loadSheet("a_", filename)

            # Transparent image format <name_alpha.png>
            elif "_alpha" in filename:
                img = pygame.image.load(self.path + filename).convert_alpha()
                self.__addNative(img, filename)

            else:
                img = pygame.image.load(self.path + filename).convert()
                self.__addNative(img, filename)

    def loadSheet(self, form, filename):
        img = pygame.image.load(self.path + filename).convert_alpha()

        name, sx, sy, useless = self.__getInfo(filename)
        sx, sy = int(sx), int(sy)
        w, h = img.get_rect()[2] // sx, img.get_rect()[3] // sy

        for y in range(h):
            for x in range(w):
                image = img.subsurface((pygame.Rect(x * sx, y * sy, sx, sy)))
                self.__addNative(image, form + name)

        self.data[form + name] = [w, h, sx, sy]

    def __addNative(self, img, filename):
        try:
            self.native[filename].append(img)

        except KeyError:
            self.native[filename] = [img]

    def __addScaled(self, filename, resolution, position, color):
        if color:
            surface = pygame.Surface(resolution)
            surface.fill(C[filename])
            self.scaled[str(resolution)][filename] = [surface]
        else:
            self.scaled[str(resolution)][filename][position] = pygame.transform.scale(self.native[filename][position], resolution)

    def __getInfo(self, filename):
        return filename.split("_")





    def event(self, mouse):
        if self.visible:
            if self.movable:
                if self.topbar.rect.collidepoint(mouse) or self.mouse_move:
                    if pygame.mouse.get_pressed()[0]:
                        if not self.mouse_move:
                            self.mouse_move = mouse
                            self.original_move = list(self.rect.topleft)
                        self.rect[0] = mouse[0] - self.mouse_move[0] + self.original_move[0]
                        self.rect[1] = mouse[1] - self.mouse_move[1] + self.original_move[1]
                    else:
                        self.mouse_move = False

            Group.all_event(self.group, mouse)