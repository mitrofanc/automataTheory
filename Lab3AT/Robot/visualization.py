import pygame

CELL_SIZE = 40

def draw_maze(screen, maze, path, robot_pos):
    for r in range(maze.height):
        for c in range(maze.width):
            color = (0, 0, 0) if maze.grid[r][c] else (255, 255, 255)
            rect = pygame.Rect(c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)

    if path:
        for (r, c) in path:
            rect = pygame.Rect(c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, (0, 255, 0), rect)

    r, c = robot_pos
    rect = pygame.Rect(c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, (255, 0, 0), rect)
