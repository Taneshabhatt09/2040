import pygame
import random
import math

pygame.init()

FPS = 60
WIDTH, HEIGHT = 700, 700
ROWS, COLS = 4, 4
RECT_HEIGHT = HEIGHT // ROWS
RECT_WIDTH = WIDTH // COLS

OUTLINE_COLOR = (187, 173, 160)
OUTLINE_THICKNESS = 10
BACKGROUND_COLOR = (205, 192, 180)
FONT_COLOR = (119, 110, 101)

FONT = pygame.font.SysFont("comicsans", 60, bold=True)
MOVE_VEL = 40

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048")

class Tile:
    COLORS = [
        (237, 229, 218), (238, 225, 201), (243, 178, 122), (246, 150, 101),
        (247, 124, 95), (247, 95, 59), (237, 208, 115), (237, 204, 99),
        (236, 202, 80),
    ]

    def __init__(self, value, row, col):
        self.value = value
        self.row = row
        self.col = col
        self.x = col * RECT_WIDTH
        self.y = row * RECT_HEIGHT
        self.target_x = self.x
        self.target_y = self.y
        self.merging = False

    def update_pos(self):
        if self.x < self.target_x:
            self.x = min(self.x + MOVE_VEL, self.target_x)
        elif self.x > self.target_x:
            self.x = max(self.x - MOVE_VEL, self.target_x)

        if self.y < self.target_y:
            self.y = min(self.y + MOVE_VEL, self.target_y)
        elif self.y > self.target_y:
            self.y = max(self.y - MOVE_VEL, self.target_y)

    def is_at_target(self):
        return self.x == self.target_x and self.y == self.target_y

    def get_color(self):
        index = min(int(math.log2(self.value)) - 1, len(self.COLORS) - 1)
        return self.COLORS[index]

    def draw(self, window):
        pygame.draw.rect(window, self.get_color(), (self.x, self.y, RECT_WIDTH, RECT_HEIGHT))
        text = FONT.render(str(self.value), 1, FONT_COLOR)
        window.blit(text, (
            self.x + (RECT_WIDTH / 2 - text.get_width() / 2),
            self.y + (RECT_HEIGHT / 2 - text.get_height() / 2)))

    def set_target(self, row, col):
        self.row, self.col = row, col
        self.target_x = col * RECT_WIDTH
        self.target_y = row * RECT_HEIGHT


def draw_grid(window):
    for row in range(1, ROWS):
        y = row * RECT_HEIGHT
        pygame.draw.line(window, OUTLINE_COLOR, (0, y), (WIDTH, y), OUTLINE_THICKNESS)
    for col in range(1, COLS):
        x = col * RECT_WIDTH
        pygame.draw.line(window, OUTLINE_COLOR, (x, 0), (x, HEIGHT), OUTLINE_THICKNESS)
    pygame.draw.rect(window, OUTLINE_COLOR, (0, 0, WIDTH, HEIGHT), OUTLINE_THICKNESS)


def draw(window, tiles):
    window.fill(BACKGROUND_COLOR)
    for tile in tiles:
        tile.draw(window)
    draw_grid(window)
    pygame.display.update()


def get_empty_positions(grid):
    return [(r, c) for r in range(ROWS) for c in range(COLS) if grid[r][c] is None]


def add_random_tile(grid, tiles):
    empty = get_empty_positions(grid)
    if not empty:
        return
    row, col = random.choice(empty)
    new_tile = Tile(random.choice([2, 4]), row, col)
    grid[row][col] = new_tile
    tiles.append(new_tile)


def generate_tiles():
    grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
    tiles = []
    for _ in range(2):
        add_random_tile(grid, tiles)
    return grid, tiles


def compress(grid, tiles, direction):
    moved = False
    new_tiles = []

    for r in range(ROWS):
        line = []
        if direction in ["left", "right"]:
            row = grid[r][:]
            if direction == "right": row.reverse()
        else:
            row = [grid[i][r] for i in range(ROWS)]
            if direction == "down": row.reverse()

        filtered = [tile for tile in row if tile is not None]
        merged = []

        i = 0
        while i < len(filtered):
            if i + 1 < len(filtered) and filtered[i].value == filtered[i + 1].value:
                merged_tile = Tile(filtered[i].value * 2, 0, 0)
                merged.append(merged_tile)
                i += 2
            else:
                merged.append(filtered[i])
                i += 1

        while len(merged) < ROWS:
            merged.append(None)

        if direction == "right" or direction == "down":
            merged.reverse()

        for i in range(ROWS):
            if direction in ["left", "right"]:
                if grid[r][i] != merged[i]: moved = True
                grid[r][i] = merged[i]
                if merged[i]: merged[i].set_target(r, i)
            else:
                if grid[i][r] != merged[i]: moved = True
                grid[i][r] = merged[i]
                if merged[i]: merged[i].set_target(i, r)

    tiles.clear()
    for row in grid:
        for tile in row:
            if tile: tiles.append(tile)
    return moved


def animate_tiles(tiles, window):
    animating = True
    clock = pygame.time.Clock()
    while animating:
        clock.tick(FPS)
        animating = False
        for tile in tiles:
            tile.update_pos()
            if not tile.is_at_target():
                animating = True
        draw(window, tiles)


def main(window):
    grid, tiles = generate_tiles()
    run = True
    clock = pygame.time.Clock()

    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                    direction = {
                        pygame.K_LEFT: "left",
                        pygame.K_RIGHT: "right",
                        pygame.K_UP: "up",
                        pygame.K_DOWN: "down"
                    }[event.key]

                    moved = compress(grid, tiles, direction)
                    animate_tiles(tiles, window)
                    if moved:
                        add_random_tile(grid, tiles)
        draw(window, tiles)

    pygame.quit()

if __name__ == "__main__":
    main(WINDOW)
