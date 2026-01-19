import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Solar System Eating Game - Updated")

# Colors
BLACK = (0, 0, 0)
YELLOW = (255, 215, 0)  # Bright sun
SUN_COLOR = (255, 200, 80)  # Slightly softer sun color
SATURN_COLOR = (180, 140, 60)  # Yellowish-brown
RING_COLOR = (220, 200, 180)  # Light creamy rings for Saturn
URANUS_RING_COLOR = (180, 220, 255)  # Pale cyan-ish rings for Uranus

GREEN = (0, 180, 0)  # Earth
BLUE = (30, 144, 255)  # Neptune
PEACH = (255, 218, 185)  # Jupiter
RED = (220, 20, 60)  # Mars
ORANGE = (255, 140, 0)  # Venus
CYAN = (0, 255, 255)  # Uranus body
GRAY = (169, 169, 169)  # Mercury

# Sun properties - now 1/15 of width
SUN_RADIUS = WIDTH // 15  # ≈53 pixels on 800px screen
SUN_POS = (WIDTH // 2, HEIGHT // 2)

# Planet data (name, radius, color)
PLANETS_DATA = [
    ("Mercury", 5, GRAY),
    ("Venus", 12, ORANGE),
    ("Earth", 13, GREEN),
    ("Mars", 7, RED),
    ("Jupiter", 50, PEACH),
    ("Saturn", 40, SATURN_COLOR),  # Now yellowish-brown
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
        pos = (random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))

    vel = (random.uniform(-2, 2), random.uniform(-2, 2))
    return {"name": name, "pos": list(pos), "vel": list(vel), "radius": radius, "color": color, "active": True}


# Create planets and asteroids
bodies = [create_body(name, radius, color) for name, radius, color in PLANETS_DATA]

for _ in range(NUM_ASTEROIDS):
    bodies.append(create_body("Asteroid", ASTEROID_RADIUS, ASTEROID_COLOR, is_asteroid=True))


def check_collision(body1, body2):
    dx = body1["pos"][0] - body2["pos"][0]
    dy = body1["pos"][1] - body2["pos"][1]
    distance = math.sqrt(dx ** 2 + dy ** 2)
    return distance < body1["radius"] + body2["radius"]


# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)

    # Draw Sun (bigger but still reasonable size)
    pygame.draw.circle(screen, SUN_COLOR, SUN_POS, SUN_RADIUS)
    # Slight glow effect
    pygame.draw.circle(screen, (255, 230, 150, 120), SUN_POS, SUN_RADIUS + 12, 12)

    active_bodies = [body for body in bodies if body["active"]]

    for body in active_bodies:
        # Update position
        body["pos"][0] += body["vel"][0]
        body["pos"][1] += body["vel"][1]

        # Bounce off edges
        if body["pos"][0] - body["radius"] < 0 or body["pos"][0] + body["radius"] > WIDTH:
            body["vel"][0] = -body["vel"][0]
        if body["pos"][1] - body["radius"] < 0 or body["pos"][1] + body["radius"] > HEIGHT:
            body["vel"][1] = -body["vel"][1]

        # Check collision with sun
        dx = body["pos"][0] - SUN_POS[0]
        dy = body["pos"][1] - SUN_POS[1]
        distance_to_sun = math.sqrt(dx ** 2 + dy ** 2)
        if distance_to_sun < SUN_RADIUS + body["radius"]:
            body["active"] = False
            continue

        # Draw body
        x, y = int(body["pos"][0]), int(body["pos"][1])
        pygame.draw.circle(screen, body["color"], (x, y), body["radius"])

        # Draw rings for Saturn
        if body["name"] == "Saturn":
            for r in range(body["radius"] + 10, body["radius"] + 28, 5):
                pygame.draw.circle(screen, RING_COLOR, (x, y), r, 3)

        # Draw rings for Uranus (fainter, thinner)
        if body["name"] == "Uranus":
            for r in range(body["radius"] + 6, body["radius"] + 18, 4):
                pygame.draw.circle(screen, URANUS_RING_COLOR, (x, y), r, 1)

    # Handle collisions between bodies
    i = 0
    while i < len(active_bodies):
        j = i + 1
        while j < len(active_bodies):
            if check_collision(active_bodies[i], active_bodies[j]):
                if active_bodies[i]["radius"] > active_bodies[j]["radius"]:
                    active_bodies[j]["active"] = False
                elif active_bodies[j]["radius"] > active_bodies[i]["radius"]:
                    active_bodies[i]["active"] = False
            j += 1
        i += 1

    # Keep only active bodies
    bodies = [body for body in bodies if body["active"]]

    pygame.display.flip()
    clock.tick(60)

pygame.quit()