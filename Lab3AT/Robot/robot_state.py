DIRECTIONS = ['N', 'E', 'S', 'W']
DELTA = {'N': (-1, 0), 'E': (0, 1), 'S': (1, 0), 'W': (0, -1)}

class RobotState:
    def __init__(self, maze_grid, start=(0, 0), facing='N'):
        self.maze = maze_grid
        self.r, self.c = start
        self.facing = facing
        self.visited = {start}

    def _inside(self, r, c):
        return 0 <= r < len(self.maze) and 0 <= c < len(self.maze[0])

    def _free(self, r, c):
        return self._inside(r, c) and not self.maze[r][c]

    def move(self):
        dr, dc = DELTA[self.facing]
        nr, nc = self.r + dr, self.c + dc
        if self._free(nr, nc):
            self.r, self.c = nr, nc
            self.visited.add((nr, nc))
            return True
        return False

    def rotate_left(self):
        idx = DIRECTIONS.index(self.facing)
        self.facing = DIRECTIONS[(idx - 1) % 4]

    def rotate_right(self):
        idx = DIRECTIONS.index(self.facing)
        self.facing = DIRECTIONS[(idx + 1) % 4]

    def get_environment(self):
        size = 3
        env = [[[False]*size for _ in range(size)] for _ in range(size)]
        dr, dc = DELTA[self.facing]
        fr, fc = self.r + dr, self.c + dc
        if not self._free(fr, fc):
            env[0][1][1] = True
        if self.r in (0, len(self.maze)-1) or self.c in (0, len(self.maze[0])-1):
            env[2][1][1] = True
        return env

    @property
    def at_exit(self) -> bool:
        return [self.r, self.c] in getattr(self.maze, "exits", [])