#-------------------------------------------------------------------------------
# Name:        undermine
# Purpose:
#
# Author:      PandP
#
# Created:     23/01/2018
# Copyright:   (c) PandP 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import random, time, pygame, sys
import math
import os
import copy
from pygame.locals import *
from random import choice, randint, sample, shuffle
import operator

FPS = 25
LEFT = 1
RIGHT = 3

WINDOWWIDTH = 400
WINDOWHEIGHT = 600
BOXSIZE = 30
BOARDWIDTH = 10
BOARDHEIGHT = 16
XMARGIN = 50 # (WINDOWWIDTH - (BOARDWIDTH * BOXSIZE))/2
XMAXMARGIN = 350
TOPMARGIN = 90
TOPMAXMARGIN = 570 # (480 + 90)

class GameScene(object):
    def __init__(self):
        super(GameScene, self).__init__()
        self.game_over = False
        self.board = Board()
        self.mouseX = 1
        self.mouseY = 1
        self.miner_1 = Miner(self.board.starting_player_coords[0:4], 1)
        self.miner_2 = Miner(self.board.starting_player_coords[4:], 2)
        self.miner_1.miners[1]['alive'] = False
        self.miner_2.miners[2]['alive'] = False
        self.miner_1.miners[3]['alive'] = False

        self.current_player = self.miner_2

        self.selected = False
        self.surrounding_coordinates = []
        self.get_surrounding_coords()
        self.actions = 3
        # self.actions = 5

        self.board_surface = pygame.Surface((WINDOWWIDTH, WINDOWHEIGHT), pygame.SRCALPHA)
        self.board_surface.blit(BGIMAGE, (0, 0))
        self.board_rect = self.board_surface.get_rect()
        DISPLAYSURF.blit(BGIMAGE, BGRECT)
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                self.draw_box(x, y, self.board.board[x][y])
        # draw lava
        for x in range(BOARDWIDTH):
            pixelx, pixely = self.convert_to_pixel_coords(x, 15)
            LAVARECT.topleft = pixelx, pixely
            self.board_surface.blit(LAVAIMAGE, LAVARECT)
        self.draw_current_player()
        self.draw_lives()
        self.draw_actions()
        self.draw_top_boulders()
        """self.board_surface.blit(BGIMAGE, (10, 90), (10, 90, BOXSIZE, BOXSIZE))
        MINER1RECT.topleft = 10, 90
        self.board_surface.blit(MINER1IMAGE, MINER1RECT)"""
        DISPLAYSURF.blit(self.board_surface, self.board_rect)
        pygame.display.flip()

    def render(self, screen):
        # raise NotImplementedError
        pass

    def update(self):
        # raise NotImplementedError
        pass

    def handle_events(self, events):
        for event in events: # event handling loop
            if event.type == MOUSEMOTION:
                self.mouseX, self.mouseY = event.pos
            elif event.type == pygame.MOUSEBUTTONUP and event.button == LEFT:
                if self.on_board():
                    continue
                elif self.selected is False:
                    self.select_miner()

    def convert_to_pixel_coords(self, boxx, boxy):
        # Convert the given xy coordinates of the board to xy
        # coordinates of the location on the screen.
        return (XMARGIN + (boxx * BOXSIZE)), (TOPMARGIN + (boxy * BOXSIZE))

    def draw_actions(self):
        if self.current_player == self.miner_1:
            x = 10
        else:
            x = 360
        y = 280

        used_action = 5 - self.actions
        for n in range(used_action):
            PICKAXEURECT.topleft = x, y
            self.board_surface.blit(PICKAXEUIMAGE, PICKAXEURECT)
            y += 40
        for n in range(self.actions):
            PICKAXERECT.topleft = x, y
            self.board_surface.blit(PICKAXEIMAGE, PICKAXERECT)
            y += 40

    def draw_box(self, boxx, boxy, value):
        # draw a single box
        # at xy coordinates on the board.

        pixelx, pixely = self.convert_to_pixel_coords(boxx, boxy)

        if value == "earth":
            boxImage = EARTHIMAGE
            boxRect = EARTHRECT
        elif value == "blank":
            pass
        elif value == "boulder":
            boxImage = BOULDERIMAGE
            boxRect = BOULDERRECT
        else:
            boxImage, boxRect = GETMINERIMAGEVARIABLE[value[:7]]
        boxRect.topleft = pixelx, pixely
        self.board_surface.blit(boxImage, boxRect)

    def draw_current_player(self, coords = False):
        if coords is False:
            (x, y) = self.current_player.current_coords
            pixelx, pixely = self.convert_to_pixel_coords(x, y)
        else:
            (pixelx, pixely) = coords
        self.current_player.current_rect.topleft = pixelx, pixely
        self.board_surface.blit(
            self.current_player.current_image,
            self.current_player.current_rect)

    def draw_lives(self):
        # draw lives up sides of board

        for n in range(4):
            # miner1 = self.miner_1[n]
            miner1 = self.miner_1.miners[n]
            if miner1["alive"] is True:
                MINER1RECT.topleft = 10, miner1["y_min"]
                self.board_surface.blit(MINER1IMAGE, MINER1RECT)
            else:
                GHOSTRECT.topleft = 10, miner1["y_min"]
                self.board_surface.blit(GHOSTIMAGE, GHOSTRECT)
            # miner2 = self.miner_2[n]
            miner2 = self.miner_2.miners[n]
            if miner2["alive"] is True:
                MINER2RECT.topleft = 360, miner2["y_min"]
                self.board_surface.blit(MINER2IMAGE, MINER2RECT)
            else:
                GHOSTRECT.topleft = 360, miner2["y_min"]
                self.board_surface.blit(GHOSTIMAGE, GHOSTRECT)
        if self.current_player == self.miner_1:
            x = 10
        else:
            x = 360
        self.draw_current_player((x, 90 + (self.current_player.current_miner * 40)))

    def draw_old_selected_miner(self, old_x, old_y, old_coords, rect, image):
        # draw blank board and a miner over last current miner
        self.board_surface.blit(BGIMAGE, (old_x, old_y), (old_x, old_y, BOXSIZE, BOXSIZE))
        rect.topleft = old_x, old_y
        self.board_surface.blit(image, rect)

        pixelx, pixely = self.convert_to_pixel_coords(old_coords[0], old_coords[1])
        self.board_surface.blit(BGIMAGE, (pixelx, pixely), (pixelx, pixely, BOXSIZE, BOXSIZE))
        self.draw_box(old_coords[0], old_coords[1], self.board.board[old_coords[0]][old_coords[1]])

    def draw_top_boulders(self):
        for (x,y) in self.board.top_boulders:
            pixelx, pixely = self.convert_to_pixel_coords(x, y)
            TOPBOULDERRECT.topleft = pixelx, pixely
            self.board_surface.blit(TOPBOULDERIMAGE, TOPBOULDERRECT)

    def get_surrounding_coords(self):
        # return the coords surrounding the active piece
        self.surrounding_coordinates = []
        (current_x, current_y) = self.current_player.current_coords
        for x in range(current_x-1, current_x+2):
            for y in range(current_y-1, current_y+2):
                if x in range(0,BOARDWIDTH) and y in range(0,BOARDHEIGHT):
                    if (x, y) != (current_x, current_y):
                        self.surrounding_coordinates.append((x,y))

    def  on_board(self):
        if (self.mouseX >= XMARGIN and self.mouseX < XMAXMARGIN and
                self.mouseY >= TOPMARGIN and self.mouseY < TOPMAXMARGIN):
            return True
        else:
            False

    def select_miner(self):
        miner_n = False
        if self.current_player == self.miner_1:
            if self.mouseX > XMARGIN:
                return
            miner_n = self.miner_1
        elif self.current_player == self.miner_2:
            if self.mouseX < XMAXMARGIN:
                return
            miner_n = self.miner_2
        if miner_n is False:
            return
        # check which miner was clicked
        for n in range(4):
            miners_n = miner_n.miners[n]
            if miner_n.current_miner == n:
                # they selected the current miner so continue
                continue
            if miners_n["alive"] is True and miners_n["active"] is True:
                if (self.mouseY >= miners_n["y_min"] and
                        self.mouseY <= miners_n["y_max"]):
                    old_miner = miner_n.current_miner
                    old_y = miner_n.miners[old_miner]["y_min"]
                    old_coords = miner_n.miners[old_miner]["coords"]
                    # self.miner_n.update_miner(old_miner)
                    self.draw_old_selected_miner(miner_n.x, old_y, old_coords,
                                        miner_n.rect,
                                        miner_n.image)
                    miner_n.current_miner = n
                    miner_n.get_current_coords()
                    self.draw_current_player(( miner_n.x, 90 + (self.current_player.current_miner * 40)))
                    self.draw_current_player()
                    DISPLAYSURF.blit(self.board_surface, self.board_rect)
                    pygame.display.flip()

