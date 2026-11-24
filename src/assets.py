"""Модуль процедурной генерации детализированной графики и тайловых анимаций."""

import math
import random
import pygame
from src.config import (
    WIDTH,
    HEIGHT,
    EXPLOSION_FRAMES,
    EXPLOSION_FRAME_SIZE,
    SPLASH_WIDTH,
    SPLASH_HEIGHT,
    COLOR_WHITE,
    COLOR_BLUE_FRAME,
    COLOR_SPLASH_BG,
)


def create_background() -> pygame.Surface:
    """Создает неподвижный космический фон с туманностями, звездами и яркой звездой в центре."""
    rng = random.Random(42)
    bg = pygame.Surface((WIDTH, HEIGHT))
    bg.fill((14, 11, 22))

    # Мягкие красно-коричневые и синие космические туманности
    nebula = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    nebula_colors = [
        (95, 35, 22, 16),
        (75, 25, 45, 16),
        (25, 35, 85, 16),
        (110, 55, 25, 12),
    ]
    for _ in range(55):
        x = rng.randint(0, WIDTH)
        y = rng.randint(0, HEIGHT)
        r = rng.randint(70, 190)
        pygame.draw.circle(nebula, rng.choice(nebula_colors), (x, y), r)
    bg.blit(nebula, (0, 0))

    # Разноцветные фоновые звезды и блики
    star_colors = [
        (255, 255, 255),
        (200, 220, 255),
        (255, 210, 180),
        (255, 90, 110),
        (100, 160, 255),
    ]
    for _ in range(220):
        x = rng.randint(0, WIDTH)
        y = rng.randint(0, HEIGHT)
        rad = rng.choices((1, 2, 3), weights=(0.7, 0.25, 0.05))[0]
        col = rng.choice(star_colors)
        pygame.draw.circle(bg, col, (x, y), rad)
        if rad >= 2:
            glow = pygame.Surface((24, 24), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*col, 55), (12, 12), 10)
            bg.blit(glow, (x - 12, y - 12))

    # Яркая голубая звезда со свечением ближе к центру
    cx, cy = int(WIDTH * 0.46), int(HEIGHT * 0.44)
    star_glow = pygame.Surface((200, 200), pygame.SRCALPHA)
    for r in range(85, 5, -4):
        alpha = int(140 * ((1 - r / 85) ** 2.2))
        pygame.draw.circle(star_glow, (70, 150, 255, alpha), (100, 100), r)
    pygame.draw.circle(star_glow, (235, 250, 255, 255), (100, 100), 9)
    bg.blit(star_glow, (cx - 100, cy - 100))

    return bg


def create_debris_layer() -> pygame.Surface:
    """Создает полупрозрачный слой мелких камней и пыли для динамического фона."""
    rng = random.Random(99)
    layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for _ in range(55):
        x = rng.randint(0, WIDTH)
        y = rng.randint(0, HEIGHT)
        size = rng.randint(4, 13)
        points = []
        for i in range(7):
            angle = math.radians(i * (360 / 7) + rng.randint(-15, 15))
            dist_val = size * rng.uniform(0.55, 1.1)
            points.append((x + math.cos(angle) * dist_val, y + math.sin(angle) * dist_val))
        shade = rng.randint(95, 155)
        pygame.draw.polygon(layer, (shade, shade - 8, shade - 15, 145), points)
        pygame.draw.polygon(layer, (50, 45, 42, 160), points, 1)
    return layer


"""Модуль процедурной генерации спрайтов корабля, астероидов и ракет."""

import math
import random
import pygame


