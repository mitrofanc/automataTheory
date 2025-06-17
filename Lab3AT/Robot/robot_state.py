DIRECTIONS = ['N', 'E', 'S', 'W']
DELTA = {'N': (-1, 0), 'E': (0, 1), 'S': (1, 0), 'W': (0, -1)}

class RobotState:
    def __init__(self, maze_grid, start=(0, 0), facing='N', hysteresis=30):
        self.maze = maze_grid
        self.r, self.c = start
        self.facing = facing
        self.mood = 0
        self.panic_counter = 0
        self.hysteresis = hysteresis
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
            self.panic_counter = 0
            return True
        self.panic_counter += 1
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
            self.mood += 1
        return env

    def check_panic(self):
        if self.panic_counter > self.hysteresis:
            from interpreter import RuntimeErrorRobot
            raise RuntimeErrorRobot("PANIC: робот слишком долго не может продвинуться!")

    def __repr__(self):
        return f'<Robot r={self.r} c={self.c} dir={self.facing}>'

    @property
    def at_exit(self) -> bool:
        """
        True, если текущие координаты совпадают
        хотя бы с одной точкой списка self.maze.exits
        (labyrinth.json хранит выходы).
        """
        return [self.r, self.c] in getattr(self.maze, "exits", [])