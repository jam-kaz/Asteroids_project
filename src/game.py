"""Основной модуль управления игровым процессом и рендерингом."""

import math
import random
import pygame
from src.config import (
    WIDTH,
    HEIGHT,
    FPS,
    WINDOW_TITLE,
    COLOR_GREEN,
    INITIAL_LIVES,
    INITIAL_SCORE,
    ASTEROID_SPAWN_INTERVAL,
    ASTEROID_MAX_COUNT,
    ASTEROID_MIN_SPEED,
    ASTEROID_MAX_SPEED,
    ASTEROID_MAX_ANGULAR_VEL,
    SAFE_SPAWN_DISTANCE,
    DEBRIS_SCROLL_SPEED,
)
from src.assets import (
    create_background,
    create_debris_layer,
    create_ship_surfaces,
    create_asteroid_surface,
    create_missile_surface,
    create_explosion_tilesheet,
    create_splash_surface,
)
from src.entities import Ship, Asteroid, Missile, Explosion, dist


class AsteroidsGame:
    """Главный класс игры, управляющий циклом, событиями, логикой и отрисовкой."""

    def __init__(self) -> None:
        """Инициализирует pygame, загружает ресурсы и устанавливает начальное состояние."""
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.hud_font = pygame.font.Font(None, 36)


        """Загрузка/генерация графических ресурсов"""
        self.bg_image = create_background()
        self.debris_image = create_debris_layer()
        self.ship_idle_img, self.ship_thrust_img = create_ship_surfaces()
        self.asteroid_img = create_asteroid_surface()
        self.missile_img = create_missile_surface()
        self.explosion_frames = create_explosion_tilesheet()
        self.splash_img = create_splash_surface()
        self.splash_rect = self.splash_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))

        """Состояние игры"""
        self.running = True
        self.started = False
        self.lives = INITIAL_LIVES
        self.score = INITIAL_SCORE
        self.debris_x = 0.0

        """Игровые объекты"""
        self.ship = Ship((WIDTH // 2, HEIGHT // 2), self.ship_idle_img, self.ship_thrust_img)
        self.asteroids: list[Asteroid] = []
        self.missiles: list[Missile] = []
        self.explosions: list[Explosion] = []

        """Пользовательское событие таймера генерации астероидов"""
        self.SPAWN_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.SPAWN_EVENT, ASTEROID_SPAWN_INTERVAL)

    def start_new_game(self) -> None:
        """Сбрасывает счетчики, очищает поле и запускает новую игровую сессию."""
        self.started = True
        self.lives = INITIAL_LIVES
        self.score = INITIAL_SCORE
        self.asteroids.clear()
        self.missiles.clear()
        self.explosions.clear()
        self.ship.reset((WIDTH // 2, HEIGHT // 2))

    def spawn_asteroid(self) -> None:
        """Генерирует новый астероид в случайном месте на безопасном расстоянии от корабля."""
        if not self.started or len(self.asteroids) >= ASTEROID_MAX_COUNT:
            return

        """Подбор координат вне безопасной зоны вокруг корабля"""
        for _ in range(20):
            pos = (random.randint(0, WIDTH), random.randint(0, HEIGHT))
            if dist(pos, self.ship.pos) > SAFE_SPAWN_DISTANCE:
                break
        else:
            pos = (0, 0)

        angle = random.uniform(0, 360)
        speed = random.uniform(ASTEROID_MIN_SPEED, ASTEROID_MAX_SPEED)
        vel_angle = random.uniform(0, 2 * math.pi)
        vel = (math.cos(vel_angle) * speed, math.sin(vel_angle) * speed)
        angle_vel = random.uniform(-ASTEROID_MAX_ANGULAR_VEL, ASTEROID_MAX_ANGULAR_VEL)

        self.asteroids.append(Asteroid(pos, vel, angle, angle_vel, self.asteroid_img))

    def handle_events(self) -> None:
        """Обрабатывает события клавиатуры, мыши и таймеров."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == self.SPAWN_EVENT:
                self.spawn_asteroid()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                """Старт только при щелчке строго по прямоугольнику заставки"""
                if not self.started and self.splash_rect.collidepoint(event.pos):
                    self.start_new_game()

            elif event.type == pygame.KEYDOWN and self.started:
                if event.key == pygame.K_LEFT:
                    self.ship.rotate(-1)
                elif event.key == pygame.K_RIGHT:
                    self.ship.rotate(1)
                elif event.key == pygame.K_UP:
                    self.ship.set_thrust(True)
                elif event.key == pygame.K_SPACE:
                    self.missiles.append(self.ship.shoot(self.missile_img))

            elif event.type == pygame.KEYUP and self.started:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    """Проверяем, не зажата ли противоположная стрелка"""
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LEFT]:
                        self.ship.rotate(-1)
                    elif keys[pygame.K_RIGHT]:
                        self.ship.rotate(1)
                    else:
                        self.ship.rotate(0)
                elif event.key == pygame.K_UP:
                    self.ship.set_thrust(False)

    def update(self) -> None:
        """Обновляет состояние динамического фона, объектов и проверяет столкновения."""
        self.debris_x = (self.debris_x - DEBRIS_SCROLL_SPEED) % WIDTH

        """Обновление анимаций взрывов (работает даже при завершении игры)"""
        for explosion in self.explosions[:]:
            explosion.update()
            if explosion.finished:
                self.explosions.remove(explosion)

        if not self.started:
            return

        self.ship.update()

        for asteroid in self.asteroids:
            asteroid.update()

        for missile in self.missiles[:]:
            if missile.update():
                self.missiles.remove(missile)

        self._check_collisions()

    def _check_collisions(self) -> None:
        """Обрабатывает столкновения ракет и корабля с астероидами."""
        """ Столкновение ракет и астероидов """
        for missile in self.missiles[:]:
            for asteroid in self.asteroids[:]:
                if missile.collides_with(asteroid):
                    if missile in self.missiles:
                        self.missiles.remove(missile)
                    if asteroid in self.asteroids:
                        self.asteroids.remove(asteroid)
                    self.explosions.append(Explosion(asteroid.pos, self.explosion_frames))
                    self.score += 1
                    break

        """ Столкновение корабля и астероидов """
        for asteroid in self.asteroids[:]:
            if self.ship.collides_with(asteroid):
                self.asteroids.remove(asteroid)
                self.explosions.append(Explosion(asteroid.pos, self.explosion_frames))
                self.lives -= 1

                if self.lives <= 0:
                    self.lives = 0
                    self.started = False
                    self.asteroids.clear()
                    self.missiles.clear()
                    self.ship.set_thrust(False)
                    break
                else:
                    self.ship.reset((WIDTH // 2, HEIGHT // 2))

    def draw(self) -> None:
        """Отрисовывает все слои графики, объекты и интерфейс."""
        """ 1. Неподвижный фон"""
        self.screen.blit(self.bg_image, (0, 0))

        """ 2. Динамический фон (движется влево, дублируется для бесшовности)"""
        ix = int(self.debris_x)
        self.screen.blit(self.debris_image, (ix - WIDTH, 0))
        self.screen.blit(self.debris_image, (ix, 0))

        """ 3. Игровые объекты (отображаются только во время активной игры)"""
        if self.started:
            for missile in self.missiles:
                missile.draw(self.screen)
            for asteroid in self.asteroids:
                asteroid.draw(self.screen)
            self.ship.draw(self.screen)

        """ 4. Взрывы """
        for explosion in self.explosions:
            explosion.draw(self.screen)

        """ 5. Интерфейс (жизни и очки) """
        lives_surf = self.hud_font.render(f"Lives: {self.lives}", False, (50, 255, 50))
        score_surf = self.hud_font.render(f"Score: {self.score}", False, (50, 255, 50))
        self.screen.blit(lives_surf, (40, 20))
        self.screen.blit(score_surf, (WIDTH - score_surf.get_width() - 40, 20))

        """ 6. Заставка (при старте или после окончания жизней) """
        if not self.started:
            self.screen.blit(self.splash_img, self.splash_rect)

        pygame.display.flip()

    def run(self) -> None:
        """Запускает главный цикл приложения."""
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

        pygame.quit()
