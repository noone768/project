import math
import random
import pygame

pygame.init()

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NEON RUNNER")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 22, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 16, bold=True)
BIG_FONT = pygame.font.SysFont("arial", 56, bold=True)

HORIZON = 190
BOTTOM = 690
CENTER = WIDTH // 2
LANES = [-1, 0, 1]

game = {}


def reset_game():
    game.update({
        "lane": 0,
        "player_x": 0.0,
        "jump": 0.0,
        "jump_velocity": 0.0,
        "obstacles": [],
        "score": 0,
        "speed": 0.42,
        "spawn_timer": 0.0,
        "road_scroll": 0.0,
        "over": False,
    })


reset_game()


def road_width(y):
    t = max(0, min(1, (y - HORIZON) / (BOTTOM - HORIZON)))
    return 65 + 440 * t


def lane_x(lane, y):
    return CENTER + lane * road_width(y) * 0.58


def draw_glow(surface, color, pos, radius, strength=70):
    glow = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
    pygame.draw.circle(glow, (*color, strength), (radius * 2, radius * 2), radius)
    surface.blit(glow, (int(pos[0] - radius * 2), int(pos[1] - radius * 2)),
                 special_flags=pygame.BLEND_ADD)


def draw_text(text, font, color, pos, center=False):
    image = font.render(text, True, color)
    rect = image.get_rect()
    rect.center = pos if center else rect.center
    if not center:
        rect.topleft = pos
    screen.blit(image, rect)


def draw_background():
    # Градиентное ночное небо
    for y in range(HEIGHT):
        t = y / HEIGHT
        color = (
            int(8 + 8 * t),
            int(12 + 7 * t),
            int(32 + 22 * t),
        )
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))

    # Далёкий город
    random.seed(12)
    x = 0
    while x < WIDTH:
        w = random.randint(22, 54)
        h = random.randint(25, 105)
        building = pygame.Rect(x, HORIZON - h, w, h)
        pygame.draw.rect(screen, (12, 20, 43), building)
        pygame.draw.line(screen, (25, 48, 83),
                         building.topleft, building.topright, 1)

        for wy in range(building.top + 10, HORIZON - 5, 16):
            for wx in range(x + 6, x + w - 4, 12):
                if random.random() > 0.45:
                    pygame.draw.rect(screen, (30, 100, 135),
                                     (wx, wy, 3, 5))
        x += w + 3

    # Луна и горизонт
    pygame.draw.circle(screen, (30, 50, 92), (CENTER, 115), 54)
    pygame.draw.circle(screen, (75, 125, 175), (CENTER, 115), 42, 2)
    pygame.draw.line(screen, (35, 100, 145), (0, HORIZON), (WIDTH, HORIZON), 2)


def draw_road():
    top_left = (CENTER - 65, HORIZON)
    top_right = (CENTER + 65, HORIZON)
    bottom_left = (CENTER - 505, BOTTOM)
    bottom_right = (CENTER + 505, BOTTOM)

    pygame.draw.polygon(screen, (17, 22, 40),
                        [top_left, top_right, bottom_right, bottom_left])

    # Дорожные края
    for side in (-1, 1):
        points = []
        for i in range(30):
            t = i / 29
            y = HORIZON + t * (BOTTOM - HORIZON)
            x = CENTER + side * road_width(y)
            points.append((int(x), int(y)))
        pygame.draw.lines(screen, (0, 190, 220), False, points, 3)

    # Пунктирные разделители
    for boundary in (-0.29, 0.29):
        for i in range(14):
            phase = (i / 14 + game["road_scroll"]) % 1
            y1 = HORIZON + phase ** 1.7 * (BOTTOM - HORIZON)
            y2 = HORIZON + min(1, phase + 0.027) ** 1.7 * (BOTTOM - HORIZON)
            x1 = CENTER + boundary * road_width(y1) * 1.72
            x2 = CENTER + boundary * road_width(y2) * 1.72
            width = max(1, int(1 + phase * 3))
            pygame.draw.line(screen, (65, 84, 117), (x1, y1), (x2, y2), width)

    # Световые маркеры вдоль дороги
    for side in (-1, 1):
        for i in range(12):
            phase = (i / 12 + game["road_scroll"] * 0.75) % 1
            y = HORIZON + phase ** 1.7 * (BOTTOM - HORIZON)
            x = CENTER + side * (road_width(y) + 20 + phase * 85)
            radius = max(2, int(2 + phase * 5))
            color = (0, 210, 240) if i % 2 else (255, 50, 130)
            draw_glow(screen, color, (x, y), radius * 3, 35)
            pygame.draw.circle(screen, color, (int(x), int(y)), radius)


def draw_obstacle(obstacle):
    depth = obstacle["depth"]
    y = HORIZON + depth ** 1.7 * (BOTTOM - HORIZON)
    x = lane_x(obstacle["lane"], y)
    scale = 0.25 + depth * 1.25

    w, h = int(48 * scale), int(54 * scale)
    rect = pygame.Rect(int(x - w / 2), int(y - h), w, h)
    color = (255, 55, 125)

    draw_glow(screen, color, (x, y - h / 2), max(8, int(w * 0.8)), 25)
    pygame.draw.rect(screen, (48, 18, 43), rect, border_radius=max(3, int(7 * scale)))
    pygame.draw.rect(screen, color, rect, max(2, int(2 * scale)),
                     border_radius=max(3, int(7 * scale)))

    # Светящаяся полоса на препятствии
    stripe_y = rect.top + int(h * 0.28)
    pygame.draw.line(screen, (255, 185, 215),
                     (rect.left + 5, stripe_y), (rect.right - 5, stripe_y),
                     max(1, int(2 * scale)))


