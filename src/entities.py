"""Модуль игровых сущностей (Корабль, Астероид, Ракета, Взрыв)."""

import math
import pygame
from src.config import (
    WIDTH,
    HEIGHT,
    SHIP_RADIUS,
    SHIP_TURN_SPEED,
    SHIP_THRUST_ACCEL,
    SHIP_FRICTION,
    MISSILE_RADIUS,
    MISSILE_SPEED,
    MISSILE_LIFESPAN,
    ASTEROID_RADIUS,
    EXPLOSION_ANIM_SPEED,
)


def angle_to_vector(angle_deg: float) -> tuple[float, float]:
    """Преобразует угол в градусах в единичный вектор направления (dx, dy)."""
    rad = math.radians(angle_deg)
    return math.cos(rad), math.sin(rad)


def dist(pos1: list[float] | tuple[float, float], pos2: list[float] | tuple[float, float]) -> float:
    """Вычисляет евклидово расстояние между двумя точками на плоскости."""
    return math.hypot(pos1 - pos2, pos1 - pos2)


class SpaceObject:
    """Базовый класс для объектов, движущихся в тороидальном пространстве."""

    def __init__(
        self,
        pos: tuple[float, float],
        vel: tuple[float, float],
        angle: float,
        angle_vel: float,
        image: pygame.Surface,
        radius: float,
    ) -> None:
        """Инициализирует базовые физические параметры объекта."""
        self.pos = [float(pos), float(pos)]
        self.vel = [float(vel), float(vel)]
        self.angle = float(angle)
        self.angle_vel = float(angle_vel)
        self.image = image
        self.radius = radius

    def update_position(self) -> None:
        """Обновляет координаты и угол, обеспечивая тороидальную геометрию экрана."""
        self.angle = (self.angle + self.angle_vel) % 360
        self.pos = (self.pos + self.vel) % WIDTH
        self.pos = (self.pos + self.vel) % HEIGHT

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает повернутый спрайт объекта относительно его центра."""
        rotated = pygame.transform.rotate(self.image, -self.angle)
        rect = rotated.get_rect(center=(int(self.pos), int(self.pos)))
        surface.blit(rotated, rect)

    def collides_with(self, other: "SpaceObject") -> bool:
        """Проверяет столкновение двух объектов по сумме их радиусов."""
        return dist(self.pos, other.pos) < (self.radius + other.radius)


class Ship(SpaceObject):
    """Класс космического корабля, управляемого игроком."""

    def __init__(
        self,
        pos: tuple[float, float],
        img_idle: pygame.Surface,
        img_thrust: pygame.Surface,
    ) -> None:
        """Инициализирует корабль в указанной точке."""
        super().__init__(pos, (0.0, 0.0), -90.0, 0.0, img_idle, SHIP_RADIUS)
        self.img_idle = img_idle
        self.img_thrust = img_thrust
        self.thrust = False

    def set_thrust(self, active: bool) -> None:
        """Включает или выключает двигатель и меняет изображение корабля."""
        self.thrust = active
        self.image = self.img_thrust if active else self.img_idle

    def rotate(self, direction: int) -> None:
        """Задает угловую скорость вращения (-1 влево, 1 вправо, 0 стоп)."""
        self.angle_vel = direction * SHIP_TURN_SPEED

    def update(self) -> None:
        """Обновляет скорость (с учетом ускорения и сопротивления среды) и позицию."""
        if self.thrust:
            fwd_x, fwd_y = angle_to_vector(self.angle)
            self.vel += fwd_x * SHIP_THRUST_ACCEL
            self.vel += fwd_y * SHIP_THRUST_ACCEL

        self.vel *= SHIP_FRICTION
        self.vel *= SHIP_FRICTION

        if math.hypot(self.vel, self.vel) < 0.02 and not self.thrust:
            self.vel = [0.0, 0.0]

        self.update_position()

    def shoot(self, missile_img: pygame.Surface) -> "Missile":
        """Создает ракету, вылетающую из носа корабля в направлении его ориентации."""
        fwd_x, fwd_y = angle_to_vector(self.angle)
        nose_x = self.pos + fwd_x * self.radius
        nose_y = self.pos + fwd_y * self.radius
        missile_vel = (fwd_x * MISSILE_SPEED, fwd_y * MISSILE_SPEED)
        return Missile((nose_x, nose_y), missile_vel, self.angle, missile_img)

    def reset(self, pos: tuple[float, float]) -> None:
        """Возрождает неподвижный корабль в центре игрового поля."""
        self.pos = [float(pos), float(pos)]
        self.vel = [0.0, 0.0]
        self.angle = -90.0
        self.angle_vel = 0.0
        self.set_thrust(False)


class Asteroid(SpaceObject):
    """Класс астероида со случайной линейной и угловой скоростью."""

    def __init__(
        self,
        pos: tuple[float, float],
        vel: tuple[float, float],
        angle: float,
        angle_vel: float,
        image: pygame.Surface,
    ) -> None:
        """Инициализирует астероид."""
        super().__init__(pos, vel, angle, angle_vel, image, ASTEROID_RADIUS)

    def update(self) -> None:
        """Обновляет положение и угол поворота астероида."""
        self.update_position()


class Missile(SpaceObject):
    """Класс ракеты с ограниченным временем жизни."""

    def __init__(
        self,
        pos: tuple[float, float],
        vel: tuple[float, float],
        angle: float,
        image: pygame.Surface,
    ) -> None:
        """Инициализирует ракету."""
        super().__init__(pos, vel, angle, 0.0, image, MISSILE_RADIUS)
        self.age = 0

    def update(self) -> bool:
        """Обновляет позицию ракеты. Возвращает True, если время жизни истекло."""
        self.update_position()
        self.age += 1
        return self.age >= MISSILE_LIFESPAN


class Explosion:
    """Класс тайловой покадровой анимации взрыва."""

    def __init__(self, pos: list[float] | tuple[float, float], frames: list[pygame.Surface]) -> None:
        """Инициализирует анимацию взрыва в заданных координатах."""
        self.pos = (int(pos), int(pos))
        self.frames = frames
        self.tick = 0
        self.finished = False

    def update(self) -> None:
        """Переключает кадры тайловой анимации."""
        self.tick += 1
        if self.tick // EXPLOSION_ANIM_SPEED >= len(self.frames):
            self.finished = True

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает текущий кадр взрыва."""
        if not self.finished:
            frame_idx = self.tick // EXPLOSION_ANIM_SPEED
            frame = self.frames[frame_idx]
            rect = frame.get_rect(center=self.pos)
            surface.blit(frame, rect)

