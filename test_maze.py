import unittest

from maze import Maze

class TestMaze(unittest.TestCase):
    def test_number_of_cells(self):
        maze = Maze(100, 100, 10, 5, 50, 50, None, 0)
        self.assertEqual(len(maze.cells), 10)
        self.assertEqual(len(maze.cells[0]), 5)

if __name__ == "__main__":
    unittest.main()