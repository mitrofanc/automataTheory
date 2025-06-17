import os
import sys
import time
import pygame
from Robot.maze import Maze
from Robot.robot_state import RobotState
from Robot.visualization import draw_maze
from interpreter import Interpreter, RuntimeErrorRobot

TILE = 45

def main() -> None:
    pygame.init()

    base_dir = os.path.dirname(__file__)
    maze_path = os.path.join(base_dir, "examples", "maze2.json")
    maze = Maze.load_from_file(maze_path)

    screen = pygame.display.set_mode((maze.width * TILE, maze.height * TILE))
    pygame.display.set_caption("Robot")
    robot = RobotState(maze.grid, maze.start)

    def after_step(state: RobotState) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((255, 255, 255))
        draw_maze(
            screen,
            maze,
            state.visited,
            (state.r, state.c),
            TILE
        )
        pygame.display.flip()
        time.sleep(0.10)

    prog_path = os.path.join(base_dir, "examples", "find_exit.txt")
    with open(prog_path, encoding="utf-8") as f:
        source = f.read()

    interpreter = Interpreter(source, robot, maze, after_step=after_step)

    try:
        interpreter.run()
        print("Программа завершена.")
    except RuntimeErrorRobot as e:
        print("Ошибка выполнения:", e)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        time.sleep(0.05)

if __name__ == "__main__":
    main()
