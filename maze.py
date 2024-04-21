from enum import IntEnum
import random
from tkinter import Tk, BOTH, Canvas
import time

class Window:
  def __init__(self, width, height):
    self.width = width
    self.height = height
    self.root = Tk()
    self.root.title = "Maze Solver"
    self.canvas = Canvas(width=width, height=height)
    self.canvas.pack()
    self.running = False
    
    self.root.protocol("WM_DELETE_WINDOW", self.close)
    
  def redraw(self):
    self.root.update_idletasks()
    self.root.update()
    
  def wait_for_close(self):
    self.running = True
    while self.running:
      self.redraw()
  
  def close(self):
    self.running = False
  
  def draw_line(self, line, fill):
    line.draw(self.canvas, fill)
    
  def draw_cell(self, cell):
    cell.draw()

class Point:
  def __init__(self, x, y):
    self.x = x
    self.y = y

class Line:
  def __init__(self, a, b):
    self.a = a
    self.b = b
  
  def draw(self, canvas, fill):
    canvas.create_line(
      self.a.x, self.a.y, self.b.x, self.b.y, fill=fill, width=2
    )
    canvas.pack()

class CellWalls(IntEnum):
  LEFT = 0,
  RIGHT = 1,
  TOP = 2,
  BOTTOM = 3

# Going down ->

class Cell:
  def __init__(self, x1, y1, x2, y2, win=None):
    self.walls = [True, True, True, True]
    self.lines = [
      Line(Point(x1, y1), Point(x1, y2)), # left
      Line(Point(x2, y1), Point(x2, y2)), # right
      Line(Point(x1, y1), Point(x2, y1)), # top
      Line(Point(x1, y2), Point(x2, y2)) # bottom
    ]
    self.x1 = x1
    self.y1 = y1
    self.x2 = x2
    self.y2 = y2
    self.win = win
    self.visited = False
    
  def draw(self):
    if self.win is not None:
      for i in range(0, 4):
        if self.walls[i]:
          self.lines[i].draw(self.win.canvas, "black")
        else:
          self.lines[i].draw(self.win.canvas, "white")
  
  def center(self):
    return Point((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)
  
  def draw_move(self, to_cell, undo=False):
    fill = "red"
    if undo:
      fill = "black"
    self.win.draw_line(Line(self.center(), to_cell.center()), fill)

class Maze:
  def __init__(self, x1, y1, num_rows, num_cols, cell_size_x, cell_size_y, win=None, seed=None):
    self.x1 = x1
    self.y1 = y1
    self.num_rows = num_rows
    self.num_cols = num_cols
    self.cell_size_x = cell_size_x
    self.cell_size_y = cell_size_y
    self.win = win
    self._create_cells()
    if seed is not None:
      random.seed(seed)
  
  def _create_cells(self):
    self.cells = []
    for i in range(0, self.num_rows):
      row = []
      for j in range(0, self.num_cols):
        cell_x = self.x1 + (i * self.cell_size_x)
        cell_y = self.y1 + (j * self.cell_size_y)
        row.append(Cell(cell_x, cell_y, cell_x + self.cell_size_x, cell_y + self.cell_size_y, self.win))
      self.cells.append(row)
    
    self._break_walls_r(0, 0)
    
    self._break_entrance_and_exit()
    
    for i in range(0, self.num_rows):
      for j in range(0, self.num_cols):
        cell = self.cells[i][j]
        cell.visited = False
        self._draw_cell(i, j)
    self._animate()
  
  def _draw_cell(self, i, j):
    cell = self.cells[i][j]
    cell.draw()
  
  def _animate(self):
    if self.win is not None:
      self.win.redraw()
      time.sleep(0.1)
      
  def _break_entrance_and_exit(self):
    top_left = self.cells[0][0]
    bottom_right = self.cells[self.num_rows - 1][self.num_cols - 1]
    top_left.walls[CellWalls.TOP] = False
    bottom_right.walls[CellWalls.BOTTOM] = False
    
  def _break_walls_r(self, i, j):
    from_cell = self.cells[i][j]
    if from_cell.visited:
      return
    # Keep visiting unvisited nodes
    while True:
      from_cell.visited = True
      directions = [
        (-1, 0, CellWalls.RIGHT), (1, 0, CellWalls.LEFT), 
        (0, -1, CellWalls.BOTTOM), (0, 1, CellWalls.TOP)]
      possible_directions = []
      w = self.num_rows
      h = self.num_cols
      for c in range(0, len(directions)):
        dir = directions[c]
        to = (i + dir[0], j + dir[1])
        if to[0] >= 0 and to[0] < w and to[1] >= 0 and to[1] < h:
          to_cell = self.cells[to[0]][to[1]]
          if not to_cell.visited:
            possible_directions.append((to_cell, to[0], to[1], dir[2]))

      if len(possible_directions) == 0:
        return
      
      move_to_dir = random.randrange(0, len(possible_directions))
      next_dir = possible_directions[move_to_dir]
      next_cell, next_i, next_j, opposite_wall = next_dir
      target_wall = None
      if opposite_wall == CellWalls.BOTTOM:
        target_wall = CellWalls.TOP
      elif opposite_wall == CellWalls.TOP:
        target_wall = CellWalls.BOTTOM
      elif opposite_wall == CellWalls.LEFT:
        target_wall = CellWalls.RIGHT
      elif opposite_wall == CellWalls.RIGHT:
        target_wall = CellWalls.LEFT
      from_cell.walls[target_wall] = False
      next_cell.walls[opposite_wall] = False
      self._break_walls_r(next_i, next_j)

  def solve(self):
    curr_cell = self.cells[0][0]
    enter_line = Line(Point(curr_cell.x1 + 25, curr_cell.y1 + 25), Point(curr_cell.x1 + 25, curr_cell.y1 - 25))
    enter_line.draw(self.win.canvas, "red")
    return self._solve_r(0, 0)

  def _solve_r(self, i, j):
    curr_cell = self.cells[i][j]
    self._animate()
    if curr_cell.visited:
      return False
    if i == len(self.cells) - 1 and j == len(self.cells[0]) - 1:
      exit_line = Line(Point(curr_cell.x1 + 25, curr_cell.y1 + 25), Point(curr_cell.x1 + 25, curr_cell.y1 + 75))
      exit_line.draw(self.win.canvas, "red")
      return True
    curr_cell.visited = True
    
    directions = [
        (-1, 0), (1, 0), 
        (0, -1), (0, 1),
      ]
    w = self.num_rows
    h = self.num_cols
    for c in range(0, len(directions)):
      dir = directions[c]
      to = (i + dir[0], j + dir[1])
      if to[0] >= 0 and to[0] < w and to[1] >= 0 and to[1] < h:
        to_cell = self.cells[to[0]][to[1]]
        if not to_cell.visited and not curr_cell.walls[c]:
          curr_cell.draw_move(to_cell)
          solved = self._solve_r(to[0], to[1])
          if not solved:
            curr_cell.draw_move(to_cell, True)
          else:
            return True
    return False
    