class Scene(object):
    def __init__(self):
        pass

    def render(self, screen):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def handle_events(self, events):
        raise NotImplementedError

class SceneMananger(object):
    def __init__(self):
        self.go_to(TitleScene())

    def go_to(self, scene):
        self.scene = scene
        self.scene.manager = self

class TitleScene(object):
    def __init__(self):
        super(TitleScene, self).__init__()
        #display title screen
        TITLERECT.topleft = 0,0
        DISPLAYSURF.blit(TITLEIMAGE, TITLERECT)
        pygame.display.flip()

    def render(self, DISPLAYSURF):
        pass

    def update(self):
        pass

    def handle_events(self, events):
        for e in events:
            if e.type == KEYDOWN:
                self.manager.go_to(GameScene())

class Board(object):
    """represents the Undermine board

    The Game board is as follows:

    x_0_y_0 | x_1_y_0 | x_2_y_0 | ...... | x_9_y_0
    x_0_y_1 | x_1_y_1 | x_2_y_1 | ...... | x_9_y_1
    ....... | ....... | ....... | ...... | .......
    x_0_y_14| x_1_y_14| x_2_y_14| ...... | x_9_y_14
    x_0_y_15| x_1_y_15| x_2_y_15| ...... | x_9_y_15

    may change depending on the BOARDWIDTH and BOARDHEIGHT
    """
    def __init__(self):

        self.board = []
        self.objects = []

        #create board
        for x in range(BOARDWIDTH):
            self.board.append(["earth"] * BOARDHEIGHT)
            for y in range(BOARDHEIGHT):
                if y < 15:
                    self.objects.append((x,y))
        shuffle(self.objects)

        self.starting_player_coords = []
        self.fill_board(self.objects)
        self.get_top_boulders()

    def fill_board(self, objects):
        # random_length_list = [7,8,9,10]
        # random_length = choice(random_length_list)
        above_coords = []
        for n in range(8):
            high_enough = False
            while high_enough is False:
                (x,y) = self.objects.pop()
                if y < 15:
                    high_enough = True
            self.starting_player_coords.append((x,y))
            above_coords.append((x,y-1))
            if n < 4:
                miner = "miner_1_{}".format(n + 1)
            else:
                miner = "miner_2_{}".format(n + 1)
            self.board[x][y] = miner
        for n in range(32):
            high_enough = False
            while high_enough is False:
                (x,y)= self.objects.pop()
                if y < 15:
                    if (x,y) not in above_coords:
                        high_enough = True
            self.board[x][y] = "boulder"
        return

    def get_top_boulders(self):
        self.top_boulders = []
        x_values = random.sample(range(BOARDWIDTH), 4)
        for x in x_values:
            self.top_boulders.append((x, -1))



