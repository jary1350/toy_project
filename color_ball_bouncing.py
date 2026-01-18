import pygame
import pymunk
import random
import math


# --- Configuration ---
WIDTH, HEIGHT = 1000, 1600  # Increased width for the UI panel
GAME_WIDTH = 800
FPS = 60
GRAVITY = 900.0
MARBLE_RADIUS = 10
PIN_RADIUS = 5
MONSTER_RADIUS = 20  # 2x marble radius
MONSTER_SPEED = 200  # pixels per second
MONSTER_Y = 400  # Center height
MAX_SURVIVOR_DISPLAY = 200

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (40, 40, 40)
BG_COLOR = (100, 149, 237)
FIRE_COLOR = (255, 69, 0)
SAFE_COLOR = (50, 205, 50)
PANEL_COLOR = (50, 50, 50)

# Add these near MONSTER_SPEED etc.
BAR_WIDTH = 180  # wider than monster
BAR_HEIGHT = 12
BAR_SPEED = MONSTER_SPEED * 2  # 2× monster speed
BAR_Y = HEIGHT - 60  # just above the fire/safe zones


class MarbleSurvival:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18)
        self.big_font = pygame.font.SysFont("Arial", 24, bold=True)

        self.space = pymunk.Space()
        self.space.gravity = (0, GRAVITY)

        # Collision handler: monster eats marbles (type 1: marbles, type 2: monster)
        def marble_monster_collision(arbiter, space, data):
            shapes = arbiter.shapes
            for shape in shapes:
                if hasattr(shape, 'custom_color'):  # Marble
                    space.remove(shape.body, shape)
                    break
            arbiter.process_collision = False
            return

        # Bar bounce handler (collision_type 1 = marble, 3 = bar)
        def bar_bounce(arbiter, space, data):
            shape_a, shape_b = arbiter.shapes
            marble = shape_a if hasattr(shape_a, 'custom_color') else shape_b

            # Strong upward impulse
            impulse_strength = 1200
            marble.body.apply_impulse_at_local_point((0, -impulse_strength), (0, 0))

            # Optional: tiny random horizontal kick for chaos
            # marble.body.apply_impulse_at_local_point((random.uniform(-80, 80), 0), (0, 0))

            return True  # normal collision still happens

        self.space.on_collision(collision_type_a=1, collision_type_b=3, begin=bar_bounce)

        self.space.on_collision(collision_type_a=1, collision_type_b=2, begin=marble_monster_collision)

        self.marbles = []
        self.survivors = []
        self.pins = []
        self.current_colors = [(random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)) for _ in range(1_000)]
        self.round_count = 1

        self.create_boundaries()
        self.create_pins()
        self.create_monster()
        self.create_bouncing_bar()
        self.start_level()



    def create_boundaries(self):
        # Walls
        walls = [
            pymunk.Segment(self.space.static_body, (0, 0), (0, HEIGHT), 5),
            pymunk.Segment(self.space.static_body, (GAME_WIDTH, 0), (GAME_WIDTH, HEIGHT), 5)
        ]
        for wall in walls:
            wall.elasticity, wall.friction = 0.5, 0.5
            self.space.add(wall)

    def create_pins(self):
        for row in range(20):
            for col in range(15):
                x = (col * 50) + 50 + (25 if row % 2 == 0 else 0)
                y = (row * 60) + 150
                body = self.space.static_body
                shape = pymunk.Circle(body, PIN_RADIUS, (x, y))
                shape.elasticity = 0.8
                shape.color = WHITE
                self.space.add(shape)
                self.pins.append(shape)

    def create_monster(self):
        # Kinematic body for smooth patrol movement
        self.monster_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.monster_body.position = (GAME_WIDTH // 4, MONSTER_Y)  # Start leftish
        self.monster_shape = pymunk.Circle(self.monster_body, MONSTER_RADIUS)
        self.monster_shape.collision_type = 2
        self.monster_shape.elasticity = 0.9
        self.monster_shape.friction = 0.5
        self.space.add(self.monster_body, self.monster_shape)

        self.monster_dir = 1  # 1: right, -1: left
        self.monster_left_bound = MONSTER_RADIUS + 20
        self.monster_right_bound = GAME_WIDTH - MONSTER_RADIUS - 20

    def create_bouncing_bar(self):
        self.bar_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.bar_body.position = (GAME_WIDTH // 2, BAR_Y)

        self.bar_shape = pymunk.Segment(
            self.bar_body,
            (-BAR_WIDTH // 2, 0),
            (BAR_WIDTH // 2, 0),
            BAR_HEIGHT // 2
        )
        self.bar_shape.elasticity = 0.9  # quite bouncy
        self.bar_shape.friction = 0.3
        self.bar_shape.collision_type = 3  # new type for bar

        self.space.add(self.bar_body, self.bar_shape)

        # Movement direction (same style as monster)
        self.bar_dir = 1  # 1 = right, -1 = left
        self.bar_left_bound = BAR_WIDTH // 2 + 40
        self.bar_right_bound = GAME_WIDTH - BAR_WIDTH // 2 - 40

    def update_bouncing_bar(self, dt):
        self.bar_body.velocity = (BAR_SPEED * self.bar_dir, 0)

        pos_x = self.bar_body.position.x

        if pos_x <= self.bar_left_bound:
            self.bar_dir = 1
            self.bar_body.position = (self.bar_left_bound, BAR_Y)
        elif pos_x >= self.bar_right_bound:
            self.bar_dir = -1
            self.bar_body.position = (self.bar_right_bound, BAR_Y)

    def update_monster(self, dt):
        self.monster_body.velocity = (MONSTER_SPEED * self.monster_dir, 0)
        pos_x = self.monster_body.position.x
        if pos_x <= self.monster_left_bound:
            self.monster_dir = 1
            self.monster_body.position = (self.monster_left_bound, MONSTER_Y)
        elif pos_x >= self.monster_right_bound:
            self.monster_dir = -1
            self.monster_body.position = (self.monster_right_bound, MONSTER_Y)

    def start_level(self):
        """Resets the game with the current pool of colors."""
        # Clean up old marbles
        for m in self.marbles:
            self.space.remove(m.body, m)
        self.marbles = []
        self.survivors = []

        # Spawn new generation
        for color in self.current_colors:
            self.add_marble(color)

    def add_marble(self, color):
        mass = 1
        moment = pymunk.moment_for_circle(mass, 0, MARBLE_RADIUS)
        body = pymunk.Body(mass, moment)
        body.position = (random.randint(50, GAME_WIDTH - 50), random.randint(-200, -50))
        shape = pymunk.Circle(body, MARBLE_RADIUS)
        shape.collision_type = 1
        shape.elasticity, shape.friction = 0.6, 0.5
        shape.custom_color = color
        self.space.add(body, shape)
        self.marbles.append(shape)

    def run(self):
        running = True
        button_rect = pygame.Rect(GAME_WIDTH + 20, HEIGHT - 60, 160, 40)
        dt = 1 / FPS

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint(event.pos) and self.survivors:
                        self.current_colors = list(set(self.survivors))  # Unique survivors
                        self.round_count += 1
                        self.start_level()

            # Update monster
            self.update_monster(dt)
            self.update_bouncing_bar(dt)

            # Physics step
            self.space.step(dt)

            # Elimination logic (fire/safe zones)
            new_marbles = []
            for m in self.marbles[:]:
                if m.body in self.space.bodies:  # Still active
                    x, y = m.body.position
                    if y > HEIGHT - 30:
                        if x < GAME_WIDTH / 2:  # Fire zone - eliminated
                            self.space.remove(m.body, m)
                        else:  # Safe zone - survive
                            if m.custom_color not in self.survivors:
                                self.survivors.append(m.custom_color)
                            self.space.remove(m.body, m)
                    else:
                        new_marbles.append(m)
            self.marbles = new_marbles

            # Rendering
            self.screen.fill(BG_COLOR)

            # Round count at top
            round_text = self.big_font.render(f"Round: {self.round_count}", True, WHITE)
            self.screen.blit(round_text, (10, 10))

            # Draw bouncing bar
            bx, by = int(self.bar_body.position.x), int(self.bar_body.position.y)
            bar_color = (220, 100, 220)  # nice purple, or whatever you like
            pygame.draw.rect(self.screen, bar_color,
                           (bx - BAR_WIDTH//2, by - BAR_HEIGHT//2,
                            BAR_WIDTH, BAR_HEIGHT), border_radius=6)
            # Optional glow/highlight
            pygame.draw.rect(self.screen, (255, 180, 255),
                           (bx - BAR_WIDTH//2, by - BAR_HEIGHT//2,
                            BAR_WIDTH, BAR_HEIGHT), 3, border_radius=6)

            # Draw pins
            for pin in self.pins:
                pos = int(pin.offset.x), int(pin.offset.y)
                pygame.draw.circle(self.screen, WHITE, pos, PIN_RADIUS)

            # Fire & Safe zones
            pygame.draw.rect(self.screen, FIRE_COLOR, (0, HEIGHT - 20, GAME_WIDTH // 2, 20))
            pygame.draw.rect(self.screen, SAFE_COLOR, (GAME_WIDTH // 2, HEIGHT - 20, GAME_WIDTH // 2, 20))

            # Draw marbles
            for m in self.marbles:
                pos = int(m.body.position.x), int(m.body.position.y)
                pygame.draw.circle(self.screen, m.custom_color, pos, MARBLE_RADIUS)

            # Draw monster (round, evil smile)
            mx, my = int(self.monster_body.position.x), int(self.monster_body.position.y)
            pygame.draw.circle(self.screen, DARK_GRAY, (mx, my), MONSTER_RADIUS)
            # Eyes (glowing evil)
            eye_offset = 6
            pygame.draw.circle(self.screen, WHITE, (mx - eye_offset, my - 3), 5)
            pygame.draw.circle(self.screen, WHITE, (mx + eye_offset, my - 3), 5)
            pygame.draw.circle(self.screen, BLACK, (mx - eye_offset, my - 3), 2)
            pygame.draw.circle(self.screen, BLACK, (mx + eye_offset, my - 3), 2)
            # Evil smile (curved arc)
            smile_rect = pygame.Rect(mx - 12, my + 2, 24, 12)
            pygame.draw.arc(self.screen, (200, 50, 50), smile_rect, math.pi, 2 * math.pi, 4)
            # Teeth (simple)
            pygame.draw.line(self.screen, WHITE, (mx - 4, my + 8), (mx - 2, my + 8), 2)
            pygame.draw.line(self.screen, WHITE, (mx + 2, my + 8), (mx + 4, my + 8), 2)

            # UI Panel
            pygame.draw.rect(self.screen, PANEL_COLOR, (GAME_WIDTH, 0, WIDTH - GAME_WIDTH, HEIGHT))
            survivors_text = self.font.render(f"Survivors: {len(self.survivors)}", True, WHITE)
            self.screen.blit(survivors_text, (GAME_WIDTH + 10, 10))

            # Survivor color swatches
            for i, color in enumerate(self.survivors):
                row, col = divmod(i, 4)
                swatch_pos = (GAME_WIDTH + 30 + col * 40, 50 + row * 40)
                pygame.draw.circle(self.screen, color, swatch_pos, 15)
                if i > MAX_SURVIVOR_DISPLAY: # Show first 100 max
                    break

            # Next Level button
            button_color = WHITE if self.survivors else (100, 100, 100)
            pygame.draw.rect(self.screen, button_color, button_rect)
            pygame.draw.rect(self.screen, BLACK, button_rect, 2)
            btn_text = self.font.render("NEXT LEVEL", True, BLACK)
            text_rect = btn_text.get_rect(center=button_rect.center)
            self.screen.blit(btn_text, text_rect)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    MarbleSurvival().run()