def create_ship_surfaces() -> tuple[pygame.Surface, pygame.Surface]:
    """Создает детализированный спрайт истребителя (без тяги и с включенным двигателем)."""
    size = (72, 72)
    cx, cy = 36, 36

    def draw_fighter(surf: pygame.Surface) -> None:
        outer_wings = [
            (cx + 6, cy - 6),
            (cx - 10, cy - 26),
            (cx - 20, cy - 22),
            (cx - 15, cy - 8),
            (cx - 15, cy + 8),
            (cx - 20, cy + 22),
            (cx - 10, cy + 26),
            (cx + 6, cy + 6),
        ]
        pygame.draw.polygon(surf, (175, 182, 195), outer_wings)
        pygame.draw.polygon(surf, (55, 60, 70), outer_wings, 2)

        # Красные полосы на крыльях
        pygame.draw.line(surf, (195, 45, 45), (cx - 6, cy - 12), (cx - 16, cy - 21), 3)
        pygame.draw.line(surf, (195, 45, 45), (cx - 6, cy + 12), (cx - 16, cy + 21), 3)

        # Основной фюзеляж
        body = [
            (cx + 28, cy),
            (cx + 8, cy - 10),
            (cx - 22, cy - 11),
            (cx - 18, cy),
            (cx - 22, cy + 11),
            (cx + 8, cy + 10),
        ]
        pygame.draw.polygon(surf, (230, 234, 240), body)
        pygame.draw.polygon(surf, (70, 75, 85), body, 2)

        # Красный нос и центральная полоса
        nose = [(cx + 28, cy), (cx + 15, cy - 5), (cx + 15, cy + 5)]
        pygame.draw.polygon(surf, (200, 40, 40), nose)
        pygame.draw.line(surf, (190, 45, 45), (cx - 16, cy), (cx + 14, cy), 2)

        # Стеклянная кабина пилота
        pygame.draw.ellipse(surf, (45, 145, 215), (cx - 2, cy - 5, 15, 10))
        pygame.draw.ellipse(surf, (170, 230, 255), (cx + 2, cy - 3, 7, 4))

    ship_idle = pygame.Surface(size, pygame.SRCALPHA)
    draw_fighter(ship_idle)

    ship_thrust = pygame.Surface(size, pygame.SRCALPHA)
    for offset_y in (-6, 6):
        flame_outer = [
            (cx - 19, cy + offset_y - 4),
            (cx - 35, cy + offset_y),
            (cx - 19, cy + offset_y + 4),
        ]
        flame_inner = [
            (cx - 19, cy + offset_y - 2),
            (cx - 28, cy + offset_y),
            (cx - 19, cy + offset_y + 2),
        ]
        pygame.draw.polygon(ship_thrust, (255, 120, 20), flame_outer)
        pygame.draw.polygon(ship_thrust, (255, 245, 140), flame_inner)

    draw_fighter(ship_thrust)
    return ship_idle, ship_thrust


def create_asteroid_surface() -> pygame.Surface:
    """Создает объемный текстурированный спрайт астероида с тенью и кратерами."""
    rng = random.Random(17)
    size = 84
    cx, cy = size // 2, size // 2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)

    points = []
    num_pts = 18
    for i in range(num_pts):
        angle = math.radians(i * (360 / num_pts))
        radius = rng.uniform(33.5, 37.5)
        points.append((cx + math.cos(angle) * radius, cy + math.sin(angle) * radius))

    pygame.draw.polygon(surf, (132, 134, 140), points)
    pygame.draw.circle(surf, (162, 165, 172), (cx - 7, cy - 7), 23)
    pygame.draw.circle(surf, (112, 114, 120), (cx + 7, cy + 7), 22)

    # Кратеры с темным дном и светлой кромкой
    craters = [
        (cx - 12, cy - 10, 7),
        (cx + 8, cy - 12, 6),
        (cx - 3, cy + 3, 8),
        (cx + 13, cy + 8, 6),
        (cx - 14, cy + 12, 5),
        (cx + 2, cy + 18, 4),
    ]
    for cr_x, cr_y, cr_r in craters:
        pygame.draw.circle(surf, (175, 178, 184), (cr_x + 1, cr_y + 1), cr_r)
        pygame.draw.circle(surf, (82, 84, 90), (cr_x, cr_y), cr_r - 1)
        pygame.draw.circle(surf, (98, 100, 106), (cr_x + 1, cr_y + 1), max(1, cr_r - 3))

    pygame.draw.polygon(surf, (65, 67, 73), points, 2)
    return surf


