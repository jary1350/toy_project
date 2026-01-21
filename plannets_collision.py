import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Solar System Eating Game - Player Controls Earth!")

# Colors
BLACK = (0, 0, 0)
SUN_COLOR = (255, 200, 80)
GLOW_COLOR = (255, 230, 150, 80)  # Semi-transparent glow
SATURN_COLOR = (180, 140, 60)  # Yellowish-brown
RING_COLOR = (220, 200, 180)  # Saturn rings
URANUS_RING_COLOR = (180, 220, 255)  # Uranus rings

GREEN = (0, 180, 0)  # Earth
BLUE = (30, 144, 255)  # Neptune
PEACH = (255, 218, 185)  # Jupiter
RED = (220, 20, 60)  # Mars
ORANGE = (255, 140, 0)  # Venus
CYAN = (0, 255, 255)  # Uranus body
GRAY = (169, 169, 169)  # Mercury

# Sun properties
SUN_RADIUS = WIDTH // 15
SUN_POS = (WIDTH // 2, HEIGHT // 2)

# Earth control settings
EARTH_SPEED = 5.0

# Planet data
PLANETS_DATA = [
    ("Mercury", 10, GRAY),
    ("Venus", 12, ORANGE),
    ("Earth", 14, GREEN),
    ("Mars", 10, RED),
    ("Jupiter", 50, PEACH),
    ("Saturn", 40, SATURN_COLOR),
    ("Uranus", 24, CYAN),
    ("Neptune", 20, BLUE)
]

# Asteroid properties
NUM_ASTEROIDS = 50
ASTEROID_RADIUS = 3
ASTEROID_COLOR = (150, 150, 150)

# Flare properties
FLARE_RADIUS = 5
FLARE_COLOR = (255, 100, 0)  # Orange fireball
FLARE_SPAWN_CHANCE = 0.02  # 2% chance per frame
FLARE_SPEED = 4

# Game level
LEVEL = 1
FLARE_FREQUENCY_MULTIPLIER = 1.0


def create_body(name, radius, color, is_asteroid=False):
    if is_asteroid:
        distance = random.uniform(150, 250)
        angle = random.uniform(0, 2 * math.pi)
        pos = (
            SUN_POS[0] + distance * math.cos(angle),
            SUN_POS[1] + distance * math.sin(angle)
        )
    else:
        # Avoid spawning too close to sun
        while True:
            pos = (random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))
            dist = math.hypot(pos[0] - SUN_POS[0], pos[1] - SUN_POS[1])
            if dist > SUN_RADIUS + radius + 20:
                break

    vel = (random.uniform(-2, 2), random.uniform(-2, 2))
    return {"name": name, "pos": list(pos), "vel": list(vel), "radius": radius, "color": color, "active": True}


# Create planets and asteroids
bodies = [create_body(name, radius, color) for name, radius, color in PLANETS_DATA]
for _ in range(int(NUM_ASTEROIDS * (1.5 ** (LEVEL - 1)))):
    bodies.append(create_body("Asteroid", ASTEROID_RADIUS, ASTEROID_COLOR, is_asteroid=True))

# Flares list
flares = []


def check_collision(body1, body2):
    dx = body1["pos"][0] - body2["pos"][0]
    dy = body1["pos"][1] - body2["pos"][1]
    dist_sq = dx * dx + dy * dy
    sum_r = body1["radius"] + body2["radius"]
    return dist_sq < sum_r * sum_r


def spawn_flare():
    """Spawn a flare from the sun in a random direction"""
    angle = random.uniform(0, 2 * math.pi)
    vel = (FLARE_SPEED * math.cos(angle), FLARE_SPEED * math.sin(angle))
    flare = {
        "pos": list(SUN_POS),
        "vel": vel,
        "radius": FLARE_RADIUS,
        "color": FLARE_COLOR,
        "lifetime": 300  # Frames until flare expires
    }
    return flare


