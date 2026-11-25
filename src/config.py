"""Модуль глобальных параметров и констант игры «Астероиды»."""

"""Размеры левой панели интерфейса и игрового холста (как в примере)"""
PANEL_WIDTH = 210
WIDTH = 800
HEIGHT = 600
WINDOW_WIDTH = PANEL_WIDTH + WIDTH

FPS = 60
WINDOW_TITLE = "Asteroids"

"""Цвета интерфейса и объектов (R, G, B)"""
COLOR_PANEL_BG = (240, 240, 240)
COLOR_PANEL_BORDER = (185, 185, 185)
COLOR_TEXT_DARK = (30, 30, 30)
COLOR_BLACK = (10, 10, 18)
COLOR_WHITE = (255, 255, 255)
COLOR_GREEN = (40, 235, 40)
COLOR_BLUE_FRAME = (45, 85, 210)
COLOR_SPLASH_BG = (42, 35, 95, 195)

"""Начальные параметры игрока"""
INITIAL_LIVES = 3
INITIAL_SCORE = 0

"""Физика корабля"""
SHIP_RADIUS = 22
SHIP_TURN_SPEED = 4.5      
SHIP_THRUST_ACCEL = 0.25    
SHIP_FRICTION = 0.985         

"""Параметры ракет"""
MISSILE_RADIUS = 4
MISSILE_SPEED = 8.5
"""Время жизни в кадрах (меньше времени пролета меньшей стороны: 600 / 8.5 ≈ 70)"""
MISSILE_LIFESPAN = 55

"""Параметры астероидов"""
ASTEROID_RADIUS = 36
ASTEROID_SPAWN_INTERVAL = 1200  # Интервал генерации в мс
ASTEROID_MAX_COUNT = 12
ASTEROID_MIN_SPEED = 1.0
ASTEROID_MAX_SPEED = 3.0
ASTEROID_MAX_ANGULAR_VEL = 2.8
SAFE_SPAWN_DISTANCE = 150

"""Параметры тайловой анимации взрыва и фона"""
EXPLOSION_FRAMES = 16
EXPLOSION_FRAME_SIZE = 72
EXPLOSION_ANIM_SPEED = 2
DEBRIS_SCROLL_SPEED = 0.5

"""Параметры заставки по центру игрового поля"""
SPLASH_WIDTH = 380
SPLASH_HEIGHT = 270
