import json

class Maze:
    def __init__(self, grid, start, exits):
        self.grid = grid  # True=стена
        self.start = start
        self.exits = exits

        self.height = len(grid)
        self.width = len(grid[0]) if self.height > 0 else 0

    def in_bounds(self, r, c):
        return 0 <= r < self.height and 0 <= c < self.width

    def is_free(self, r, c):
        return self.in_bounds(r, c) and not self.grid[r][c]

    def neighbors(self, r, c):
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r + dr, c + dc
            if self.is_free(nr, nc):
                yield (nr, nc)

    @classmethod
    def load_from_file(cls, filepath):
        with open(filepath) as f:
            data = json.load(f)
        grid = [[False]*data['width'] for _ in range(data['height'])]
        for (r, c) in data['walls']:
            grid[r][c] = True
        return cls(grid, tuple(data['start']), [tuple(e) for e in data['exits']])
