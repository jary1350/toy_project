import pygame
import random
import math
import numpy as np

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
WIDTH, HEIGHT = 1800, 1600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Solar System Eating Game - Player Controls Earth!")

# Colors
BLACK = (0, 0, 0)
SUN_COLOR = (255, 200, 80)
GLOW_COLOR = (255, 230, 150, 80)  # Semi-transparent glow
SUN_IMPACT_COLOR = (255, 135, 25)
SUN_IMPACT_GLOW_COLOR = (255, 175, 70, 110)
SUN_BLUE_GIANT_COLOR = (145, 214, 255)
SUN_BLUE_GIANT_GLOW_COLOR = (180, 235, 255, 125)
SUN_WHITE_DWARF_COLOR = (240, 248, 255)
SUN_WHITE_DWARF_GLOW_COLOR = (215, 235, 255, 130)
SUN_BLACK_HOLE_GLOW_COLOR = (85, 115, 180, 110)
GHOST_COLOR = (235, 245, 255)
GHOST_EYE_COLOR = (25, 30, 45)
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
MOON_COLOR = (220, 225, 235)
MOON_GLOW_COLOR = (180, 200, 230)

# Sun properties
SUN_BASE_RADIUS = WIDTH // 15
SUN_RADIUS = SUN_BASE_RADIUS
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

# Planet mood/behavior tuning
DEFAULT_PLANET_MOOD = "neutral"
THREAT_DETECTION_BASE = 120
THREAT_DETECTION_PER_RADIUS = 4
THREAT_DETECTION_LEVEL_BONUS = 18
ESCAPE_CHANCE_BASE = 0.30
ESCAPE_CHANCE_PER_LEVEL = 0.10
ESCAPE_CHANCE_MAX = 0.98
ESCAPE_ACCEL_BASE = 0.38
ESCAPE_ACCEL_PER_LEVEL = 0.10
ESCAPE_ACCEL_MAX = 1.60
PLANET_MAX_SPEED = 4.0

# Asteroid properties
NUM_ASTEROIDS = 50
MAX_ASTEROIDS = 1000
ASTEROID_RADIUS = 3
ASTEROID_COLOR = (150, 150, 150)

# Flare properties
FLARE_RADIUS = 5
FLARE_COLOR = (255, 100, 0)  # Orange fireball
FLARE_SPAWN_CHANCE = 0.02  # 2% chance per frame
FLARE_SPEED = 4
SUN_IMPACT_FLARE_MULTIPLIER = 3.8
SUN_IMPACT_BOOST_SECONDS = 5
GAME_FPS = 60
SUN_IMPACT_BOOST_FRAMES = SUN_IMPACT_BOOST_SECONDS * GAME_FPS
SUN_LIFECYCLE_SECONDS = 42
SUN_AGE_MAX_FRAMES = SUN_LIFECYCLE_SECONDS * GAME_FPS
SUN_BLUE_GIANT_START_RATIO = 0.55
SUN_BLUE_GIANT_RADIUS_MULT = 1.85
SUN_WHITE_DWARF_RADIUS_MULT = 0.58
WHITE_DWARF_SECONDS = 5
WHITE_DWARF_MAX_FRAMES = WHITE_DWARF_SECONDS * GAME_FPS
SUN_BLACK_HOLE_RADIUS_MULT = 0.34
SUN_COLLAPSE_FLARE_COUNT = 150
SUN_COLLAPSE_FLARE_SPEED_MIN = 6.5
SUN_COLLAPSE_FLARE_SPEED_MAX = 12.0
COLLAPSE_SHAKE_FRAMES = 28
COLLAPSE_SHAKE_INTENSITY = 20
COLLAPSE_SHOCKWAVE_DURATION = 45
COLLAPSE_SHOCKWAVE_SPEED = 24
BLACK_FLARE_RADIUS = 7
BLACK_FLARE_SPEED = 5.5
BLACK_FLARE_SPAWN_CHANCE = 0.05
BLACK_HOLE_PULL_ACCEL = 0.35
BLACK_HOLE_PULL_SPEED_MIN = 4.5
BLACK_HOLE_PULL_SPEED_MAX = 14.0
BLACK_HOLE_GHOST_COUNT = 3
BLACK_HOLE_GHOST_RADIUS = 18
BLACK_HOLE_GHOST_SPEED_MIN = 2.1
BLACK_HOLE_GHOST_SPEED_MAX = 3.8
BLACK_HOLE_AMBIENCE_INTERVAL = 210
BLACK_HOLE_GHOST_TRAIL_LENGTH = 9
BLACK_HOLE_GHOST_ALPHA_MIN = 80
BLACK_HOLE_GHOST_ALPHA_MAX = 200

# Sun impact splash properties
IMPACT_SPLASH_MIN = 44
IMPACT_SPLASH_MAX = 82
IMPACT_SPLASH_SPEED_MIN = 5.5
IMPACT_SPLASH_SPEED_MAX = 13.0
IMPACT_SPLASH_LIFETIME_MIN = 22
IMPACT_SPLASH_LIFETIME_MAX = 48
IMPACT_DEBRIS_MIN = 28
IMPACT_DEBRIS_MAX = 56
IMPACT_DEBRIS_SPEED_MIN = 2.5
IMPACT_DEBRIS_SPEED_MAX = 7.5
IMPACT_DEBRIS_LIFETIME_MIN = 30
IMPACT_DEBRIS_LIFETIME_MAX = 64

# Planet debris properties (when flares destroy planets)
PLANET_DEBRIS_COUNT_MIN = 26
PLANET_DEBRIS_COUNT_MAX = 52
PLANET_DEBRIS_SPEED_MIN = 2.0
PLANET_DEBRIS_SPEED_MAX = 7.5
PLANET_DEBRIS_LIFETIME_MIN = 26
PLANET_DEBRIS_LIFETIME_MAX = 58

# Moon shield properties
MAX_MOONS = 3
MOON_RADIUS = 5
MOON_ORBIT_GAP = 16
MOON_ORBIT_SPEED_MIN = 0.01
MOON_ORBIT_SPEED_MAX = 0.02
MOON_SLOT_ANGLES = (-math.pi / 2, math.pi / 6, 5 * math.pi / 6)
MOON_DEBRIS_COUNT_MIN = 12
MOON_DEBRIS_COUNT_MAX = 22
MOON_DEBRIS_SPEED_MIN = 2.5
MOON_DEBRIS_SPEED_MAX = 6.5
MOON_DEBRIS_LIFETIME_MIN = 18
MOON_DEBRIS_LIFETIME_MAX = 36
ASTEROIDS_PER_MOON = 5

# Game level
LEVEL = 1
FLARE_FREQUENCY_MULTIPLIER = 1.0

# Wormhole properties
WORMHOLE_RADIUS = 45
WORMHOLE_COOLDOWN_FRAMES = 60


def get_initial_moon_count(name):
    if name in ("Mercury", "Venus"):
        return 0
    if name in ("Earth", "Mars"):
        return 1
    if name in ("Jupiter", "Saturn", "Uranus", "Neptune"):
        return 2
    return 0


