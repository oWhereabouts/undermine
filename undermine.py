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
from random import randint, sample, shuffle
import operator

FPS = 25

WINDOWWIDTH = 400
WINDOWHEIGHT = 600
BOXSIZE = 30
BOARDWIDTH = 10
BOARDHEIGHT = 16
XMARGIN = 50 # (WINDOWWIDTH - (BOARDWIDTH * BOXSIZE))/2
TOPMARGIN = 50

class GameScene(object):
    def __init__(self):
        super(GameScene, self).__init__()
        self.game_over = False
        self.board = Board()

    def render(self, screen):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def handle_events(self, events):
        raise NotImplementedError

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
    def __init__(self, possible_random_spaces):

        self.board = []

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
    EARTHIMAGE, EARTHRECT, MINER1IMAGE, MINER1RECT, MINER2IMAGE, MINER2RECTITLE,\
    TITLEIMAGE, TITLERECT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

    BGIMAGE, BGRECT = load_png('background.png')
    BOULDERIMAGE, BOULDERRECT = load_png('boulder.png')
    EARTHIMAGE, EARTHRECT = load_png('earth.png')
    MINER1IMAGE, MINER1RECT =load_png('miner_1.png')
    MINER2IMAGE, MINER2RECT =load_png('miner_2.png')
    TITLEIMAGE, TITLERECT = load_png('title.png')

    manager = SceneMananger()

    while True:
        checkForQuit()
        manager.scene.handle_events(pygame.event.get())
        manager.scene.update()
        manager.scene.render(DISPLAYSURF)
        FPSCLOCK.tick(FPS)

if __name__ == '__main__':
    main()
