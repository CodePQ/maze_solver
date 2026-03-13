import pygame
import random

# -------------------------
# Settings
# -------------------------
WIDTH, HEIGHT = 600, 600
ROWS, COLS = 25, 25
SHIFT = 10
CELL_SIZE = (WIDTH - 1) // COLS

BG_COLOR = (20, 20, 20)
WALL_COLOR = (240, 240, 240)
VISITED_COLOR = (60, 140, 255)
CURRENT_COLOR = (255, 180, 60)
START_COLOR = (0, 255, 0)
END_COLOR = (255, 0, 0)

FPS = 60


# -------------------------
# Cell class
# -------------------------
class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col

        # Walls: top, right, bottom, left
        self.walls = [True, True, True, True]
        self.in_maze = False

        self.color = None

    def draw(self, screen, highlight=False):
        x = self.col * CELL_SIZE + SHIFT
        y = self.row * CELL_SIZE + SHIFT

        if self.in_maze:
            if (not self.color) | (self.color == CURRENT_COLOR):
                self.color = CURRENT_COLOR if highlight else VISITED_COLOR
            pygame.draw.rect(screen, self.color, (x, y, CELL_SIZE, CELL_SIZE))

        # Draw walls
        if self.walls[0]:  # top
            pygame.draw.line(screen, WALL_COLOR, (x, y), (x + CELL_SIZE, y), 2)
        if self.walls[1]:  # right
            pygame.draw.line(screen, WALL_COLOR, (x + CELL_SIZE, y),
                             (x + CELL_SIZE, y + CELL_SIZE), 2)
        if self.walls[2]:  # bottom
            pygame.draw.line(screen, WALL_COLOR, (x, y + CELL_SIZE),
                             (x + CELL_SIZE, y + CELL_SIZE), 2)
        if self.walls[3]:  # left
            pygame.draw.line(screen, WALL_COLOR, (x, y), (x, y + CELL_SIZE), 2)


# -------------------------
# Helpers
# -------------------------
def get_neighbors(grid, row, col):
    neighbors = []

    directions = [
        (-1, 0),  # top
        (0, 1),   # right
        (1, 0),   # bottom
        (0, -1)   # left
    ]

    for dr, dc in directions:
        nr, nc = row + dr, col + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS:
            neighbors.append((nr, nc))

    return neighbors


def wall_between(cell1, cell2):
    dr = cell2.row - cell1.row
    dc = cell2.col - cell1.col

    if dr == -1:  # cell2 is above cell1
        return 0, 2
    if dr == 1:   # cell2 is below cell1
        return 2, 0
    if dc == 1:   # cell2 is right of cell1
        return 1, 3
    if dc == -1:  # cell2 is left of cell1
        return 3, 1

    return None


def remove_wall(cell1, cell2):
    walls = wall_between(cell1, cell2)
    if walls:
        w1, w2 = walls
        cell1.walls[w1] = False
        cell2.walls[w2] = False


def add_frontier(grid, row, col, frontier_set, frontier_list):
    for nr, nc in get_neighbors(grid, row, col):
        neighbor = grid[nr][nc]
        if not neighbor.in_maze and (nr, nc) not in frontier_set:
            frontier_set.add((nr, nc))
            frontier_list.append((nr, nc))


def generate_maze_prim(grid):
    start_row = random.randint(0, ROWS - 1)
    start_col = random.randint(0, COLS - 1)

    start_cell = grid[start_row][start_col]
    start_cell.in_maze = True
    start_cell.color = START_COLOR

    frontier_list = []
    frontier_set = set()

    add_frontier(grid, start_row, start_col, frontier_set, frontier_list)

    while frontier_list:
        fr, fc = random.choice(frontier_list)
        frontier_list.remove((fr, fc))
        frontier_set.remove((fr, fc))

        frontier_cell = grid[fr][fc]

        # Find neighbors already in maze
        in_maze_neighbors = []
        for nr, nc in get_neighbors(grid, fr, fc):
            if grid[nr][nc].in_maze:
                in_maze_neighbors.append(grid[nr][nc])

        if in_maze_neighbors:
            chosen_neighbor = random.choice(in_maze_neighbors)
            remove_wall(frontier_cell, chosen_neighbor)
            frontier_cell.in_maze = True
            add_frontier(grid, fr, fc, frontier_set, frontier_list)

        yield frontier_cell  # for animation

    end_row, end_col = start_row, start_col
    while (end_row == start_row) & (end_col == start_col):
        end_row, end_col = random.choice(
            [(0, random.randint(0, COLS - 1)), (random.randint(0, ROWS - 1), 0)])
    end_cell = grid[end_row][end_col]
    end_cell.color = END_COLOR


def create_grid():
    return [[Cell(r, c) for c in range(COLS)] for r in range(ROWS)]


def draw_grid(screen, grid, current_cell=None):
    screen.fill(BG_COLOR)

    for row in grid:
        for cell in row:
            highlight = (current_cell == cell)
            cell.draw(screen, highlight)

    pygame.display.flip()


# -------------------------
# Main
# -------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Prim's Algorithm Perfect Maze Generator")
    clock = pygame.time.Clock()

    grid = create_grid()
    maze_generator = generate_maze_prim(grid)
    generating = True
    current_cell = None

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Press R to regenerate
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    grid = create_grid()
                    maze_generator = generate_maze_prim(grid)
                    generating = True
                    current_cell = None

        if generating:
            try:
                current_cell = next(maze_generator)
            except StopIteration:
                generating = False
                current_cell = None

        draw_grid(screen, grid, current_cell)

    pygame.quit()


if __name__ == "__main__":
    main()
