"""Игра «Змейка» на pygame."""

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

    def __init__(
        self,
        body_color=BOARD_BACKGROUND_COLOR,
        border_color=BORDER_COLOR,
    ):
        """Инициализирует объект: позиция, цвет тела и цвет рамки."""
        self.position = CENTER_POSITION
        self.body_color = body_color
        self.border_color = border_color

    def draw_cell(self, position, color=None, border=True):
        """Отрисовывает одну клетку поля по заданной позиции."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        if self.border_color is not None:
            pg.draw.rect(screen, self.border_color, rect, 1)

    def draw(self):
        """Отрисовывает объект. Реализуется в дочерних классах."""
        raise NotImplementedError(
            'Метод draw должен быть реализован в дочернем классе',
        )


class Apple(GameObject):
    """Яблоко: появляется в случайной свободной клетке."""

    def __init__(
        self,
        body_color=APPLE_COLOR,
        border_color=BORDER_COLOR,
        occupied_positions=(CENTER_POSITION,),
    ):
        """Создаёт яблоко и ставит его в свободную клетку."""
        super().__init__(body_color, border_color)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions):
        """Ставит яблоко в случайную клетку, не занятую другими объектами."""
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if self.position not in occupied_positions:
                break

    def draw(self):
        """Отрисовывает яблоко на игровом поле."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Змейка: движется по полю, растёт от яблок, гибнет от препятствий."""

    def __init__(self, body_color=SNAKE_COLOR, border_color=BORDER_COLOR):
        """Создаёт змейку длины 1 в центре поля."""
        super().__init__(body_color, border_color)
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def update_direction(self):
        """Применяет отложенное направление к текущему."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Смещает змейку на одну клетку в текущем направлении."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head)

        self.last = (
            self.positions.pop()
            if len(self.positions) > self.length
            else None
        )
    def erase_last(self):
        """Затирает прошлую позицию хвоста."""
        if self.last is not None:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR, border=False)
            self.last = None

    def draw(self):
        """Рисует змейку на игровом поле."""
        for position in self.positions:
            self.draw_cell(position)

    def reset(self):
        """Возвращает змейку в начальное состояние в центре поля."""
        self.length = 1
        self.last = None
        self.positions = [self.position]
        self.direction = choice([RIGHT, LEFT, UP, DOWN])
        self.next_direction = None


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш и события окна."""
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
    """Запускает основной игровой цикл."""
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
            apple.randomize_position(snake.positions)
            fruit.randomize_position(snake.positions + [apple.position])

        snake.erase_last()
        snake.draw()
        apple.draw()
        fruit.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