# Main game loop
running = True
clock = pygame.time.Clock()
game_over = False
level_passed = False
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if level_passed:
                    # Next level
                    LEVEL += 1
                    FLARE_FREQUENCY_MULTIPLIER = 1.0 * (1.5 ** (LEVEL - 1))
                    level_passed = False
                    game_over = False
                    # Reset bodies with new counts
                    bodies.clear()
                    bodies.extend([create_body(name, radius, color) for name, radius, color in PLANETS_DATA])
                    for _ in range(int(NUM_ASTEROIDS * (1.5 ** (LEVEL - 1)))):
                        bodies.append(create_body("Asteroid", ASTEROID_RADIUS, ASTEROID_COLOR, is_asteroid=True))
                    flares.clear()
                elif game_over:
                    # Restart from level 1
                    LEVEL = 1
                    FLARE_FREQUENCY_MULTIPLIER = 1.0
                    game_over = False
                    level_passed = False
                    # Reset bodies
                    bodies.clear()
                    bodies.extend([create_body(name, radius, color) for name, radius, color in PLANETS_DATA])
                    for _ in range(NUM_ASTEROIDS):
                        bodies.append(create_body("Asteroid", ASTEROID_RADIUS, ASTEROID_COLOR, is_asteroid=True))
                    flares.clear()

    screen.fill(BLACK)

    keys = pygame.key.get_pressed()

    # Spawn flares randomly with level-based frequency
    if not level_passed and not game_over:
        spawn_chance = FLARE_SPAWN_CHANCE * FLARE_FREQUENCY_MULTIPLIER
        if random.random() < spawn_chance:
            flares.append(spawn_flare())

    # Update phase: move, bounce, sun collision
    for body in bodies:
        if not body["active"]:
            continue

        # Earth player controls (arrows or WASD)
        if body["name"] == "Earth":
            vx, vy = 0.0, 0.0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                vx -= 1.0
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                vx += 1.0
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                vy -= 1.0
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                vy += 1.0

            mag = math.sqrt(vx * vx + vy * vy)
            if mag > 0:
                vx = (vx / mag) * EARTH_SPEED
                vy = (vy / mag) * EARTH_SPEED
            body["vel"][0] = vx
            body["vel"][1] = vy

        # Update position
        body["pos"][0] += body["vel"][0]
        body["pos"][1] += body["vel"][1]

        # Bounce off edges with clamping
        if body["pos"][0] - body["radius"] < 0:
            body["pos"][0] = body["radius"]
            body["vel"][0] *= -1
        elif body["pos"][0] + body["radius"] > WIDTH:
            body["pos"][0] = WIDTH - body["radius"]
            body["vel"][0] *= -1

        if body["pos"][1] - body["radius"] < 0:
            body["pos"][1] = body["radius"]
            body["vel"][1] *= -1
        elif body["pos"][1] + body["radius"] > HEIGHT:
            body["pos"][1] = HEIGHT - body["radius"]
            body["vel"][1] *= -1

        # Sun collision check (optimized)
        dx = body["pos"][0] - SUN_POS[0]
        dy = body["pos"][1] - SUN_POS[1]
        dist_sq = dx * dx + dy * dy
        sum_r = SUN_RADIUS + body["radius"]
        if dist_sq < sum_r * sum_r:
            body["active"] = False

    # Update flares
    for flare in flares[:]:
        flare["pos"][0] += flare["vel"][0]
        flare["pos"][1] += flare["vel"][1]
        flare["lifetime"] -= 1

        # Remove flare if it goes off screen or expires
        if (flare["pos"][0] < -FLARE_RADIUS or flare["pos"][0] > WIDTH + FLARE_RADIUS or
            flare["pos"][1] < -FLARE_RADIUS or flare["pos"][1] > HEIGHT + FLARE_RADIUS or
            flare["lifetime"] <= 0):
            flares.remove(flare)

    # Flare collisions with bodies
    for flare in flares[:]:
        for body in bodies[:]:
            if not body["active"]:
                continue
            dx = flare["pos"][0] - body["pos"][0]
            dy = flare["pos"][1] - body["pos"][1]
            dist_sq = dx * dx + dy * dy
            sum_r = flare["radius"] + body["radius"]
            if dist_sq < sum_r * sum_r:
                body["active"] = False
                if flare in flares:
                    flares.remove(flare)
                break

    # Planet/Asteroid collisions (only among active survivors)
    active_bodies = [b for b in bodies if b["active"]]
    for i in range(len(active_bodies)):
        for j in range(i + 1, len(active_bodies)):
            b1 = active_bodies[i]
            b2 = active_bodies[j]
            if check_collision(b1, b2):
                if b1["radius"] > b2["radius"]:
                    # b1 eats b2: increase b1's radius by b2's radius
                    b1["radius"] += b2["radius"]
                    b2["active"] = False
                elif b2["radius"] > b1["radius"]:
                    # b2 eats b1: increase b2's radius by b1's radius
                    b2["radius"] += b1["radius"]
                    b1["active"] = False
                # Equal size: both survive

    # Check win condition
    active_bodies = [b for b in bodies if b["active"]]
    earth_alive = any(b for b in active_bodies if b["name"] == "Earth")
    planets_alive = [b for b in active_bodies if b["name"] != "Asteroid"]
    
    if earth_alive and len(planets_alive) == 1:
        # Only Earth remains - Level passed!
        level_passed = True
    elif not earth_alive:
        # Earth destroyed - Game Over
        game_over = True

    # Draw Sun with glow
    pygame.draw.circle(screen, SUN_COLOR, SUN_POS, SUN_RADIUS)
    pygame.draw.circle(screen, GLOW_COLOR, SUN_POS, SUN_RADIUS + 15, 15)

    # Draw active bodies
    active_bodies = [b for b in bodies if b["active"]]  # Refresh after collisions
    for body in active_bodies:
        x, y = int(body["pos"][0]), int(body["pos"][1])
        pygame.draw.circle(screen, body["color"], (x, y), body["radius"])

        # Saturn rings
        if body["name"] == "Saturn":
            for r in range(body["radius"] + 10, body["radius"] + 28, 5):
                pygame.draw.circle(screen, RING_COLOR, (x, y), r, 3)

        # Uranus rings (faint)
        if body["name"] == "Uranus":
            for r in range(body["radius"] + 6, body["radius"] + 18, 4):
                pygame.draw.circle(screen, URANUS_RING_COLOR, (x, y), r, 1)

    # Draw flares
    for flare in flares:
        x, y = int(flare["pos"][0]), int(flare["pos"][1])
        pygame.draw.circle(screen, flare["color"], (x, y), flare["radius"])
        # Add glow effect to flares
        pygame.draw.circle(screen, (255, 150, 50, 100), (x, y), flare["radius"] + 5, 2)

    # Display level
    level_text = font.render(f"Level: {LEVEL}", True, (255, 255, 255))
    screen.blit(level_text, (10, 10))

    # Draw level passed or game over message
    if level_passed:
        success_text = large_font.render("SUCCESS!", True, (0, 255, 0))
        passed_text = font.render("Level Passed!", True, (0, 255, 0))
        space_text = font.render("Press SPACE to continue", True, (255, 255, 255))
        screen.blit(success_text, (WIDTH // 2 - 180, HEIGHT // 2 - 80))
        screen.blit(passed_text, (WIDTH // 2 - 120, HEIGHT // 2))
        screen.blit(space_text, (WIDTH // 2 - 140, HEIGHT // 2 + 60))
    elif game_over:
        gameover_text = large_font.render("GAME OVER", True, (255, 0, 0))
        dead_text = font.render("Earth destroyed!", True, (255, 0, 0))
        level_gameover_text = font.render(f"Level: {LEVEL}", True, (255, 255, 100))
        restart_text = font.render("Press SPACE to restart from Level 1", True, (255, 255, 255))
        screen.blit(gameover_text, (WIDTH // 2 - 200, HEIGHT // 2 - 80))
        screen.blit(dead_text, (WIDTH // 2 - 130, HEIGHT // 2 - 10))
        screen.blit(level_gameover_text, (WIDTH // 2 - 80, HEIGHT // 2 + 40))
        screen.blit(restart_text, (WIDTH // 2 - 180, HEIGHT // 2 + 90))

    # Prune inactive bodies
    bodies[:] = [b for b in bodies if b["active"]]

    pygame.display.flip()
    clock.tick(60)

pygame.quit()