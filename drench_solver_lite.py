import copy
import random
import time
import msvcrt

GRID_SIZE   = 14
GRID2_SIZE  = GRID_SIZE * GRID_SIZE
NUM_COLORS  = 6
game        = None
CALL_COUNT  = 0

# ------------------------------------------------------------------------------
class Drench(object):

    def __init__(self, tries = 30, grid_size = 14):
        global GRID_SIZE, GRID2_SIZE
        GRID_SIZE  = grid_size
        GRID2_SIZE = grid_size * grid_size
        self.steps = 0
        self.color_grid = [[0 for i in range(GRID_SIZE)] for j in range(GRID_SIZE)]
        self.color_done = self.new_color_done()

    def new_color_done(self):
        return [[0 for i in range(GRID_SIZE)] for j in range(GRID_SIZE)]

    def setup(self):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                self.color_grid[row][col] = random.randrange(0, NUM_COLORS)
        self.redraw(self.color_grid)

    def redraw(self, color_grid):
        out = ''
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                out += str(color_grid[row][col])
            out += "\n"
        print out
        print '---------------------------------------------'
        print '  Steps <%d>  Score <%d>' % (self.steps, self.check_score(color_grid))
        print '  Border: %s' % self.check_border(color_grid)
        print '  First:  %d' % self.first_border(color_grid)
        print '---------------------------------------------'

    def drench_fast(self, row, col, old_color, new_color, color_grid, color_done):
        #print '    drench_fast [%2d][%2d]  %d -> %d' % (row, col, old_color, new_color)
        color_done[row][col] = 1
        curr_color = color_grid[row][col]
        if curr_color == old_color:
            score = 1
            color_grid[row][col] = new_color
            if col < GRID_SIZE-1 and not color_done[row][col+1]:
                score += self.drench_fast(row, col+1, old_color, new_color, color_grid, color_done)
            if col > 0 and not color_done[row][col-1]:
                score += self.drench_fast(row, col-1, old_color, new_color, color_grid, color_done)
            if row < GRID_SIZE-1 and not color_done[row+1][col]:
                score += self.drench_fast(row+1, col, old_color, new_color, color_grid, color_done)
            if row > 0 and not color_done[row-1][col]:
                score += self.drench_fast(row-1, col, old_color, new_color, color_grid, color_done)
        else:
            score = 1 if curr_color == new_color else 0
        return score

    def drench_color(self, new_color, color_grid, color_done):
        return self.drench_fast(0, 0, color_grid[0][0], new_color, color_grid, color_done)

    def drench(self, key):
        new_color = key - ord('0')
        if new_color not in range(NUM_COLORS):
            return -1
        if new_color == self.color_grid[0][0]:
            print 'Color already applied. Choose a new one.'
            return -1
        self.color_done = self.new_color_done()
        score = self.drench_color(new_color, self.color_grid, self.color_done)
        self.steps += 1
        self.redraw(self.color_grid)
        return score

    def score_fast(self, row, col, check_color, color_grid, color_done):
        color_done[row][col] = 1
        if check_color == color_grid[row][col]:
            score = 1
            if col < GRID_SIZE-1 and not color_done[row][col+1]:
                score += self.score_fast(row, col+1, check_color, color_grid, color_done)
            if col > 0 and not color_done[row][col-1]:
                score += self.score_fast(row, col-1, check_color, color_grid, color_done)
            if row < GRID_SIZE-1 and not color_done[row+1][col]:
                score += self.score_fast(row+1, col, check_color, color_grid, color_done)
            if row > 0 and not color_done[row-1][col]:
                score += self.score_fast(row-1, col, check_color, color_grid, color_done)
        else:
            score = 0
        return score

    def check_score(self, color_grid):
        return self.score_fast(0, 0, color_grid[0][0], color_grid, self.new_color_done())

    def check_win(self, color_grid):
        # Also valid -- but slower --
        #     win = (self.check_score(color_grid) == GRID2_SIZE)
        return (self.first_border(color_grid) == -1)
