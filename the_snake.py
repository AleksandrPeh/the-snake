from random import choice, randint

import pygame as pg

pg.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

CENTER_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (0, 255, 0)
SNAKE_COLOR = (0, 0, 255)
BAD_FRUIT_COLOR = (255, 0, 0)

SPEED = 10

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption('Змейка')
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, body_color=BOARD_BACKGROUND_COLOR):
        self.position = CENTER_POSITION
        self.body_color = body_color
        self.border_color = BORDER_COLOR

    def draw_cell(self, position, color=None, border=True):
        """Отрисовывает одну клетку поля по заданной позиции."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(
            screen, color if color is not None else self.body_color, rect)
        if border:
            pg.draw.rect(screen, self.border_color, rect, 1)

    def draw(self):
        raise NotImplementedError(
            'Метод draw должен быть реализован в дочернем классе')


class Apple(GameObject):
    """Яблоко: появляется в случайной свободной клетке."""

    def __init__(self, body_color=APPLE_COLOR, occupied_positions=(CENTER_POSITION,)):
        super().__init__(body_color)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions):
        """Ставит яблоко в случайную клетку, не занятую переданными позициями."""
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if self.position not in occupied_positions:
                break

    def draw(self):
        self.draw_cell(self.position)


class Snake(GameObject):
    """Змейка."""

    def __init__(self, body_color=SNAKE_COLOR):
        super().__init__(body_color)
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        return self.positions[0]

    def update_direction(self):
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR, border=False)

        for position in self.positions:
            self.draw_cell(position)

    def reset(self):
        self.length = 1
        self.last = None
        self.positions = [CENTER_POSITION]
        self.direction = choice([RIGHT, LEFT, UP, DOWN])
        self.next_direction = None


def handle_keys(game_object):
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)
    fruit = Apple(
        body_color=BAD_FRUIT_COLOR,
        occupied_positions=snake.positions + [apple.position],
    )

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        head = snake.get_head_position()

        if head == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions + [fruit.position])

        elif head == fruit.position or head in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            occupied = snake.positions + [apple.position, fruit.position]
            apple.randomize_position(occupied)
            fruit.randomize_position(occupied)

        snake.draw()
        apple.draw()
        fruit.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
