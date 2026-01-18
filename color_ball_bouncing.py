import pygame
import pymunk
import random

# --- Configuration ---
WIDTH, HEIGHT = 1000, 800  # Increased width for the UI panel
GAME_WIDTH = 800
FPS = 60
GRAVITY = 900.0
MARBLE_RADIUS = 10
PIN_RADIUS = 5

# Colors
WHITE = (255, 255, 255)
BG_COLOR = (100, 149, 237)
FIRE_COLOR = (255, 69, 0)
SAFE_COLOR = (50, 205, 50)
PANEL_COLOR = (50, 50, 50)


class MarbleSurvival:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18)

        self.space = pymunk.Space()
        self.space.gravity = (0, GRAVITY)

        self.marbles = []
        self.survivors = []
        self.pins = []
        self.current_colors = [(random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)) for _ in
                               range(1_000)]

        self.create_boundaries()
        self.create_pins()
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
        for row in range(10):
            for col in range(15):
                x = (col * 50) + 50 + (25 if row % 2 == 0 else 0)
                y = (row * 60) + 150
                body = self.space.static_body
                shape = pymunk.Circle(body, PIN_RADIUS, (x, y))
                shape.elasticity = 0.8
                shape.color = WHITE
                self.space.add(shape)
                self.pins.append(shape)

    def start_level(self):
        """Resets the game with the current pool of colors."""
        for m in self.marbles:
            self.space.remove(m.body, m)
        self.marbles = []
        self.survivors = []

        for color in self.current_colors:
            self.add_marble(color)

    def add_marble(self, color):
        mass, moment = 1, pymunk.moment_for_circle(1, 0, MARBLE_RADIUS)
        body = pymunk.Body(mass, moment)
        body.position = (random.randint(50, GAME_WIDTH - 50), random.randint(-200, 0))
        shape = pymunk.Circle(body, MARBLE_RADIUS)
        shape.elasticity, shape.friction = 0.6, 0.5
        shape.custom_color = color
        self.space.add(body, shape)
        self.marbles.append(shape)

    def run(self):
        running = True
        button_rect = pygame.Rect(GAME_WIDTH + 20, HEIGHT - 60, 160, 40)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint(event.pos) and self.survivors:
                        self.current_colors = [s for s in self.survivors]
                        self.start_level()

            self.space.step(1 / FPS)

            # Logic: Elimination and Survival
            new_marbles = []
            for m in self.marbles:
                x, y = m.body.position
                # FIRE ZONE: Bottom Left
                if y > HEIGHT - 30 and x < GAME_WIDTH / 2:
                    self.space.remove(m.body, m)
                # SAFE ZONE: Bottom Right
                elif y > HEIGHT - 30 and x >= GAME_WIDTH / 2:
                    if m.custom_color not in self.survivors:
                        self.survivors.append(m.custom_color)
                    self.space.remove(m.body, m)
                else:
                    new_marbles.append(m)
            self.marbles = new_marbles

            # Drawing
            self.screen.fill(BG_COLOR)

            # Draw Pins
            for pin in self.pins:
                pos = int(pin.offset.x), int(pin.offset.y)
                pygame.draw.circle(self.screen, WHITE, pos, PIN_RADIUS)

            # Draw Fire and Safe Zones
            pygame.draw.rect(self.screen, FIRE_COLOR, (0, HEIGHT - 20, GAME_WIDTH // 2, 20))
            pygame.draw.rect(self.screen, SAFE_COLOR, (GAME_WIDTH // 2, HEIGHT - 20, GAME_WIDTH // 2, 20))

            # Draw Marbles
            for m in self.marbles:
                pos = int(m.body.position.x), int(m.body.position.y)
                pygame.draw.circle(self.screen, m.custom_color, pos, MARBLE_RADIUS)

            # --- UI Panel ---
            pygame.draw.rect(self.screen, PANEL_COLOR, (GAME_WIDTH, 0, WIDTH - GAME_WIDTH, HEIGHT))
            title = self.font.render(f"Survivors: {len(self.survivors)}", True, WHITE)
            self.screen.blit(title, (GAME_WIDTH + 10, 10))

            # Draw surviving marble swatches
            for i, color in enumerate(self.survivors):
                row, col = i // 4, i % 4
                pygame.draw.circle(self.screen, color, (GAME_WIDTH + 30 + col * 40, 60 + row * 40), 15)

            # Level Button
            pygame.draw.rect(self.screen, WHITE if self.survivors else (100, 100, 100), button_rect)
            btn_text = self.font.render("ENTER NEXT LEVEL", True, (0, 0, 0))
            self.screen.blit(btn_text, (button_rect.x + 10, button_rect.y + 10))

            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()


if __name__ == "__main__":
    MarbleSurvival().run()