import pygame
from Robot.maze import Maze
from Robot.robot_state import RobotState
from Robot.visualization import draw_maze
from interpreter import Interpreter

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))

    maze = Maze.load_from_file('examples/maze.json')
    robot = RobotState(maze.grid, maze.start)

    with open('examples/program.txt') as f:
        source_code = f.read()

    interpreter = Interpreter(source_code, robot, maze)

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        try:
            has_more = interpreter.step()
        except RuntimeError as e:
            print("Ошибка исполнения:", e)
            running = False

        screen.fill((255, 255, 255))
        draw_maze(screen, maze, interpreter.findexit_path, (robot.r, robot.c))
        pygame.display.flip()

        if not has_more:
            print("Программа выполнена")
            running = False

        clock.tick(5)

    pygame.quit()

if __name__ == "__main__":
    main()