# ------------------------------------------------------------------------------
# Solver
# ------------------------------------------------------------------------------
    def border_fast(self, row, col, check_color, border_colors, color_grid, color_done):
        #print '    border_fast [%2d][%2d]  check %d' % (row, col, check_color)
        color_done[row][col] = 1
        color = color_grid[row][col]
        if check_color != color:
            if color not in border_colors:
                border_colors.append(color)
        else:
            if col < GRID_SIZE-1 and not color_done[row][col+1]:
                self.border_fast(row, col+1, check_color, border_colors, color_grid, color_done)
            if col > 0 and not color_done[row][col-1]:
                self.border_fast(row, col-1, check_color, border_colors, color_grid, color_done)
            if row < GRID_SIZE-1 and not color_done[row+1][col]:
                self.border_fast(row+1, col, check_color, border_colors, color_grid, color_done)
            if row > 0 and not color_done[row-1][col]:
                self.border_fast(row-1, col, check_color, border_colors, color_grid, color_done)

    def border_next(self, row, col, check_color, border_colors, color_grid, color_done):
        if row < 0 or col < 0 or row >= GRID_SIZE or col >= GRID_SIZE or color_done[row][col]:
            return
        color_done[row][col] = 1
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
        self.border_fast(0, 0, check_color, border_colors, color_grid, color_done)
        #self.border_next(0, 0, check_color, border_colors, color_grid, color_done)
        return border_colors

    def first_border(self, color_grid):
        color = color_grid[0][0]
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                next_color = color_grid[row][col]
                if (next_color != color):
                    return next_color
        return -1

    def dumb_solver(self, color_grid, quit_score=999):
        colors = []
        while True:
            color = self.first_border(color_grid)
            if color == -1:
                break
            colors.append(color)
            color_done = self.new_color_done()
            score = self.drench_color(color, color_grid, color_done)
            win   = 1 if score == GRID2_SIZE else 0
            print '  dumb - color <%d> score <%d> win <%d>' % (color, score, win)
            if score >= quit_score:
                break
        return colors

    def side_solver(self, do_col, color_grid, moves):
        curr_color = color_grid[0][0]
        row, col, col_inc, row_inc = (0,0,1,0) if do_col else (0,0,0,1)
        while row < GRID_SIZE and col < GRID_SIZE:
            next_color = color_grid[row][col]
            row += row_inc
            col += col_inc
            if next_color != curr_color:
                moves.append(next_color)
                score      = self.drench_color(next_color, color_grid, self.new_color_done())
                curr_color = next_color
                win        = self.check_win(color_grid)
                print '  side - color <%d> score <%d> win <%d>' % (next_color, score, win)
        return moves

    def best_score_solver(self, max_depth, color_grid, moves, score=0):
        global CALL_COUNT
        CALL_COUNT += 1
        best_grid, best_moves, best_score = color_grid, moves, score
        if len(moves) < max_depth:
            border_colors = self.check_border(color_grid)
            #print 'Solver depth <%d> score <%d> border_colors <%s>' % (len(moves), score, border_colors)
            for c in border_colors:
                #print 'Solver depth <%d> score <%d> border <%s> moves <%s> next <%d>' % (len(moves), best_score, border_colors, moves, c)
                next_grid  = copy.deepcopy(color_grid)
                next_moves = moves + [c]
                next_score = self.drench_color(c, next_grid, self.new_color_done())
                if next_score == GRID2_SIZE:
                    return (999, next_moves, next_grid)
                next_best_score, next_best_moves, next_best_grid = self.best_score_solver(max_depth, next_grid, next_moves, next_score)
                if best_score < next_best_score:
                    best_score, best_moves, best_grid = next_best_score, next_best_moves, next_best_grid
                    #print '  new best score <%d>  %s' % (best_score, best_moves)
        #print '  return (%d,  %s)' % (best_score, best_moves)
        return (best_score, best_moves, best_grid)

    def near_corner_fast(self, row, col, check_color, color_grid, color_done):
        #print '    near_corner_fast [%2d][%2d]  check %d' % (row, col, check_color)
        color_done[row][col] = 1
        color = color_grid[row][col]
        if check_color != color:
            return 888
        else:
            dist = (GRID_SIZE - row) * (GRID_SIZE - row) + (GRID_SIZE - col) * (GRID_SIZE - col)
            if col < GRID_SIZE-1 and not color_done[row][col+1]:
                dist = min(dist, self.near_corner_fast(row, col+1, check_color, color_grid, color_done))
            if col > 0 and not color_done[row][col-1]:
                dist = min(dist, self.near_corner_fast(row, col-1, check_color, color_grid, color_done))
            if row < GRID_SIZE-1 and not color_done[row+1][col]:
                dist = min(dist, self.near_corner_fast(row+1, col, check_color, color_grid, color_done))
            if row > 0 and not color_done[row-1][col]:
                dist = min(dist, self.near_corner_fast(row-1, col, check_color, color_grid, color_done))
        return dist

    def near_corner_solver(self, max_depth, color_grid, moves, score=1111):
        global CALL_COUNT
        CALL_COUNT += 1
        best_grid, best_moves, best_score = color_grid, moves, score

        if len(moves) < max_depth:
            border_colors = self.check_border(color_grid)
            print 'Solver depth <%d> score <%d> border_colors <%s>' % (len(moves), score, border_colors)
            for c in border_colors:
                print 'Solver depth <%d> score <%d> border <%s> moves <%s> next <%d>' % (len(moves), best_score, border_colors, moves, c)
                next_grid  = copy.deepcopy(color_grid)
                next_moves = moves + [c]
                next_score = self.drench_color(c, next_grid, self.new_color_done())
                if next_score == GRID2_SIZE:
                    return (0, next_moves)
                # Swap the num-filled score with the near-dist score.
                next_score = self.near_corner_fast(0, 0, c, next_grid, self.new_color_done())
                print 'Solver next_moves <%s> near_score <%d>' % (next_moves, next_score)
                next_best_score, next_best_moves, next_best_grid = self.best_score_solver(max_depth, next_grid, next_moves, next_score)
                if best_score > next_best_score:
                    best_score, best_moves, best_grid = next_best_score, next_best_moves, next_best_grid
                    print '  new best score <%d>  %s' % (best_score, best_moves)
        print '  return (%d,  %s)' % (best_score, best_moves)
        return (best_score, best_moves, best_grid)