class Miner(object):
    """lass for remember the current state of the miners
    of each player
    """
    def __init__(self, miner_coords, player_number):

        self.miners = []
        self.player_number = player_number
        self.get_starting_attributes(miner_coords)
        self.current_miner = 0
        self.current_coords = False
        self.get_current_coords()
        self.round_complete = False
        self.get_images()
        self.x = 0
        self.get_x()

    def get_current_coords(self):
        self.current_coords = self.miners[self.current_miner]["coords"]

    def get_images(self):
        if self.player_number == 1:
            self.image = MINER1IMAGE
            self.rect = MINER1RECT
            self.current_image = CURRENTMINER1IMAGE
            self.current_rect = CURRENTMINER1RECT
        elif self.player_number == 2:
            self.image = MINER2IMAGE
            self.rect = MINER2RECT
            self.current_image = CURRENTMINER2IMAGE
            self.current_rect = CURRENTMINER2RECT

    def get_starting_attributes(self, miner_coords):
        if self.player_number in [1, 2]:
            y_min = 90
            y_max = 120
        elif self.player_number == [3, 4]:
            y_min = 280
            y_max = 310
        for n in range(len(miner_coords)):
            self.miners.append({
                        "coords": miner_coords[n],
                        "active": True,
                        "alive": True,
                        "y_min": y_min,
                        "y_max": y_max})
            y_min += 40
            y_max += 40

    def get_x(self):
        if self.player_number == 1:
            self.x = 10
        elif self.player_number == 2:
            self.x = 360