def get_initial_moon_slots(name):
    return list(range(get_initial_moon_count(name)))


def sync_moon_count(body):
    body["moons"] = len(body.get("moon_slots", []))


def add_moon_to_body(body):
    moon_slots = body.setdefault("moon_slots", [])
    if len(moon_slots) >= MAX_MOONS:
        sync_moon_count(body)
        return False

    for slot_id in range(MAX_MOONS):
        if slot_id not in moon_slots:
            moon_slots.append(slot_id)
            moon_slots.sort()
            sync_moon_count(body)
            return True

    sync_moon_count(body)
    return False


def remove_moon_from_body(body, slot_id):
    moon_slots = body.get("moon_slots", [])
    if slot_id in moon_slots:
        moon_slots.remove(slot_id)
        sync_moon_count(body)
        return True
    return False


def handle_asteroid_eat(body):
    if body.get("name") == "Asteroid":
        return

    if len(body.get("moon_slots", [])) >= MAX_MOONS:
        body["asteroids_eaten_toward_moon"] = 0
        return

    progress = body.get("asteroids_eaten_toward_moon", 0) + 1
    if progress >= ASTEROIDS_PER_MOON:
        gained = add_moon_to_body(body)
        progress = 0 if gained else progress
    body["asteroids_eaten_toward_moon"] = progress


def get_moon_positions(body):
    moon_slots = body.get("moon_slots", [])
    if not moon_slots:
        return []

    orbit_radius = body["radius"] + MOON_ORBIT_GAP
    base_angle = body.get("moon_orbit_angle", 0.0)
    positions = []

    for slot_id in moon_slots:
        angle = base_angle + MOON_SLOT_ANGLES[slot_id]
        positions.append({
            "slot_id": slot_id,
            "pos": [
                body["pos"][0] + math.cos(angle) * orbit_radius,
                body["pos"][1] + math.sin(angle) * orbit_radius,
            ],
        })

    return positions


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
    body = {"name": name, "pos": list(pos), "vel": list(vel), "radius": radius, "color": color, "active": True}
    if not is_asteroid:
        body["moon_slots"] = get_initial_moon_slots(name)
        body["asteroids_eaten_toward_moon"] = 0
        body["moon_orbit_angle"] = random.uniform(0, 2 * math.pi)
        body["moon_orbit_speed"] = random.uniform(MOON_ORBIT_SPEED_MIN, MOON_ORBIT_SPEED_MAX)
        sync_moon_count(body)
    return body


# Create planets and asteroids
bodies = [create_body(name, radius, color) for name, radius, color in PLANETS_DATA]
num_asteroids = min(int(NUM_ASTEROIDS * (1.5 ** (LEVEL - 1))), MAX_ASTEROIDS)
for _ in range(num_asteroids):
    bodies.append(create_body("Asteroid", ASTEROID_RADIUS, ASTEROID_COLOR, is_asteroid=True))

# Flares list
flares = []

# Two connected wormhole portals
wormholes = [
    {"pos": [200, 200],             "color": (160, 0, 255),  "angle": 0.0},
    {"pos": [WIDTH - 200, HEIGHT - 200], "color": (0, 220, 255), "angle": 0.0},
]


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


def spawn_black_flare():
    """Spawn an invisible black flare from the black hole stage."""
    angle = random.uniform(0, 2 * math.pi)
    speed = random.uniform(BLACK_FLARE_SPEED * 0.85, BLACK_FLARE_SPEED * 1.15)
    return {
        "pos": list(SUN_POS),
        "vel": [math.cos(angle) * speed, math.sin(angle) * speed],
        "radius": BLACK_FLARE_RADIUS,
        "color": BLACK,
        "lifetime": 260,
        "kind": "black",
    }


def spawn_black_hole_ghosts():
    ghosts = []
    for index in range(BLACK_HOLE_GHOST_COUNT):
        angle = (2 * math.pi * index) / BLACK_HOLE_GHOST_COUNT
        distance = SUN_RADIUS + 140 + index * 40
        ghosts.append({
            "pos": [
                SUN_POS[0] + math.cos(angle) * distance,
                SUN_POS[1] + math.sin(angle) * distance,
            ],
            "vel": [0.0, 0.0],
            "speed": random.uniform(BLACK_HOLE_GHOST_SPEED_MIN, BLACK_HOLE_GHOST_SPEED_MAX),
            "phase": random.uniform(0, 2 * math.pi),
            "trail": [],
        })
    return ghosts