# ------------------------------------------------------------------------------
def debug_timing(sc, info):
    ec = time.clock()
    if sc > 0:
        print '                                         debug_timing: %7.5f .. %s' % (ec-sc, info)
    return ec
# ------------------------------------------------------------------------------
def start():
    global game, game_done
    game_done = False
    game = Drench()
    game.setup()
# ------------------------------------------------------------------------------
start()

#stdscr     = curses.initscr()
#curses.cbreak()
#stdscr.keypad(1)
#stdscr.addstr(0,10,"Hit [012345] or 'q' to quit")
#stdscr.refresh()
#
#key = ''
#while key != ord('q'):
#    key = stdscr.getch()
#    stdscr.addch(20,25,key)
#    stdscr.refresh()
#    if key == curses.KEY_UP:
#        stdscr.addstr(2, 20, "Up")
#    elif key == curses.KEY_DOWN:
#        stdscr.addstr(3, 20, "Down")
#curses.endwin()

print "Press [012345|ds] or 'q' to quit"
key = ''
while True:
    key = ord(msvcrt.getch())

    if key == ord('q'):
        break

    elif key == ord('d'):
        print 'Using DUMB solver:'
        temp_grid = copy.deepcopy(game.color_grid)
        colors    = game.dumb_solver(temp_grid)
        print '%d steps %s' % (len(colors), colors)

    elif key == ord('s'):
        print 'Using SIDE solvers:'

        temp_grid   = copy.deepcopy(game.color_grid)
        col_colors  = game.side_solver(True, temp_grid, [])
        col_colors += game.dumb_solver(temp_grid)
        print '    COL: %d steps %s' % (len(col_colors), col_colors)
        # Note: Col+Dumb is same as pure Dumb solver.

        temp_grid   = copy.deepcopy(game.color_grid)
        row_colors  = game.side_solver(False, temp_grid, [])
        row_colors += game.dumb_solver(temp_grid)
        print '    ROW: %d steps %s' % (len(row_colors), row_colors)

        temp_grid   = copy.deepcopy(game.color_grid)
        mix_colors  = game.side_solver(False, temp_grid, [])
        mix_colors += game.side_solver(True, temp_grid, [])
        mix_colors += game.dumb_solver(temp_grid)
        print '    MIX: %d steps %s' % (len(mix_colors), mix_colors)

    elif key == ord('n'):
