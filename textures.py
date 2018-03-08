import pygame
import os
from settings import *
import time


class Texture:
    supportedFormats = ".png"

    path = os.getcwd() + "/images/"

    native = {}  # Keeps a copy of all the unscaled images
    scaled = {}  # Keeps track of all the scaled images, so it only loads them once
    data = {}  # Keeps track of all spritesheets tile width and height and animations fps

    def __init__(self, rect, name, position=0):
        self.name = name
        self.color = False
        if self.name in C:
            self.color = True

        self.position = position

        self.rect = rect
        self.res = rect.size
        self.s_res = str(self.res)
        self.image = self.__add()

    def __call__(self):
        return self.image

    def blit(self, window):
        window.blit(self(), self.rect)

    def rescale(self, rect):
        self.rect = rect
        self.res = rect.size
        self.s_res = str(self.res)
        self.image = self.__add()

    def rename(self, name, position=0):
        self.name = name
        self.color = False
        if self.name in C:
            self.color = True
        self.image = self.__add()

    def __add(self):
        # If the texture doesn't exist return
        if self.name not in self.native and not self.color:
            best_match = []
            for image in self.native:
                if self.name in image:
                    best_match.append(image)
            raise Exception("'{}' texture does not exist, did you mean: {}?".format(self.name, best_match))

        # If the resolution doesn't exist add it to dict
        if self.s_res not in self.scaled:
            self.scaled[self.s_res] = {}

        # If the name doesn't exist add an empty list
        if self.name not in self.scaled[self.s_res]:
            self.scaled[self.s_res][self.name] = [None]

        # If the position you're looking for is outside existing ones, extend the list to fit it
        while len(self.scaled[self.s_res][self.name]) < self.position+1:
            self.scaled[self.s_res][self.name].append(None)

        # If the texture doesn't exist in the scaled dict, we make it
        if self.scaled[self.s_res][self.name][self.position] is None:
            self.__add_scaled(self.name, self.res, self.position, self.color)

        return self.scaled[self.s_res][self.name][self.position]

    def bulk(self, folder):
        # Loads everything in the textures folder
        for filename in os.listdir(self.path+folder):
            self.__load(filename)

    def __load(self, filename):
        if self.supportedFormats in filename:
            # Sheet format <name_tilesize_sheet.png>
            if "_sheet" in filename: self.__load_sheet("s_", filename)

            # Animation format <name_tilesize_anim.png>
            if "_anim" in filename: self.__load_sheet("a_", filename)

            # Transparent image format <name_alpha.png>
            elif "_alpha" in filename:
                img = pygame.image.load(self.path + filename).convert_alpha()
                self.__add_native(img, filename)

            else:
                img = pygame.image.load(self.path + filename).convert()
                self.__add_native(img, filename)

    def __load_sheet(self, format, filename):
        img = pygame.image.load(self.path + filename).convert_alpha()

        name, sx, sy, useless = self.__get_info(filename)
        sx, sy = int(sx), int(sy)
        w, h = img.get_rect()[2] // sx, img.get_rect()[3] // sy

        for y in range(h):
            for x in range(w):
                image = img.subsurface((pygame.Rect(x * sx, y * sy, sx, sy)))
                self.__add_native(image, format + name)

        self.data[format + name] = [w, h, sx, sy]

    def __add_native(self, img, filename):
        try:
            self.native[filename].append(img)

        except KeyError:
            self.native[filename] = [img]

    def __add_scaled(self, filename, resolution, position, color):
        if color:
            surface = pygame.Surface(resolution)
            surface.fill(C[filename])
            self.scaled[str(resolution)][filename] = [surface]
        else:
            self.scaled[str(resolution)][filename][position] = pygame.transform.scale(self.native[filename][position], resolution)

    def __get_info(self, filename):
        return filename.split("_")