def create_missile_surface() -> pygame.Surface:
    """Создает спрайт яркой энергетической ракеты."""
    surf = pygame.Surface((14, 14), pygame.SRCALPHA)
    pygame.draw.circle(surf, (255, 90, 40, 140), (7, 7), 6)
    pygame.draw.circle(surf, (255, 220, 110), (7, 7), 3)
    return surf


def create_missile_surface() -> pygame.Surface:
    """Создает спрайт яркой энергетической ракеты."""
    surf = pygame.Surface((14, 14), pygame.SRCALPHA)
    pygame.draw.circle(surf, (255, 90, 40, 140), (7, 7), 6)
    pygame.draw.circle(surf, (255, 220, 110), (7, 7), 3)
    return surf


def create_explosion_tilesheet() -> list[pygame.Surface]:
    """Генерирует тайловый лист для покадровой анимации взрыва."""
    tilesheet = pygame.Surface(
        (EXPLOSION_FRAMES * EXPLOSION_FRAME_SIZE, EXPLOSION_FRAME_SIZE),
        pygame.SRCALPHA,
    )
    half = EXPLOSION_FRAME_SIZE // 2

    for i in range(EXPLOSION_FRAMES):
        progress = i / (EXPLOSION_FRAMES - 1)
        fx = i * EXPLOSION_FRAME_SIZE + half
        fy = half

        outer_r = int(10 + progress * (half - 4))
        alpha = int(255 * (1.0 - progress * 0.85))

        pygame.draw.circle(tilesheet, (235, 85, 30, alpha), (fx, fy), outer_r)
        if progress < 0.8:
            pygame.draw.circle(tilesheet, (255, 175, 45, alpha), (fx, fy), int(outer_r * 0.7))
        if progress < 0.55:
            pygame.draw.circle(tilesheet, (255, 240, 160, alpha), (fx, fy), int(outer_r * 0.4))

    frames = []
    for i in range(EXPLOSION_FRAMES):
        rect = pygame.Rect(i * EXPLOSION_FRAME_SIZE, 0, EXPLOSION_FRAME_SIZE, EXPLOSION_FRAME_SIZE)
        frames.append(tilesheet.subsurface(rect))
    return frames


def create_splash_surface() -> pygame.Surface:
    """Создает полупрозрачную заставку в стиле RiceRocks со скриншота."""
    splash = pygame.Surface((SPLASH_WIDTH, SPLASH_HEIGHT), pygame.SRCALPHA)
    splash.fill(COLOR_SPLASH_BG)
    pygame.draw.rect(splash, COLOR_BLUE_FRAME, (0, 0, SPLASH_WIDTH, SPLASH_HEIGHT), 2)

    title_font = pygame.font.SysFont("impact", 52)
    title_str = "Asteroids"
    cx, cy = SPLASH_WIDTH // 2, SPLASH_HEIGHT // 2 - 25

    outline_surf = title_font.render(title_str, True, (200, 210, 255))
    main_surf = title_font.render(title_str, True, (45, 48, 65))
    for dx in (-3, 0, 3):
        for dy in (-3, 0, 3):
            splash.blit(outline_surf, outline_surf.get_rect(center=(cx + dx, cy + dy)))
    splash.blit(main_surf, main_surf.get_rect(center=(cx, cy)))

    sub_font = pygame.font.SysFont("arial", 18, bold=True)
    sub_surf = sub_font.render("CLICK TO START", True, COLOR_WHITE)
    sub_y = SPLASH_HEIGHT // 2 + 42
    splash.blit(sub_surf, sub_surf.get_rect(center=(cx, sub_y)))

    for side in (-1, 1):
        rx = cx + side * 105
        for step in range(3):
            ry = sub_y - 12 + step * 8
            color = (180, 200, 245) if step % 2 == 0 else (110, 130, 195)
            pygame.draw.polygon(
                splash,
                color,
                [(rx - 8, ry), (rx + 8, ry + 3), (rx + 6, ry + 9), (rx - 10, ry + 6)],
            )

    return splash