def spawn_massive_collapse_wave():
    """Spawn a large radial shock of flares during sun collapse."""
    wave = []
    for i in range(SUN_COLLAPSE_FLARE_COUNT):
        angle = (2 * math.pi * i) / SUN_COLLAPSE_FLARE_COUNT + random.uniform(-0.03, 0.03)
        speed = random.uniform(SUN_COLLAPSE_FLARE_SPEED_MIN, SUN_COLLAPSE_FLARE_SPEED_MAX)
        wave.append({
            "pos": [SUN_POS[0] + math.cos(angle) * max(3, SUN_RADIUS // 3), SUN_POS[1] + math.sin(angle) * max(3, SUN_RADIUS // 3)],
            "vel": [math.cos(angle) * speed, math.sin(angle) * speed],
            "radius": random.randint(4, 8),
            "color": (200, 235, 255),
            "lifetime": random.randint(180, 320),
        })
    return wave


def create_beep_sound(frequency, duration_ms, sample_rate=22050):
    """Create a simple beep sound with given frequency and duration"""
    frames = int(duration_ms * sample_rate / 1000)
    arr = np.sin(2.0 * np.pi * np.arange(frames) * frequency / sample_rate)
    arr = (arr * 32767).astype(np.int16)
    arr = np.repeat(arr.reshape(frames, 1), 2, axis=1)
    sound = pygame.sndarray.make_sound(arr)
    return sound


def create_sharp_explosion_sound(duration_ms=140, sample_rate=22050):
    """Create a short, bright burst for planet impacts on the sun."""
    frames = int(duration_ms * sample_rate / 1000)
    t = np.arange(frames, dtype=np.float32) / sample_rate
    # Sharp attack with a quick decay and noisy edge so it feels explosive.
    envelope = np.exp(-24.0 * t)
    tone = np.sin(2.0 * np.pi * 1700.0 * t) + 0.6 * np.sin(2.0 * np.pi * 2400.0 * t)
    noise = np.random.uniform(-1.0, 1.0, frames).astype(np.float32)
    wave = (0.72 * tone + 0.28 * noise) * envelope
    wave = np.clip(wave, -1.0, 1.0)
    arr = (wave * 32767).astype(np.int16)
    arr = np.repeat(arr.reshape(frames, 1), 2, axis=1)
    return pygame.sndarray.make_sound(arr)


def create_flare_planet_impact_sound(duration_ms=130, sample_rate=22050):
    """Create a crisp crackle burst for flare-to-planet impacts."""
    frames = int(duration_ms * sample_rate / 1000)
    t = np.arange(frames, dtype=np.float32) / sample_rate
    envelope = np.exp(-18.0 * t)
    tone = np.sin(2.0 * np.pi * 1150.0 * t) + 0.45 * np.sin(2.0 * np.pi * 1950.0 * t)
    noise = np.random.uniform(-1.0, 1.0, frames).astype(np.float32)
    wave = (0.6 * tone + 0.4 * noise) * envelope
    wave = np.clip(wave, -1.0, 1.0)
    arr = (wave * 32767).astype(np.int16)
    arr = np.repeat(arr.reshape(frames, 1), 2, axis=1)
    return pygame.sndarray.make_sound(arr)


def create_black_hole_ambience_sound(duration_ms=950, sample_rate=22050):
    """Create an eerie drifting tone for the black hole stage."""
    frames = int(duration_ms * sample_rate / 1000)
    t = np.arange(frames, dtype=np.float32) / sample_rate
    envelope = np.minimum(1.0, t * 7.0) * np.exp(-1.6 * t)
    low = np.sin(2.0 * np.pi * (72.0 + 12.0 * np.sin(2.0 * np.pi * 0.7 * t)) * t)
    high = np.sin(2.0 * np.pi * (410.0 + 55.0 * np.sin(2.0 * np.pi * 0.33 * t)) * t)
    noise = np.random.uniform(-1.0, 1.0, frames).astype(np.float32)
    wave = (0.58 * low + 0.22 * high + 0.20 * noise) * envelope
    wave = np.clip(wave, -1.0, 1.0)
    arr = (wave * 32767).astype(np.int16)
    arr = np.repeat(arr.reshape(frames, 1), 2, axis=1)
    return pygame.sndarray.make_sound(arr)


def create_ghost_capture_sound(duration_ms=220, sample_rate=22050):
    """Create a sharp ghostly shriek for captures."""
    frames = int(duration_ms * sample_rate / 1000)
    t = np.arange(frames, dtype=np.float32) / sample_rate
    envelope = np.exp(-9.0 * t)
    sweep = np.sin(2.0 * np.pi * (880.0 - 430.0 * t) * t)
    undertone = np.sin(2.0 * np.pi * 180.0 * t)
    noise = np.random.uniform(-1.0, 1.0, frames).astype(np.float32)
    wave = (0.56 * sweep + 0.22 * undertone + 0.22 * noise) * envelope
    wave = np.clip(wave, -1.0, 1.0)
    arr = (wave * 32767).astype(np.int16)
    arr = np.repeat(arr.reshape(frames, 1), 2, axis=1)
    return pygame.sndarray.make_sound(arr)


def spawn_sun_impact_splash(impact_pos, normal_vec):
    """Spawn violent plasma jets and heavier debris from a sun impact."""
    splashes = []
    base_angle = math.atan2(normal_vec[1], normal_vec[0])

    plasma_count = random.randint(IMPACT_SPLASH_MIN, IMPACT_SPLASH_MAX)
    for _ in range(plasma_count):
        spread = random.uniform(-1.35, 1.35)
        angle = base_angle + spread
        speed = random.uniform(IMPACT_SPLASH_SPEED_MIN, IMPACT_SPLASH_SPEED_MAX)
        life = random.randint(IMPACT_SPLASH_LIFETIME_MIN, IMPACT_SPLASH_LIFETIME_MAX)
        splashes.append({
            "pos": [impact_pos[0], impact_pos[1]],
            "vel": [math.cos(angle) * speed, math.sin(angle) * speed],
            "radius": random.randint(2, 6),
            "lifetime": life,
            "max_life": life,
            "drag": random.uniform(0.92, 0.97),
            "kind": "plasma",
            "base_color": (255, random.randint(120, 220), random.randint(40, 115)),
        })

    debris_count = random.randint(IMPACT_DEBRIS_MIN, IMPACT_DEBRIS_MAX)
    for _ in range(debris_count):
        spread = random.uniform(-1.8, 1.8)
        angle = base_angle + spread
        speed = random.uniform(IMPACT_DEBRIS_SPEED_MIN, IMPACT_DEBRIS_SPEED_MAX)
        life = random.randint(IMPACT_DEBRIS_LIFETIME_MIN, IMPACT_DEBRIS_LIFETIME_MAX)
        splashes.append({
            "pos": [impact_pos[0], impact_pos[1]],
            "vel": [math.cos(angle) * speed, math.sin(angle) * speed],
            "radius": random.randint(1, 4),
            "lifetime": life,
            "max_life": life,
            "drag": random.uniform(0.90, 0.95),
            "kind": "debris",
            "base_color": (255, random.randint(70, 140), random.randint(15, 45)),
        })

    return splashes


def spawn_planet_debris(body, incoming_velocity):
    """Break a planet into debris chunks when a solar flare hits it."""
    debris = []
    base_angle = math.atan2(incoming_velocity[1], incoming_velocity[0]) if incoming_velocity else random.uniform(0, 2 * math.pi)
    chunk_count = random.randint(PLANET_DEBRIS_COUNT_MIN, PLANET_DEBRIS_COUNT_MAX)
    base_color = body.get("color", (200, 200, 200))

    for _ in range(chunk_count):
        angle = base_angle + random.uniform(-2.2, 2.2)
        speed = random.uniform(PLANET_DEBRIS_SPEED_MIN, PLANET_DEBRIS_SPEED_MAX)
        life = random.randint(PLANET_DEBRIS_LIFETIME_MIN, PLANET_DEBRIS_LIFETIME_MAX)
        debris.append({
            "pos": [body["pos"][0], body["pos"][1]],
            "vel": [math.cos(angle) * speed, math.sin(angle) * speed],
            "radius": random.randint(1, max(2, body["radius"] // 3)),
            "lifetime": life,
            "max_life": life,
            "drag": random.uniform(0.91, 0.96),
            "color": (
                min(255, int(base_color[0] * random.uniform(0.8, 1.2))),
                min(255, int(base_color[1] * random.uniform(0.8, 1.15))),
                min(255, int(base_color[2] * random.uniform(0.8, 1.25))),
            ),
        })

    return debris


def spawn_moon_debris(explosion_pos):
    debris = []
    chunk_count = random.randint(MOON_DEBRIS_COUNT_MIN, MOON_DEBRIS_COUNT_MAX)
    for _ in range(chunk_count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(MOON_DEBRIS_SPEED_MIN, MOON_DEBRIS_SPEED_MAX)
        life = random.randint(MOON_DEBRIS_LIFETIME_MIN, MOON_DEBRIS_LIFETIME_MAX)
        debris.append({
            "pos": [explosion_pos[0], explosion_pos[1]],
            "vel": [math.cos(angle) * speed, math.sin(angle) * speed],
            "radius": random.randint(1, 3),
            "lifetime": life,
            "max_life": life,
            "drag": random.uniform(0.90, 0.95),
            "color": (
                random.randint(200, 255),
                random.randint(200, 240),
                random.randint(210, 255),
            ),
        })
    return debris


# Create sound effects
flare_hit_sound = create_beep_sound(800, 100)  # High pitch, short beep for flare
swallow_sound = create_beep_sound(400, 150)    # Lower pitch, slightly longer for swallow
sun_impact_explosion_sound = create_sharp_explosion_sound()
flare_planet_impact_sound = create_flare_planet_impact_sound()
black_hole_ambience_sound = create_black_hole_ambience_sound()
ghost_capture_sound = create_ghost_capture_sound()

# Sun impact splashes list
sun_impact_splashes = []
sun_impact_boost_timer = 0
planet_debris_particles = []

# Sun lifecycle state
sun_age_frames = 0
sun_collapsed = False
white_dwarf_age_frames = 0
black_hole_active = False
black_hole_ghosts = []
black_hole_ambience_timer = 0
collapse_shockwave = None
camera_shake_timer = 0
camera_shake_intensity = 0


def draw_planet_face(surface, body):
    """Draw a mood-based face for a planet (neutral, worried, happy, sleepy)."""
    x, y = int(body["pos"][0]), int(body["pos"][1])
    r = body["radius"]
    if r < 8:
        return

    mood = body.get("mood", DEFAULT_PLANET_MOOD)
    eye_ox = max(2, r // 3)
    eye_oy = max(2, r // 4)
    eye_r  = max(2, r // 5)
    pup_r  = max(1, eye_r // 2)
    lx, ly = x - eye_ox, y - eye_oy
    rx, ry = x + eye_ox, y - eye_oy

    # Base eye whites
    pygame.draw.circle(surface, (255, 255, 220), (lx, ly), eye_r)
    pygame.draw.circle(surface, (255, 255, 220), (rx, ry), eye_r)

    if mood == "sleepy":
        lid_color = (25, 20, 20)
        pygame.draw.line(surface, lid_color, (lx - eye_r, ly), (lx + eye_r, ly), max(1, r // 8))
        pygame.draw.line(surface, lid_color, (rx - eye_r, ry), (rx + eye_r, ry), max(1, r // 8))
    elif mood == "worried":
        pygame.draw.circle(surface, (15, 10, 10), (lx, ly + pup_r // 2), pup_r)
        pygame.draw.circle(surface, (15, 10, 10), (rx, ry + pup_r // 2), pup_r)
        brow_w = max(1, r // 9)
        pygame.draw.line(surface, (15, 10, 10), (lx - eye_r, ly - eye_r - 2), (lx + eye_r, ly - eye_r), brow_w)
        pygame.draw.line(surface, (15, 10, 10), (rx - eye_r, ry - eye_r), (rx + eye_r, ry - eye_r - 2), brow_w)
    else:
        pygame.draw.circle(surface, (15, 10, 10), (lx, ly), pup_r)
        pygame.draw.circle(surface, (15, 10, 10), (rx, ry), pup_r)

    mouth_w = max(r // 2, 10)
    mouth_h = max(r // 3, 6)
    mouth_rect = pygame.Rect(x - mouth_w // 2, y + r // 8, mouth_w, mouth_h)
    mouth_color = (15, 10, 10)
    mouth_thickness = max(1, r // 8)

    if mood == "happy":
        pygame.draw.arc(surface, mouth_color, mouth_rect, math.pi, 2 * math.pi, mouth_thickness)
    elif mood == "worried":
        wav_y = y + r // 3
        pygame.draw.line(surface, mouth_color, (x - mouth_w // 2, wav_y), (x - mouth_w // 6, wav_y + 2), mouth_thickness)
        pygame.draw.line(surface, mouth_color, (x - mouth_w // 6, wav_y + 2), (x + mouth_w // 6, wav_y - 2), mouth_thickness)
        pygame.draw.line(surface, mouth_color, (x + mouth_w // 6, wav_y - 2), (x + mouth_w // 2, wav_y), mouth_thickness)
    elif mood == "sleepy":
        pygame.draw.line(surface, mouth_color, (x - mouth_w // 3, y + r // 3), (x + mouth_w // 3, y + r // 3), mouth_thickness)
    else:
        # Neutral face: relaxed straight mouth.
        pygame.draw.line(surface, mouth_color, (x - mouth_w // 3, y + r // 3), (x + mouth_w // 3, y + r // 3), mouth_thickness)


def get_threat_vector(body, active_planets, flares, level):
    """Return normalized vector away from nearest threat and whether a threat is nearby."""
    detect_range = (
        THREAT_DETECTION_BASE
        + body["radius"] * THREAT_DETECTION_PER_RADIUS
        + (level - 1) * THREAT_DETECTION_LEVEL_BONUS
    )
    nearest_dist = float("inf")
    away_vec = None

    for other in active_planets:
        if other is body:
            continue
        if other["radius"] <= body["radius"]:
            continue

        dx = body["pos"][0] - other["pos"][0]
        dy = body["pos"][1] - other["pos"][1]
        dist = math.hypot(dx, dy)
        if 0 < dist < detect_range and dist < nearest_dist:
            nearest_dist = dist
            away_vec = (dx / dist, dy / dist)

    for flare in flares:
        dx = body["pos"][0] - flare["pos"][0]
        dy = body["pos"][1] - flare["pos"][1]
        dist = math.hypot(dx, dy)
        if 0 < dist < detect_range and dist < nearest_dist:
            nearest_dist = dist
            away_vec = (dx / dist, dy / dist)

    return away_vec


def is_threat_to_smaller_planet(body, active_planets, level):
    """Return True if this planet is currently menacing any smaller nearby planet."""
    detect_range = (
        THREAT_DETECTION_BASE
        + body["radius"] * THREAT_DETECTION_PER_RADIUS
        + (level - 1) * THREAT_DETECTION_LEVEL_BONUS
    )
    for other in active_planets:
        if other is body:
            continue
        if body["radius"] <= other["radius"]:
            continue

        dx = body["pos"][0] - other["pos"][0]
        dy = body["pos"][1] - other["pos"][1]
        dist = math.hypot(dx, dy)
        if dist < detect_range:
            return True
    return False


def draw_sun_face(surface, is_angry):
    """Draw sleepy or angry expression for the sun based on flare activity."""
    x, y = SUN_POS
    r = SUN_RADIUS
    eye_ox = r // 3
    eye_oy = r // 4
    eye_r = max(3, r // 10)
    face_color = (60, 30, 10)
    mouth_thickness = max(2, r // 14)

    if is_angry:
        # Angry eyes and frown when the sun is actively firing flares.
        pygame.draw.circle(surface, (255, 240, 200), (x - eye_ox, y - eye_oy), eye_r)
        pygame.draw.circle(surface, (255, 240, 200), (x + eye_ox, y - eye_oy), eye_r)
        pygame.draw.circle(surface, face_color, (x - eye_ox + eye_r // 2, y - eye_oy), eye_r // 2)
        pygame.draw.circle(surface, face_color, (x + eye_ox - eye_r // 2, y - eye_oy), eye_r // 2)
        brow_w = max(2, r // 16)
        pygame.draw.line(surface, face_color, (x - eye_ox - eye_r, y - eye_oy - eye_r), (x - eye_ox + eye_r, y - eye_oy - 1), brow_w)
        pygame.draw.line(surface, face_color, (x + eye_ox - eye_r, y - eye_oy - 1), (x + eye_ox + eye_r, y - eye_oy - eye_r), brow_w)
        angry_mouth = pygame.Rect(x - r // 3, y + r // 5, (2 * r) // 3, r // 4)
        pygame.draw.arc(surface, face_color, angry_mouth, 0, math.pi, mouth_thickness)
    else:
        # Sleepy closed eyes and small relaxed mouth when calm.
        lid_w = max(2, r // 12)
        pygame.draw.line(surface, face_color, (x - eye_ox - eye_r, y - eye_oy), (x - eye_ox + eye_r, y - eye_oy), lid_w)
        pygame.draw.line(surface, face_color, (x + eye_ox - eye_r, y - eye_oy), (x + eye_ox + eye_r, y - eye_oy), lid_w)
        pygame.draw.arc(surface, face_color, pygame.Rect(x - r // 5, y + r // 6, (2 * r) // 5, r // 5), math.pi, 2 * math.pi, mouth_thickness)


def draw_wormhole(surface, wh):
    """Draw an animated spinning wormhole portal."""
    x, y  = int(wh["pos"][0]), int(wh["pos"][1])
    r     = WORMHOLE_RADIUS
    color = wh["color"]
    angle = wh["angle"]

    # Dark void centre
    pygame.draw.circle(surface, (5, 0, 18), (x, y), r - 4)

    # Spinning spiral arms
    num_arms = 6
    for i in range(num_arms):
        a     = angle + i * (2 * math.pi / num_arms)
        mid_x = x + int((r // 2) * math.cos(a + 0.5))
        mid_y = y + int((r // 2) * math.sin(a + 0.5))
        end_x = x + int((r - 4)  * math.cos(a))
        end_y = y + int((r - 4)  * math.sin(a))
        pygame.draw.line(surface, color, (x, y), (mid_x, mid_y), 2)
        pygame.draw.line(surface, color, (mid_x, mid_y), (end_x, end_y), 1)

    # Outer glowing rings
    pygame.draw.circle(surface, color, (x, y), r, 3)
    pygame.draw.circle(surface, (220, 220, 255), (x, y), r + 3, 1)

    # Inner pulsing ring
    pulse_r = r - 10 + int(5 * math.sin(angle * 3))
    if pulse_r > 2:
        pygame.draw.circle(surface, color, (x, y), pulse_r, 1)


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
                    num_asteroids = min(int(NUM_ASTEROIDS * (1.5 ** (LEVEL - 1))), MAX_ASTEROIDS)
                    for _ in range(num_asteroids):
                        bodies.append(create_body("Asteroid", ASTEROID_RADIUS, ASTEROID_COLOR, is_asteroid=True))
                    flares.clear()
                    sun_impact_splashes.clear()
                    planet_debris_particles.clear()
                    sun_impact_boost_timer = 0
                    sun_age_frames = 0
                    sun_collapsed = False
                    white_dwarf_age_frames = 0
                    black_hole_active = False
                    black_hole_ghosts.clear()
                    black_hole_ambience_timer = 0
                    SUN_RADIUS = SUN_BASE_RADIUS
                    collapse_shockwave = None
                    camera_shake_timer = 0
                    camera_shake_intensity = 0
                elif game_over:
                    # Restart from level 1
                    LEVEL = 1
                    FLARE_FREQUENCY_MULTIPLIER = 1.0
                    game_over = False
                    level_passed = False
                    # Reset bodies
                    bodies.clear()
                    bodies.extend([create_body(name, radius, color) for name, radius, color in PLANETS_DATA])
                    num_asteroids = min(NUM_ASTEROIDS, MAX_ASTEROIDS)
                    for _ in range(num_asteroids):
                        bodies.append(create_body("Asteroid", ASTEROID_RADIUS, ASTEROID_COLOR, is_asteroid=True))
                    flares.clear()
                    sun_impact_splashes.clear()
                    planet_debris_particles.clear()
                    sun_impact_boost_timer = 0
                    sun_age_frames = 0
                    sun_collapsed = False
                    white_dwarf_age_frames = 0
                    black_hole_active = False
                    black_hole_ghosts.clear()
                    black_hole_ambience_timer = 0
                    SUN_RADIUS = SUN_BASE_RADIUS
                    collapse_shockwave = None
                    camera_shake_timer = 0
                    camera_shake_intensity = 0

    screen.fill(BLACK)

    keys = pygame.key.get_pressed()

    if sun_impact_boost_timer > 0:
        sun_impact_boost_timer -= 1

    if camera_shake_timer > 0:
        camera_shake_timer -= 1

    if collapse_shockwave is not None:
        collapse_shockwave["radius"] += COLLAPSE_SHOCKWAVE_SPEED
        collapse_shockwave["life"] -= 1
        if collapse_shockwave["life"] <= 0:
            collapse_shockwave = None

    if not level_passed and not game_over:
        blue_giant_start = int(SUN_AGE_MAX_FRAMES * SUN_BLUE_GIANT_START_RATIO)
        if black_hole_active:
            SUN_RADIUS = max(10, int(SUN_BASE_RADIUS * SUN_BLACK_HOLE_RADIUS_MULT))
        elif sun_collapsed:
            white_dwarf_age_frames += 1
            SUN_RADIUS = max(16, int(SUN_BASE_RADIUS * SUN_WHITE_DWARF_RADIUS_MULT))
            if white_dwarf_age_frames >= WHITE_DWARF_MAX_FRAMES:
                black_hole_active = True
                black_hole_ghosts = spawn_black_hole_ghosts()
                black_hole_ambience_timer = BLACK_HOLE_AMBIENCE_INTERVAL
                SUN_RADIUS = max(10, int(SUN_BASE_RADIUS * SUN_BLACK_HOLE_RADIUS_MULT))
                collapse_shockwave = {
                    "radius": SUN_RADIUS + 6,
                    "life": COLLAPSE_SHOCKWAVE_DURATION,
                    "max_life": COLLAPSE_SHOCKWAVE_DURATION,
                    "dark": True,
                }
                camera_shake_timer = COLLAPSE_SHAKE_FRAMES
                camera_shake_intensity = COLLAPSE_SHAKE_INTENSITY
                black_hole_ambience_sound.play()
        else:
            sun_age_frames += 1
            if sun_age_frames >= SUN_AGE_MAX_FRAMES:
                sun_collapsed = True
                white_dwarf_age_frames = 0
                SUN_RADIUS = max(16, int(SUN_BASE_RADIUS * SUN_WHITE_DWARF_RADIUS_MULT))
                flares.extend(spawn_massive_collapse_wave())
                sun_impact_explosion_sound.play()
                collapse_shockwave = {
                    "radius": SUN_RADIUS + 8,
                    "life": COLLAPSE_SHOCKWAVE_DURATION,
                    "max_life": COLLAPSE_SHOCKWAVE_DURATION,
                }
                camera_shake_timer = COLLAPSE_SHAKE_FRAMES
                camera_shake_intensity = COLLAPSE_SHAKE_INTENSITY
            elif sun_age_frames >= blue_giant_start:
                # Grow from baseline to giant size before collapse.
                giant_progress = (sun_age_frames - blue_giant_start) / max(1, SUN_AGE_MAX_FRAMES - blue_giant_start)
                giant_progress = max(0.0, min(1.0, giant_progress))
                SUN_RADIUS = int(SUN_BASE_RADIUS * (1.0 + (SUN_BLUE_GIANT_RADIUS_MULT - 1.0) * giant_progress))
            else:
                SUN_RADIUS = SUN_BASE_RADIUS

    # Spawn flares randomly with level-based frequency
    if not level_passed and not game_over:
        if black_hole_active:
            if random.random() < BLACK_FLARE_SPAWN_CHANCE:
                flares.append(spawn_black_flare())
            if black_hole_ambience_timer <= 0:
                black_hole_ambience_sound.play()
                black_hole_ambience_timer = BLACK_HOLE_AMBIENCE_INTERVAL
            else:
                black_hole_ambience_timer -= 1
        else:
            spawn_chance = FLARE_SPAWN_CHANCE * FLARE_FREQUENCY_MULTIPLIER
            if sun_impact_boost_timer > 0:
                spawn_chance *= SUN_IMPACT_FLARE_MULTIPLIER
            if random.random() < spawn_chance:
                flares.append(spawn_flare())

    # Planet face state + threat-response AI
    active_planets = [b for b in bodies if b["active"] and b["name"] != "Asteroid"]
    for body in active_planets:
        body["moon_orbit_angle"] = (body.get("moon_orbit_angle", 0.0) + body.get("moon_orbit_speed", MOON_ORBIT_SPEED_MIN)) % (2 * math.pi)
        mood = DEFAULT_PLANET_MOOD
        away_vec = get_threat_vector(body, active_planets, flares, LEVEL)

        if away_vec is not None:
            mood = "worried"
            if body["name"] != "Earth":
                escape_chance = min(
                    ESCAPE_CHANCE_MAX,
                    ESCAPE_CHANCE_BASE + (LEVEL - 1) * ESCAPE_CHANCE_PER_LEVEL,
                )
                if random.random() < escape_chance:
                    escape_accel = min(
                        ESCAPE_ACCEL_MAX,
                        ESCAPE_ACCEL_BASE + (LEVEL - 1) * ESCAPE_ACCEL_PER_LEVEL,
                    )
                    body["vel"][0] += away_vec[0] * escape_accel
                    body["vel"][1] += away_vec[1] * escape_accel
                    speed = math.hypot(body["vel"][0], body["vel"][1])
                    if speed > PLANET_MAX_SPEED:
                        body["vel"][0] = (body["vel"][0] / speed) * PLANET_MAX_SPEED
                        body["vel"][1] = (body["vel"][1] / speed) * PLANET_MAX_SPEED
        elif is_threat_to_smaller_planet(body, active_planets, LEVEL):
            mood = "happy"

        body["mood"] = mood

    # Update black hole ghosts and let them hunt planets.
    if black_hole_active:
        huntable_planets = [b for b in bodies if b["active"] and b["name"] != "Asteroid" and not b.get("black_hole_pull", False)]
        for ghost in black_hole_ghosts:
            ghost["phase"] = (ghost["phase"] + 0.08) % (2 * math.pi)
            if huntable_planets:
                target = min(
                    huntable_planets,
                    key=lambda body: (ghost["pos"][0] - body["pos"][0]) ** 2 + (ghost["pos"][1] - body["pos"][1]) ** 2,
                )
                dx = target["pos"][0] - ghost["pos"][0]
                dy = target["pos"][1] - ghost["pos"][1]
                dist = math.hypot(dx, dy)
                if dist > 0:
                    wobble_x = math.cos(ghost["phase"]) * 0.65
                    wobble_y = math.sin(ghost["phase"] * 1.3) * 0.65
                    ghost["vel"][0] = (dx / dist) * ghost["speed"] + wobble_x
                    ghost["vel"][1] = (dy / dist) * ghost["speed"] + wobble_y
            else:
                orbit_angle = math.atan2(ghost["pos"][1] - SUN_POS[1], ghost["pos"][0] - SUN_POS[0]) + 0.04
                orbit_radius = max(SUN_RADIUS + 110, math.hypot(ghost["pos"][0] - SUN_POS[0], ghost["pos"][1] - SUN_POS[1]))
                ghost["pos"][0] = SUN_POS[0] + math.cos(orbit_angle) * orbit_radius
                ghost["pos"][1] = SUN_POS[1] + math.sin(orbit_angle) * orbit_radius
                continue

            ghost["pos"][0] += ghost["vel"][0]
            ghost["pos"][1] += ghost["vel"][1]
            ghost["trail"].append((ghost["pos"][0], ghost["pos"][1]))
            if len(ghost["trail"]) > BLACK_HOLE_GHOST_TRAIL_LENGTH:
                ghost["trail"].pop(0)

            for target in huntable_planets[:]:
                dx = ghost["pos"][0] - target["pos"][0]
                dy = ghost["pos"][1] - target["pos"][1]
                sum_r = BLACK_HOLE_GHOST_RADIUS + target["radius"]
                if dx * dx + dy * dy < sum_r * sum_r:
                    planet_debris_particles.extend(spawn_planet_debris(target, ghost["vel"]))
                    for moon_data in get_moon_positions(target):
                        planet_debris_particles.extend(spawn_moon_debris(moon_data["pos"]))
                    target["moon_slots"] = []
                    sync_moon_count(target)
                    target["active"] = False
                    ghost_capture_sound.play()
                    huntable_planets.remove(target)
                    break

    # Update phase: move, bounce, sun collision
    for body in bodies:
        if not body["active"]:
            continue

        if body.get("black_hole_pull", False):
            dx_to_sun = SUN_POS[0] - body["pos"][0]
            dy_to_sun = SUN_POS[1] - body["pos"][1]
            dist_to_sun = math.hypot(dx_to_sun, dy_to_sun)

            if dist_to_sun <= SUN_RADIUS + body["radius"] + 8:
                planet_debris_particles.extend(spawn_planet_debris(body, body["vel"]))
                for moon_data in get_moon_positions(body):
                    planet_debris_particles.extend(spawn_moon_debris(moon_data["pos"]))
                body["moon_slots"] = []
                sync_moon_count(body)
                flare_planet_impact_sound.play()
                body["active"] = False
                continue

            if dist_to_sun > 0:
                pull_speed = min(
                    BLACK_HOLE_PULL_SPEED_MAX,
                    body.get("black_hole_pull_speed", BLACK_HOLE_PULL_SPEED_MIN) + BLACK_HOLE_PULL_ACCEL,
                )
                body["black_hole_pull_speed"] = pull_speed
                body["vel"][0] = (dx_to_sun / dist_to_sun) * pull_speed
                body["vel"][1] = (dy_to_sun / dist_to_sun) * pull_speed
                body["pos"][0] += body["vel"][0]
                body["pos"][1] += body["vel"][1]
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
            if body["name"] != "Asteroid":
                dist = math.sqrt(max(dist_sq, 1e-6))
                nx, ny = dx / dist, dy / dist
                impact_pos = [SUN_POS[0] + nx * SUN_RADIUS, SUN_POS[1] + ny * SUN_RADIUS]
                sun_impact_splashes.extend(spawn_sun_impact_splash(impact_pos, (nx, ny)))
                sun_impact_explosion_sound.play()
                sun_impact_boost_timer = SUN_IMPACT_BOOST_FRAMES
            body["active"] = False

    # Wormhole teleportation
    for body in bodies:
        if not body["active"]:
            continue
        cooldown = body.get("wh_cooldown", 0)
        if cooldown > 0:
            body["wh_cooldown"] = cooldown - 1
            continue
        for idx, wh in enumerate(wormholes):
            dx = body["pos"][0] - wh["pos"][0]
            dy = body["pos"][1] - wh["pos"][1]
            if math.hypot(dx, dy) < WORMHOLE_RADIUS:
                other = wormholes[1 - idx]
                body["pos"][0] = float(other["pos"][0])
                body["pos"][1] = float(other["pos"][1])
                body["wh_cooldown"] = WORMHOLE_COOLDOWN_FRAMES
                break

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

    # Update sun impact splash particles
    for particle in sun_impact_splashes[:]:
        particle["pos"][0] += particle["vel"][0]
        particle["pos"][1] += particle["vel"][1]
        particle["vel"][0] *= particle.get("drag", 0.95)
        particle["vel"][1] *= particle.get("drag", 0.95)
        particle["lifetime"] -= 1

        if particle["lifetime"] <= 0:
            sun_impact_splashes.remove(particle)

    # Update flare-created planet debris particles
    for piece in planet_debris_particles[:]:
        piece["pos"][0] += piece["vel"][0]
        piece["pos"][1] += piece["vel"][1]
        piece["vel"][0] *= piece["drag"]
        piece["vel"][1] *= piece["drag"]
        piece["lifetime"] -= 1

        if piece["lifetime"] <= 0:
            planet_debris_particles.remove(piece)

    # Flare collisions with bodies
    for flare in flares[:]:
        for body in bodies[:]:
            if not body["active"]:
                continue
            if body.get("black_hole_pull", False):
                continue

            flare_kind = flare.get("kind", "solar")

            if flare_kind == "black":
                if body["name"] == "Asteroid":
                    continue

                dx = flare["pos"][0] - body["pos"][0]
                dy = flare["pos"][1] - body["pos"][1]
                sum_r = flare["radius"] + body["radius"]
                if dx * dx + dy * dy < sum_r * sum_r:
                    body["black_hole_pull"] = True
                    body["black_hole_pull_speed"] = BLACK_HOLE_PULL_SPEED_MIN
                    if flare in flares:
                        flares.remove(flare)
                    break
                continue

            if body["name"] != "Asteroid" and body.get("moons", 0) > 0:
                moon_positions = get_moon_positions(body)
                moon_hit = None
                for moon_data in moon_positions:
                    moon_pos = moon_data["pos"]
                    dx = flare["pos"][0] - moon_pos[0]
                    dy = flare["pos"][1] - moon_pos[1]
                    moon_sum_r = flare["radius"] + MOON_RADIUS
                    if dx * dx + dy * dy < moon_sum_r * moon_sum_r:
                        moon_hit = moon_data
                        break

                if moon_hit is not None:
                    remove_moon_from_body(body, moon_hit["slot_id"])
                    planet_debris_particles.extend(spawn_moon_debris(moon_hit["pos"]))
                    flare_planet_impact_sound.play()
                    if flare in flares:
                        flares.remove(flare)
                    break

            dx = flare["pos"][0] - body["pos"][0]
            dy = flare["pos"][1] - body["pos"][1]
            dist_sq = dx * dx + dy * dy
            sum_r = flare["radius"] + body["radius"]
            if dist_sq < sum_r * sum_r:
                if body["name"] != "Asteroid":
                    if body.get("moons", 0) > 0:
                        moon_positions = get_moon_positions(body)
                        impact_moon = min(
                            moon_positions,
                            key=lambda moon_data: (flare["pos"][0] - moon_data["pos"][0]) ** 2 + (flare["pos"][1] - moon_data["pos"][1]) ** 2,
                        )
                        remove_moon_from_body(body, impact_moon["slot_id"])
                        planet_debris_particles.extend(spawn_moon_debris(impact_moon["pos"]))
                        flare_planet_impact_sound.play()
                    else:
                        planet_debris_particles.extend(spawn_planet_debris(body, flare["vel"]))
                        flare_planet_impact_sound.play()
                        body["active"] = False
                else:
                    flare_hit_sound.play()
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
                    if b1["name"] != "Asteroid":
                        if b2["name"] == "Asteroid":
                            handle_asteroid_eat(b1)
                        else:
                            add_moon_to_body(b1)
                    b2["active"] = False
                    swallow_sound.play()
                elif b2["radius"] > b1["radius"]:
                    # b2 eats b1: increase b2's radius by b1's radius
                    b2["radius"] += b1["radius"]
                    if b2["name"] != "Asteroid":
                        if b1["name"] == "Asteroid":
                            handle_asteroid_eat(b2)
                        else:
                            add_moon_to_body(b2)
                    b1["active"] = False
                    swallow_sound.play()
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

    # Update wormhole animation
    for wh in wormholes:
        wh["angle"] = (wh["angle"] + 0.05) % (2 * math.pi)

    # Draw wormholes (behind everything else)
    for wh in wormholes:
        draw_wormhole(screen, wh)

    # Draw Sun with glow
    sun_is_orange = sun_impact_boost_timer > 0
    blue_giant_start = int(SUN_AGE_MAX_FRAMES * SUN_BLUE_GIANT_START_RATIO)
    if black_hole_active:
        sun_color = BLACK
        sun_glow = SUN_BLACK_HOLE_GLOW_COLOR
    elif sun_collapsed:
        sun_color = SUN_WHITE_DWARF_COLOR
        sun_glow = SUN_WHITE_DWARF_GLOW_COLOR
    elif sun_age_frames >= blue_giant_start:
        sun_color = SUN_BLUE_GIANT_COLOR
        sun_glow = SUN_BLUE_GIANT_GLOW_COLOR
    else:
        sun_color = SUN_COLOR
        sun_glow = GLOW_COLOR
    if sun_is_orange and not sun_collapsed and not black_hole_active:
        sun_color = SUN_IMPACT_COLOR
        sun_glow = SUN_IMPACT_GLOW_COLOR
    pygame.draw.circle(screen, sun_color, SUN_POS, SUN_RADIUS)
    pygame.draw.circle(screen, sun_glow, SUN_POS, SUN_RADIUS + 15, 15)
    flare_near_sun = any(
        f.get("kind", "solar") != "black" and math.hypot(f["pos"][0] - SUN_POS[0], f["pos"][1] - SUN_POS[1]) < SUN_RADIUS
        for f in flares
    )
    if not black_hole_active:
        draw_sun_face(screen, is_angry=flare_near_sun)

    # Draw black hole ghosts.
    if black_hole_active:
        ghost_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for ghost in black_hole_ghosts:
            gx, gy = int(ghost["pos"][0]), int(ghost["pos"][1])
            phase_ratio = (math.sin(ghost["phase"] * 1.7) + 1.0) / 2.0
            ghost_alpha = int(BLACK_HOLE_GHOST_ALPHA_MIN + (BLACK_HOLE_GHOST_ALPHA_MAX - BLACK_HOLE_GHOST_ALPHA_MIN) * phase_ratio)

            for index, trail_pos in enumerate(ghost["trail"]):
                trail_ratio = (index + 1) / max(1, len(ghost["trail"]))
                trail_alpha = int(ghost_alpha * trail_ratio * 0.35)
                trail_radius = max(4, int(BLACK_HOLE_GHOST_RADIUS * (0.45 + 0.35 * trail_ratio)))
                tx, ty = int(trail_pos[0]), int(trail_pos[1])
                pygame.draw.circle(ghost_overlay, (*GHOST_COLOR, trail_alpha), (tx, ty), trail_radius)

            body_rect = pygame.Rect(gx - BLACK_HOLE_GHOST_RADIUS, gy - BLACK_HOLE_GHOST_RADIUS, BLACK_HOLE_GHOST_RADIUS * 2, BLACK_HOLE_GHOST_RADIUS * 2)
            pygame.draw.ellipse(ghost_overlay, (*GHOST_COLOR, ghost_alpha), body_rect)
            skirt_y = gy + BLACK_HOLE_GHOST_RADIUS // 2
            for offset in (-10, 0, 10):
                pygame.draw.circle(ghost_overlay, (*GHOST_COLOR, ghost_alpha), (gx + offset, skirt_y), 6)
            eye_alpha = min(255, ghost_alpha + 25)
            pygame.draw.circle(ghost_overlay, (*GHOST_EYE_COLOR, eye_alpha), (gx - 5, gy - 2), 2)
            pygame.draw.circle(ghost_overlay, (*GHOST_EYE_COLOR, eye_alpha), (gx + 5, gy - 2), 2)
        screen.blit(ghost_overlay, (0, 0))

    # Draw collapse shockwave ring.
    if collapse_shockwave is not None:
        life_ratio = collapse_shockwave["life"] / max(1, collapse_shockwave["max_life"])
        if collapse_shockwave.get("dark"):
            ring_color = (
                min(255, max(0, int(80 * life_ratio + 10))),
                min(255, max(0, int(110 * life_ratio + 20))),
                min(255, max(0, int(190 * life_ratio + 35))),
            )
        else:
            ring_color = (
                255,
                min(255, max(0, int(210 * life_ratio + 30))),
                min(255, max(0, int(255 * life_ratio + 20))),
            )
        ring_thickness = max(2, int(12 * life_ratio))
        pygame.draw.circle(screen, ring_color, SUN_POS, int(collapse_shockwave["radius"]), ring_thickness)

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

        # Mood face on planets (skip tiny asteroids)
        if body["name"] != "Asteroid":
            for moon_data in get_moon_positions(body):
                moon_pos = moon_data["pos"]
                mx, my = int(moon_pos[0]), int(moon_pos[1])
                pygame.draw.circle(screen, MOON_COLOR, (mx, my), MOON_RADIUS)
                pygame.draw.circle(screen, MOON_GLOW_COLOR, (mx, my), MOON_RADIUS + 2, 1)
            draw_planet_face(screen, body)

    # Draw flares
    for flare in flares:
        if flare.get("kind", "solar") == "black":
            continue
        x, y = int(flare["pos"][0]), int(flare["pos"][1])
        pygame.draw.circle(screen, flare["color"], (x, y), flare["radius"])
        # Add glow effect to flares
        pygame.draw.circle(screen, (255, 150, 50, 100), (x, y), flare["radius"] + 5, 2)

    # Draw sun impact splash fragments
    for particle in sun_impact_splashes:
        life_ratio = particle["lifetime"] / max(1, particle["max_life"])
        x, y = int(particle["pos"][0]), int(particle["pos"][1])
        r = max(1, int(particle["radius"] * life_ratio + 1))
        base_r, base_g, base_b = particle.get("base_color", (255, 160, 70))
        brightness = 0.45 + 0.75 * life_ratio
        color = (
            min(255, int(base_r * brightness)),
            min(255, int(base_g * brightness)),
            min(255, int(base_b * brightness)),
        )
        pygame.draw.circle(screen, color, (x, y), r)
        if particle.get("kind") == "plasma" and life_ratio > 0.2:
            pygame.draw.circle(screen, (255, min(255, color[1] + 35), min(255, color[2] + 20)), (x, y), r + 2, 1)

    # Draw planet debris created by flare impacts
    for piece in planet_debris_particles:
        life_ratio = piece["lifetime"] / max(1, piece["max_life"])
        x, y = int(piece["pos"][0]), int(piece["pos"][1])
        r = max(1, int(piece["radius"] * (0.55 + life_ratio)))
        c = piece["color"]
        color = (
            min(255, int(c[0] * (0.5 + life_ratio))),
            min(255, int(c[1] * (0.5 + life_ratio))),
            min(255, int(c[2] * (0.5 + life_ratio))),
        )
        pygame.draw.circle(screen, color, (x, y), r)

    # Display level
    level_text = font.render(f"Level: {LEVEL}", True, (255, 255, 255))
    screen.blit(level_text, (10, 10))

    # Sun aging countdown and phase display
    if black_hole_active:
        black_hole_text = font.render("Final stage: Black Hole", True, (130, 170, 255))
        screen.blit(black_hole_text, (10, 45))
    elif sun_collapsed:
        seconds_left = max(0, math.ceil((WHITE_DWARF_MAX_FRAMES - white_dwarf_age_frames) / GAME_FPS))
        countdown_text = font.render(f"Black Hole in: {seconds_left}s", True, (210, 235, 255))
        screen.blit(countdown_text, (10, 45))
    else:
        seconds_left = max(0, math.ceil((SUN_AGE_MAX_FRAMES - sun_age_frames) / GAME_FPS))
        countdown_text = font.render(f"Sun Collapse in: {seconds_left}s", True, (180, 220, 255))
        screen.blit(countdown_text, (10, 45))

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

    # Camera shake post-process for collapse event.
    if camera_shake_timer > 0:
        fade = camera_shake_timer / max(1, COLLAPSE_SHAKE_FRAMES)
        amplitude = max(1, int(camera_shake_intensity * fade))
        shake_x = random.randint(-amplitude, amplitude)
        shake_y = random.randint(-amplitude, amplitude)
        shaken_frame = screen.copy()
        screen.fill(BLACK)
        screen.blit(shaken_frame, (shake_x, shake_y))

    pygame.display.flip()
    clock.tick(GAME_FPS)

pygame.quit()