def checkForQuit():
    for event in pygame.event.get(QUIT): # get all the QUIT events
        terminate() # terminate if any QUIT events are present
    for event in pygame.event.get(KEYUP): # get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate() # terminate if the KEYUP event was for the Esc key
        pygame.event.post(event) # put the other KEYUP event objects back

def load_png(name):
    """ Load image and return image object"""
    fullname = os.path.join('texture', name)
    try:
            image = pygame.image.load(fullname)
            if image.get_alpha is None:
                image = image.convert()
            else:
                image = image.convert_alpha()
    except pygame.error, message:
            print 'Cannot load image:', fullname
            raise SystemExit, message
    return image, image.get_rect()

def makeTextObjs(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()

def terminate():
    pygame.quit()
    sys.exit()

def main():
    global DISPLAYSURF, FPSCLOCK, BGIMAGE, BGRECT, BOULDERIMAGE, BOULDERRECT,\
    CURRENTMINER1IMAGE, CURRENTMINER1RECT, CURRENTMINER2IMAGE, CURRENTMINER2RECT,\
    EARTHIMAGE, EARTHRECT, GETMINERIMAGEVARIABLE, GHOSTIMAGE, GHOSTRECT,\
    LAVAIMAGE, LAVARECT, MINER1IMAGE, MINER1RECT, MINER2IMAGE, MINER2RECT,\
    PICKAXEIMAGE, PICKAXERECT, PICKAXEUIMAGE, PICKAXEURECT, TITLEIMAGE, TITLERECT,\
    TOPBOULDERIMAGE, TOPBOULDERRECT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

    BGIMAGE, BGRECT = load_png('background.png')
    BOULDERIMAGE, BOULDERRECT = load_png('boulder.png')
    CURRENTMINER1IMAGE, CURRENTMINER1RECT =load_png('current_miner_1.png')
    CURRENTMINER2IMAGE, CURRENTMINER2RECT =load_png('current_miner_2.png')
    EARTHIMAGE, EARTHRECT = load_png('earth.png')
    GHOSTIMAGE, GHOSTRECT = load_png('ghost.png')
    LAVAIMAGE, LAVARECT = load_png('lava.png')
    MINER1IMAGE, MINER1RECT =load_png('miner_1.png')
    MINER2IMAGE, MINER2RECT =load_png('miner_2.png')
    PICKAXEIMAGE, PICKAXERECT =load_png('pickaxe.png')
    PICKAXEUIMAGE, PICKAXEURECT =load_png('pickaxe_used.png')
    TITLEIMAGE, TITLERECT = load_png('title.png')
    TOPBOULDERIMAGE, TOPBOULDERRECT = load_png('top_boulder.png')

    GETMINERIMAGEVARIABLE = {
                            'miner_1':(MINER1IMAGE, MINER1RECT),
                            'miner_2':(MINER2IMAGE, MINER2RECT)
                            }

    manager = SceneMananger()

    while True:
        checkForQuit()
        manager.scene.handle_events(pygame.event.get())
        manager.scene.update()
        manager.scene.render(DISPLAYSURF)
        FPSCLOCK.tick(FPS)

if __name__ == '__main__':
    main()