def draw_player():
    x = int(game["player_x"])
    jump_height = int(game["jump"] * 105)
    ground_y = 625
    y = ground_y - jump_height

    # Тень
    shadow_w = max(18, 58 - jump_height // 3)
    pygame.draw.ellipse(screen, (5, 8, 20),
                        (x - shadow_w // 2, ground_y + 5, shadow_w, 13))

    # Ноги
    pygame.draw.line(screen, (20, 190, 210), (x - 10, y - 25), (x - 15, y),
                     8)
    pygame.draw.line(screen, (20, 190, 210), (x + 10, y - 25), (x + 15, y),
                     8)

    # Тело
    body = pygame.Rect(x - 22, y - 67, 44, 48)
    pygame.draw.rect(screen, (12, 115, 150), body, border_radius=13)
    pygame.draw.rect(screen, (0, 235, 245), body, 2, border_radius=13)

    # Руки
    pygame.draw.line(screen, (0, 220, 230), (x - 17, y - 53), (x - 31, y - 34), 6)
    pygame.draw.line(screen, (0, 220, 230), (x + 17, y - 53), (x + 31, y - 34), 6)

    # Голова и визор
    pygame.draw.circle(screen, (22, 44, 72), (x, y - 79), 17)
    pygame.draw.circle(screen, (0, 235, 245), (x, y - 79), 17, 2)
    pygame.draw.roundrect if False else None
    pygame.draw.rect(screen, (255, 70, 145), (x - 11, y - 83, 22, 7),
                     border_radius=4)


def draw_hud():
    # Полупрозрачная панель
    panel = pygame.Surface((250, 72), pygame.SRCALPHA)
    pygame.draw.rect(panel, (7, 15, 35, 205), (0, 0, 250, 72), border_radius=16)
    pygame.draw.rect(panel, (0, 210, 230, 150), (0, 0, 250, 72), 2,
                     border_radius=16)
    screen.blit(panel, (22, 20))

    draw_text("DISTANCE", SMALL_FONT, (130, 170, 195), (40, 30))
    draw_text(f"{game['score']:05d} m", FONT, (235, 250, 255), (40, 48))

    help_text = "← →  MOVE     SPACE  JUMP"
    draw_text(help_text, SMALL_FONT, (125, 180, 205),
              (WIDTH - 275, 39))


def draw_game_over():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((3, 6, 18, 185))
    screen.blit(overlay, (0, 0))

    panel = pygame.Rect(220, 240, 560, 220)
    pygame.draw.rect(screen, (12, 22, 45), panel, border_radius=24)
    pygame.draw.rect(screen, (255, 55, 130), panel, 2, border_radius=24)

    draw_text("RUN OVER", BIG_FONT, (255, 75, 145), (CENTER, 300), True)
    draw_text(f"DISTANCE   {game['score']} m", FONT, (230, 245, 255),
              (CENTER, 365), True)
    draw_text("PRESS  R  TO RUN AGAIN", SMALL_FONT, (0, 220, 235),
              (CENTER, 415), True)


def spawn_obstacle():
    game["obstacles"].append({
        "lane": random.choice(LANES),
        "depth": 0.0,
    })


running = True

while running:
    dt = min(clock.tick(60) / 1000, 0.04)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if game["over"]:
                if event.key == pygame.K_r:
                    reset_game()
            else:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    game["lane"] = max(-1, game["lane"] - 1)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    game["lane"] = min(1, game["lane"] + 1)
                elif event.key == pygame.K_SPACE and game["jump"] <= 0:
                    game["jump_velocity"] = 2.8

    if not game["over"]:
        target_x = lane_x(game["lane"], 625)
        game["player_x"] += (target_x - game["player_x"]) * min(1, dt * 12)

        game["score"] += int(game["speed"] * 60 * dt)
        game["speed"] = min(0.85, 0.42 + game["score"] / 22000)
        game["road_scroll"] = (game["road_scroll"] + game["speed"] * dt) % 1

        if game["jump"] > 0 or game["jump_velocity"] > 0:
            game["jump"] += game["jump_velocity"] * dt
            game["jump_velocity"] -= 7.3 * dt
            if game["jump"] <= 0:
                game["jump"] = 0
                game["jump_velocity"] = 0

        game["spawn_timer"] += dt
        if game["spawn_timer"] > max(0.55, 1.05 - game["score"] / 30000):
            game["spawn_timer"] = 0
            spawn_obstacle()

        for obstacle in game["obstacles"][:]:
            obstacle["depth"] += game["speed"] * dt * 0.55

            if 0.84 < obstacle["depth"] < 0.91:
                if obstacle["lane"] == game["lane"] and game["jump"] < 0.42:
                    game["over"] = True

            if obstacle["depth"] > 1.15:
                game["obstacles"].remove(obstacle)

    draw_background()
    draw_road()

    for obstacle in sorted(game["obstacles"], key=lambda item: item["depth"]):
        draw_obstacle(obstacle)

    draw_player()
    draw_hud()

    if game["over"]:
        draw_game_over()

    pygame.display.flip()

pygame.quit()