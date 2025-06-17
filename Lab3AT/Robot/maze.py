import json

class Maze:
    def __init__(self, grid, start, exits):
        self.grid = grid  # True=стена
        self.start = start
        self.exits = exits
        self.height = len(grid)
        self.width = len(grid[0]) if self.height > 0 else 0

    @classmethod
    def load_from_file(cls, filepath):
        with open(filepath) as f:
            data = json.load(f)
        grid = [[False]*data['width'] for _ in range(data['height'])]
        for (r, c) in data['walls']:
            grid[r][c] = True
        return cls(grid, tuple(data['start']), [tuple(e) for e in data['exits']])
