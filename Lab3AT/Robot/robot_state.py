# robot_state.py
# ------------------------------------------------------------
#  Хранит текущее положение робота и умеет двигаться / крутиться
#  Метод get_environment() возвращает 3 × 3 × 2 булев массив:
#    слой 0 – стены вокруг робота   (True = стена)
#    слой 1 – информация о выходе   (True = робот стоит на выходе)
#  Индексы предназначены для вашего языка (1-based):
#    env[2,2,*] – позиция робота
#    env[1,2,1] – «спереди», env[2,1,1] – «слева» и т.д.
# ------------------------------------------------------------

DIRECTIONS = ['N', 'E', 'S', 'W']                  # индексы 0-3
DELTA = {                                          # смещение (dr, dc)
    'N': (-1, 0),
    'E': (0, 1),
    'S': (1, 0),
    'W': (0, -1),
}

class RobotState:
    def __init__(self, maze_grid, start=(0, 0), facing='N'):
        """
        maze_grid  – 2-d список: True = стена, False = проход
        start      – (row, col) начальная клетка
        facing     – 'N' | 'E' | 'S' | 'W'
        """
        self.maze     = maze_grid
        self.r, self.c = start
        self.facing   = facing
        self.visited  = {start}

    # --------------------------------------------------------
    #   внутренние проверки
    # --------------------------------------------------------
    def _inside(self, r, c):
        return 0 <= r < len(self.maze) and 0 <= c < len(self.maze[0])

    def _free(self, r, c):
        return self._inside(r, c) and not self.maze[r][c]          # False -- проход

    # --------------------------------------------------------
    #   физические действия
    # --------------------------------------------------------
    def move(self):
        dr, dc = DELTA[self.facing]
        nr, nc = self.r + dr, self.c + dc
        if self._free(nr, nc):                                     # впереди свободно
            self.r, self.c = nr, nc
            self.visited.add((nr, nc))
            return True
        return False                                               # упёрся в стену

    def rotate_left(self):
        idx = DIRECTIONS.index(self.facing)
        self.facing = DIRECTIONS[(idx - 1) % 4]

    def rotate_right(self):
        idx = DIRECTIONS.index(self.facing)
        self.facing = DIRECTIONS[(idx + 1) % 4]

    # --------------------------------------------------------
    #   сенсорное окружение
    # --------------------------------------------------------
    def get_environment(self):
        size = 3
        env = [[[False for _ in range(2)]            # слой-0 и слой-1
                for _ in range(size)] for _ in range(size)]

        # ---------- слой 0: стены (оставляем как был) ----------
        idx = DIRECTIONS.index(self.facing)
        dirs = {'front': DIRECTIONS[idx],
                'left' : DIRECTIONS[(idx - 1) % 4],
                'right': DIRECTIONS[(idx + 1) % 4],
                'back' : DIRECTIONS[(idx + 2) % 4]}
        positions = {'front': (0, 1), 'left': (1, 0),
                     'right': (1, 2), 'back': (2, 1)}
        for key, face in dirs.items():
            dr, dc = DELTA[face]
            r, c   = self.r + dr, self.c + dc
            row, col = positions[key]
            env[row][col][0] = not self._free(r, c)

        # ---------- слой 1: выход ----------
        env[1][1][1] = self.at_exit          # центр матрицы

        return env

    # --------------------------------------------------------
    #   свойство-флаг «робот достиг выхода»
    # --------------------------------------------------------
    # RobotState.robot_state.py
    @property
    def at_exit(self) -> bool:
        """True, если текущая клетка входит в список maze.exits"""
        return (self.r, self.c) in getattr(self.maze, "exits", [])