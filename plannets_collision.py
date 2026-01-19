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
    ("Mercury", 5, GRAY),
    ("Venus", 12, ORANGE),
    ("Earth", 13, GREEN),
    ("Mars", 7, RED),
    ("Jupiter", 50, PEACH),
    ("Saturn", 40, SATURN_COLOR),
    ("Uranus", 20, CYAN),
    ("Neptune", 20, BLUE)
]

# Asteroid properties
NUM_ASTEROIDS = 50
ASTEROID_RADIUS = 3
ASTEROID_COLOR = (150, 150, 150)


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
for _ in range(NUM_ASTEROIDS):
    bodies.append(create_body("Asteroid", ASTEROID_RADIUS, ASTEROID_COLOR, is_asteroid=True))


def check_collision(body1, body2):
    dx = body1["pos"][0] - body2["pos"][0]
    dy = body1["pos"][1] - body2["pos"][1]
    dist_sq = dx * dx + dy * dy
    sum_r = body1["radius"] + body2["radius"]
    return dist_sq < sum_r * sum_r


# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)

    keys = pygame.key.get_pressed()

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

    # Planet/Asteroid collisions (only among active survivors)
    active_bodies = [b for b in bodies if b["active"]]
    for i in range(len(active_bodies)):
        for j in range(i + 1, len(active_bodies)):
            b1 = active_bodies[i]
            b2 = active_bodies[j]
            if check_collision(b1, b2):
                if b1["radius"] > b2["radius"]:
                    b2["active"] = False
                elif b2["radius"] > b1["radius"]:
                    b1["active"] = False
                # Equal size: both survive

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

    # Prune inactive bodies
    bodies[:] = [b for b in bodies if b["active"]]

    pygame.display.flip()
    clock.tick(60)

pygame.quit()