###  Not yet working... somehow moves[] is dropping data even though same method works for 'best' ???
        temp_grid   = copy.deepcopy(game.color_grid)
        max_depth   = 2
        for i in range(2):   # Near # of iterations that is likely to yield solution.  5 works pretty well (may need 7 for guarantee?)
            CALL_COUNT  = 0
            score, moves, temp_grid = game.near_corner_solver(max_depth, temp_grid, [])
            print '    NEAR[%d]: %d steps %s calls %d' % (i, len(moves), moves, CALL_COUNT)
        game.redraw(temp_grid)

    elif key == ord('u'):
        print 'BEST-8 (u)ltra'
        sc = debug_timing(0, '')
        temp_grid   = copy.deepcopy(game.color_grid)
        max_depth   = 8
        for i in range(6):   # Near # of iterations that is likely to yield solution.  5 works pretty well (may need 7 for guarantee?)
            CALL_COUNT  = 0
            score, moves, temp_grid = game.best_score_solver(max_depth, temp_grid, [])
            print '    BEST[%d]: %d steps %s calls %d' % (i, len(moves), moves, CALL_COUNT)
        sc = debug_timing(sc, 'best-depth-8')
        game.redraw(temp_grid)

    elif key == ord('b'):
        print 'BEST-6 (b)est'
        sc = debug_timing(0, '')
        temp_grid   = copy.deepcopy(game.color_grid)
        max_depth   = 6
        for i in range(6):   # Near # of iterations that is likely to yield solution.  5 works pretty well (may need 7 for guarantee?)
            CALL_COUNT  = 0
            score, moves, temp_grid = game.best_score_solver(max_depth, temp_grid, [])
            print '    BEST[%d]: %d steps %s calls %d' % (i, len(moves), moves, CALL_COUNT)
        sc = debug_timing(sc, 'best-depth-6')
        game.redraw(temp_grid)

    elif key == ord('m'):

        print 'Using MIXED BEST SCORE (depth 6) solver:'
        temp_grid   = copy.deepcopy(game.color_grid)
        dumb_moves  = game.dumb_solver(temp_grid, GRID2_SIZE - 40)
        print '    DUMB: %d steps %s' % (len(dumb_moves), dumb_moves)
        game.redraw(temp_grid)
        CALL_COUNT = 0
        max_depth  = 6
        best_score, best_moves, temp_grid = game.best_score_solver(max_depth, temp_grid, [])
        print '    BEST: %d steps %s calls %d' % (len(best_moves), best_moves, CALL_COUNT)
        game.redraw(temp_grid)
        dumb_moves += best_moves  # Note: Best does not guarantee a WIN due to max_depth
        dumb_moves += game.dumb_solver(temp_grid)  # Ensure the final WIN
        print '    BEST* %d steps %s' % (len(dumb_moves), dumb_moves)

    else:
        score = game.drench(key)
