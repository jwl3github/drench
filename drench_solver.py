import copy
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
#               0    1    2    3    4    5
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

    def new_color_done(self):
        return [[False for i in range(GRID_SIZE)] for j in range(GRID_SIZE)]

    def setup(self):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                self.color_grid[row][col] = random.randrange(0, len(COLORS))
        self.redraw(self.color_grid)

    def redraw(self, color_grid):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x, y = BLOCK_X*col, BLOCK_Y*row,
                w, h = BLOCK_X, BLOCK_Y
                self.draw_block(COLORS[color_grid[row][col]], pygame.Rect((x,y+Y_BORDER), (w, h)), 0)
        pygame.display.update()

    def draw_block(self, color, rect, line_width):
        pygame.draw.rect(self.DISPLAY, color, rect, line_width)

    def drench_next(self, row, col, old_color, new_color, color_grid, color_done):
        if row < 0 or col < 0 or row >= GRID_SIZE or col >= GRID_SIZE or color_done[row][col]:
            return
        color_done[row][col] = True
        if color_grid[row][col] == old_color:
            color_grid[row][col] = new_color
            self.drench_next(row+0, col+1, old_color, new_color, color_grid, color_done)
            self.drench_next(row+0, col-1, old_color, new_color, color_grid, color_done)
            self.drench_next(row+1, col+0, old_color, new_color, color_grid, color_done)
            self.drench_next(row-1, col+0, old_color, new_color, color_grid, color_done)

    def drench_color(self, new_color, color_grid):
        old_color = color_grid[0][0]
        if old_color == new_color:
            print 'Color already applied. Choose a new one.'
            return
        self.drench_next(0, 0, old_color, new_color, color_grid, self.new_color_done())

    def drench(self, key, color_grid):
        try:
            color = COLOR_KEYS.index(key)
        except:
            print 'Key not valid: %s -- expected %s' % (key, str(COLOR_KEYS))
            return
        self.drench_color(color, color_grid)
        self.tries -= 1
        self.redraw(color_grid)

    def check_score(self, color_grid):
        score = 1
        first_color = color_grid[0][0]
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if color_grid[row][col] == first_color:
                    score += 1  # Kind of approximate since contiguous not checked.
        return score

    def check_win(self, color_grid):
        first_color = color_grid[0][0]
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if color_grid[row][col] != first_color:
                    return False
        return True
# ------------------------------------------------------------------------------
# Solver
# ------------------------------------------------------------------------------
    def border_next(self, row, col, check_color, border_colors, color_grid, color_done):
        if row < 0 or col < 0 or row >= GRID_SIZE or col >= GRID_SIZE or color_done[row][col]:
            return
        color_done[row][col] = True
        color = color_grid[row][col]
        if check_color != color:
            if color not in border_colors:
                border_colors.append(color)
        else:
            self.border_next(row+0, col+1, check_color, border_colors, color_grid, color_done)
            self.border_next(row+0, col-1, check_color, border_colors, color_grid, color_done)
            self.border_next(row+1, col+0, check_color, border_colors, color_grid, color_done)
            self.border_next(row-1, col+0, check_color, border_colors, color_grid, color_done)

    def check_border(self, color_grid):
        border_colors = []
        check_color   = color_grid[0][0]
        color_done    = self.new_color_done()
        self.border_next(0, 0, check_color, border_colors, color_grid, color_done)
        #print 'Border: %s' % border_colors
        return border_colors

    def recursive_solver(self, max_depth, color_grid, moves=[], score=0):
        depth = len(moves)
        if depth > max_depth:
            return (0,[])
        best_moves      = moves
        best_color_grid = color_grid
        best_score      = self.check_score(color_grid)
        border_colors   = self.check_border(color_grid)
        for c in border_colors:
            #print 'Solver depth <%d> score <%d> border <%s> moves <%s> next <%d>' % (depth, best_score, border_colors, moves, c)
            next_color_grid = copy.deepcopy(color_grid)
            next_moves      = copy.deepcopy(moves)
            next_moves.append(c)
            self.drench_color(c, next_color_grid)
            if self.check_win(next_color_grid):
                return (999, next_moves)
            else:
                next_score, next_best_moves = self.recursive_solver(max_depth, next_color_grid, next_moves, best_score)
                if best_score < next_score:
                    best_score, best_moves = next_score, next_best_moves
                    #print '  new best score <%d>  %s' % (best_score, best_moves)
        return (best_score, best_moves)

    def side_solver(self, do_col, color_grid, moves=[]):
        curr_color = color_grid[0][0]
        if do_col:
            row, col, col_inc, row_inc = 0, 0, 1, 0
        else:
            row, col, col_inc, row_inc = 0, 0, 0, 1
        while row < GRID_SIZE and col < GRID_SIZE:
            next_color = color_grid[row][col]
            row += row_inc
            col += col_inc
            if next_color != curr_color:
                moves.append(next_color)
                self.drench_color(next_color, color_grid)
                curr_color = next_color
        return moves
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
        elif key == 'q':
            game.check_border()
        elif key == 'x':
            print 'Solver...'
            print 'Final best moves:'
            grid = copy.deepcopy(game.color_grid)
            col_moves = game.side_solver(True, grid)
            #print [COLOR_KEYS[m] for m in col_moves]
            row_moves = game.side_solver(False, grid)
            print [COLOR_KEYS[m] for m in row_moves]
            score, end_moves = game.recursive_solver(6, grid)
            print [COLOR_KEYS[m] for m in end_moves]
        elif not game_done:
            print "DRENCH!  key=<%s>  tries=<%d>" % (key, game.tries)
            game.drench(key, game.color_grid)
            if game.check_win(game.color_grid):
                print 'YOU WIN with %d tries left!!' % game.tries
                game_done = True
            elif game.tries < 1:
                print 'YOU LOSE'
                game_done = True
        else:
            print 'Game is done, press "z" to restart.'
    #elif event.type == MOUSEBUTTONUP:
    #    print event.pos

