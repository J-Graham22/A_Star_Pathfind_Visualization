#imports
from _ast import Lambda

import pygame
import math
from queue import PriorityQueue

#window set up
STD_WIDTH = 1000
WIN = pygame.display.set_mode((STD_WIDTH, STD_WIDTH))
pygame.display.set_caption("A* Visualizer")

#Colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
CYAN = (64, 224, 208)

class Square:
    def __init__(self, row, col, width, row_num):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = BLACK
        self.neighbors = []
        self.width = width
        self.row_num = row_num

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_wall(self):
        return self.color == WHITE

    def is_start(self):
        return self.color == ORANGE

    def is_goal(self):
        return self.color == CYAN

    def restart(self):
        self.color = BLACK

    def make_start(self):
        self.color = ORANGE

    def close(self):
        self.color = RED

    def open(self):
        self.color = GREEN

    def build_wall(self):
        self.color = WHITE

    def make_end(self):
        self.color = CYAN

    def find_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_adjacent(self, grid):
        self.adjacent = []
        if self.row < self.row_num - 1 and not grid[self.row + 1][self.col].is_wall(): #DOWN
            self.adjacent.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_wall(): #UP
            self.adjacent.append(grid[self.row - 1][self.col])

        if self.col < self.row_num - 1 and not grid[self.row][self.col + 1].is_wall(): #RIGHT
            self.adjacent.append(grid[self.row][self.col + 1])

        if self.row > 0 and not grid[self.row][self.col - 1].is_wall(): #LEFT
            self.adjacent.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False

def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def build_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            square = Square(i, j, gap, rows)
            grid[i].append(square)

    return grid

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

def draw(win, grid, rows, width):
    win.fill(BLACK)

    for row in grid:
        for square in row:
            square.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap
    return row, col

def display_path(source, current, win, grid, rows, width):
    while current in source:
        current = source[current]
        current.find_path()
        draw(win, grid, rows, width)

def algorithm(win, rows, width, grid, start, goal):
    count = 0
    open_list = PriorityQueue()
    open_list.put((0, count, start))
    source = {}
    g_score = {square: float("inf") for row in grid for square in row}
    g_score[start] = 0
    f_score = {square: float("inf") for row in grid for square in row}
    f_score[start] = h(start.get_pos(), goal.get_pos())

    hash_open_list = {start}

    while not open_list.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_list.get()[2]
        hash_open_list.remove(current)

        if current == goal:
            display_path(source, goal, win, grid, rows, width)
            start.make_start()
            goal.make_end()
            return True
        for adjacent in current.adjacent:
            hold_g_score = g_score[current] + 1

            if hold_g_score < g_score[adjacent]:
                source[adjacent] = current
                g_score[adjacent] = hold_g_score
                f_score[adjacent] = hold_g_score + h(adjacent.get_pos(), goal.get_pos())
                if adjacent not in hash_open_list:
                    count += 1
                    open_list.put((f_score[adjacent], count, adjacent))
                    hash_open_list.add(adjacent)
                    adjacent.open()

        draw(win, grid, rows, width)

        if current != start:
            current.close()

    return False



def main(win, width):
    ROWS = 50
    grid = build_grid(ROWS, width)

    start = None
    goal = None

    run = True
    started = False
    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]: #Left click
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                square = grid[row][col]
                if not start and square != goal:
                    start = square
                    start.make_start()
                elif not goal and square != start:
                    goal = square
                    goal.make_end()
                elif square != goal and square != start:
                    square.build_wall()

            elif pygame.mouse.get_pressed()[2]: #Right click
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                square = grid[row][col]
                square.restart()
                if square == start:
                    start = None
                if square == goal:
                    goal = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and goal:
                    for row in grid:
                        for square in row:
                            square.update_adjacent(grid)
                    algorithm(win, ROWS, width, grid, start, goal)

                if event.key == pygame.K_r:
                    start = None
                    goal = None
                    grid = build_grid(ROWS, width)

    pygame.quit()

main(WIN, STD_WIDTH)
