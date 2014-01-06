import random
import time
import pygame
from pygame import *

COLORS = [ pygame.Color("red"),
           pygame.Color("yellow"),
           pygame.Color("white"),
           pygame.Color("pink"),
           pygame.Color("blue"),
           pygame.Color("green") ]

COLOR_KEYS = [ 'r', 'y', 'w', 'p', 'b', 'g' ]

SCREEN_X  = 480  # 480  adjust aspect ratio
SCREEN_Y  = 480
GRID_SIZE = 14
BLOCK_X   = 0
BLOCK_Y   = 0
Y_BORDER  = 30   # Reserved pixel space for remaining turn display.
game      = None

# ------------------------------------------------------------------------------
class Drench(object):

    def __init__(self, tries = 30, grid_size = 14):
        global GRID_SIZE, BLOCK_X, BLOCK_Y
        pygame.init()
        pygame.display.set_mode((SCREEN_X, SCREEN_Y), 0, 24)
        self.DISPLAY    = pygame.display.get_surface()
        GRID_SIZE       = grid_size
        BLOCK_X         = int(SCREEN_X/grid_size)
        BLOCK_Y         = int((SCREEN_Y - Y_BORDER)/grid_size)
        self.tries      = tries
        self.color_grid = [[0 for i in range(GRID_SIZE)] for j in range(GRID_SIZE)]
        self.reset_color_done()

    def reset_color_done(self):
        self.color_done = [[False for i in range(GRID_SIZE)] for j in range(GRID_SIZE)]

    def setup(self):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                self.color_grid[row][col] = random.randrange(0, len(COLORS))
        self.redraw()

    def redraw(self):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x, y = BLOCK_X*col, BLOCK_Y*row,
                w, h = BLOCK_X, BLOCK_Y
                self.draw_block(COLORS[self.color_grid[row][col]], pygame.Rect((x,y+Y_BORDER), (w, h)), 0)
        pygame.display.update()

    def draw_block(self, color, rect, line_width):
        pygame.draw.rect(self.DISPLAY, color, rect, line_width)

    def drench_next(self, row, col, old_color, new_color):
        if row < 0 or col < 0 or row >= GRID_SIZE or col >= GRID_SIZE or self.color_done[row][col]:
            return
        self.color_done[row][col] = True
        if self.color_grid[row][col] == old_color:
            self.color_grid[row][col] = new_color
            self.drench_next(row+0, col+1, old_color, new_color)
            self.drench_next(row+0, col-1, old_color, new_color)
            self.drench_next(row+1, col+0, old_color, new_color)
            self.drench_next(row-1, col+0, old_color, new_color)

    def drench(self, key):
        print "DRENCH!  key=<%s>  tries=<%d>" % (key, self.tries)
        try:
            new_color = COLOR_KEYS.index(key)
        except:
            print 'Key not valid: %s -- expected %s' % (key, str(COLOR_KEYS))
            return
        old_color = self.color_grid[0][0]
        if old_color == new_color:
            print 'Color already applied. Choose a new one.'
            return
        self.drench_next(0, 0, old_color, new_color)
        self.reset_color_done()
        self.tries -= 1
        self.redraw()

    def check_win(self):
        first_color = self.color_grid[0][0]
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.color_grid[row][col] != first_color:
                    return False
        return True
# ------------------------------------------------------------------------------
def start():
    global game, game_done
    game_done = False
    game = Drench()
    game.setup()
# ------------------------------------------------------------------------------
start()
while True:
    event = pygame.event.wait()
    if event.type == QUIT:
        break
    elif event.type == KEYDOWN:
        try:
            key = chr(event.key)
        except:
            continue
        if key == 'z':
            start()
        elif not game_done:
            game.drench(key)
            if game.check_win():
                print 'YOU WIN with %d tries left!!' % game.tries
                game_done = True
            elif game.tries < 1:
                print 'YOU LOSE'
                game_done = True
        else:
            print 'Game is done, press "z" to restart.'
    #elif event.type == MOUSEBUTTONUP:
    #    print event.pos

