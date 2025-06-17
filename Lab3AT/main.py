# main.py

import os
import sys
import time
import pygame

from Robot.maze          import Maze
from Robot.robot_state   import RobotState
from Robot.visualization import draw_maze
from interpreter         import Interpreter, RuntimeErrorRobot

# Размер одной клетки в пикселях
TILE = 32

def main() -> None:
    pygame.init()

    # ---------- загрузка лабиринта -----------------------------------
    base_dir = os.path.dirname(__file__)
    maze_path = os.path.join(base_dir, "examples", "maze2.json")
    maze = Maze.load_from_file(maze_path)

    # Окно нужного размера
    screen = pygame.display.set_mode(
        (maze.width * TILE, maze.height * TILE)
    )
    pygame.display.set_caption("Клеточный робот")

    # ---------- состояние робота -------------------------------------
    # ПЕРЕДАЁМ maze.grid, а не сам объект Maze
    robot = RobotState(maze.grid, maze.start)

    # ---------- колбэк после каждого шага ----------------------------
    def after_step(state: RobotState) -> None:
        # Без этой помпы окно «замрёт» на некоторых платформах
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((255, 255, 255))
        # draw_maze принимает параметры позиционно:
        # (screen, maze, visited, current_pos, tile_size)
        draw_maze(
            screen,
            maze,
            state.visited,
            (state.r, state.c),
            TILE
        )
        pygame.display.flip()
        time.sleep(0.10)

    # ---------- читаем программу на нашем языке ----------------------
    prog_path = os.path.join(base_dir, "examples", "find_exit.txt")
    with open(prog_path, encoding="utf-8") as f:
        source = f.read()

    # ---------- создаём интерпретатор и передаём ему колбэк ------------
    interpreter = Interpreter(source, robot, maze, after_step=after_step)

    # ---------- запускаем и ловим ошибки -----------------------------
    try:
        interpreter.run()
        print("Программа завершена.")
    except RuntimeErrorRobot as e:
        print("Ошибка выполнения:", e)

    # ---------- после окончания ждём, пока пользователь закроет окно ---
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        time.sleep(0.05)

if __name__ == "__main__":
    main()
