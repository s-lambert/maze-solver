from maze import Window, Maze

def main():
  win = Window(800, 800)
  maze = Maze(100, 100, 10, 5, 50, 50, win)
  maze.solve()
  win.wait_for_close()
  
if __name__ == "__main__":
  main()
