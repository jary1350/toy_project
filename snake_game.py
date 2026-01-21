import pygame
import random
import sys
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE
BASE_FPS = 7  # Level 1 speed
APPLES_PER_LEVEL = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Eats Apples")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        # Try to load or create a beep sound
        self.create_beep_sound()
        
        # Initialize game state
        self.reset_game()
    
    def reset_game(self):
        """Reset game to initial state"""
        # Initialize snake in the middle
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        
        # Spawn first apple
        self.apple = self.spawn_apple()
        
        # Score and level
        self.score = 0
        self.level = 1
        self.apples_eaten_this_level = 0
        
        self.game_over = False
        self.level_passed = False
        
    def create_beep_sound(self):
        """Create a simple beep sound using numpy and pygame"""
        try:
            import numpy as np
            sample_rate = 22050
            duration = 0.2  # 200ms
            frequency = 440  # A4 note
            
            # Generate sine wave
            frames = int(sample_rate * duration)
            arr = np.sin(2.0 * np.pi * frequency * np.linspace(0, duration, frames))
            arr = (arr * 32767).astype(np.int16)
            arr = np.repeat(arr.reshape(frames, 1), 2, axis=1)
            
            sound = pygame.sndarray.make_sound(arr)
            self.beep_sound = sound
        except:
            # Fallback: no sound if numpy not available
            self.beep_sound = None
    
    def spawn_apple(self):
        """Spawn apple at random location not occupied by snake"""
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in self.snake:
                return (x, y)
    
    def handle_input(self):
        """Handle keyboard input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                # Handle space bar for restart/next level
                if event.key == pygame.K_SPACE:
                    if self.game_over:
                        self.reset_game()
                    elif self.level_passed:
                        self.next_level()
                # Check arrow keys
                elif event.key == pygame.K_UP and self.direction != Direction.DOWN:
                    self.next_direction = Direction.UP
                elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
                    self.next_direction = Direction.DOWN
                elif event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
                    self.next_direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
                    self.next_direction = Direction.RIGHT
        
        return True
    
    def next_level(self):
        """Advance to next level"""
        self.level += 1
        self.apples_eaten_this_level = 0
        self.level_passed = False
        
        # Keep score and snake, just reset apple position
        self.apple = self.spawn_apple()
    
    def update(self):
        """Update game state"""
        if self.game_over or self.level_passed:
            return
        
        # Update direction
        self.direction = self.next_direction
        
        # Calculate new head position
        head_x, head_y = self.snake[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, new_head_y := head_y + dy)
        
        # Check wall collision
        if new_head[0] < 0 or new_head[0] >= GRID_WIDTH or \
           new_head[1] < 0 or new_head[1] >= GRID_HEIGHT:
            self.game_over = True
            return
        
        # Check self collision
        if new_head in self.snake:
            self.game_over = True
            return
        
        # Add new head
        self.snake.insert(0, new_head)
        
        # Check if apple eaten
        if new_head == self.apple:
            self.score += 10
            self.apples_eaten_this_level += 1
            self.apple = self.spawn_apple()
            
            # Play beep sound
            if self.beep_sound:
                self.beep_sound.play()
            
            # Check if level completed
            if self.apples_eaten_this_level >= APPLES_PER_LEVEL:
                self.level_passed = True
        else:
            # Remove tail if didn't eat apple
            self.snake.pop()
    
    def draw(self):
        """Draw game screen"""
        self.screen.fill(BLACK)
        
        # Draw grid (optional)
        for x in range(0, WINDOW_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, WINDOW_HEIGHT), 1)
        for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (WINDOW_WIDTH, y), 1)
        
        # Draw snake
        for i, (x, y) in enumerate(self.snake):
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE - 2, GRID_SIZE - 2)
            if i == 0:  # Head
                pygame.draw.rect(self.screen, GREEN, rect)
            else:  # Body
                pygame.draw.rect(self.screen, WHITE, rect)
        
        # Draw apple
        apple_x, apple_y = self.apple
        apple_rect = pygame.Rect(apple_x * GRID_SIZE + 2, apple_y * GRID_SIZE + 2, 
                                  GRID_SIZE - 4, GRID_SIZE - 4)
        pygame.draw.rect(self.screen, RED, apple_rect)
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Draw level
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (10, 50))
        
        # Draw length
        length_text = self.font.render(f"Length: {len(self.snake)}", True, WHITE)
        self.screen.blit(length_text, (10, 90))
        
        # Draw apples progress
        apples_text = self.font.render(f"Apples: {self.apples_eaten_this_level}/{APPLES_PER_LEVEL}", True, WHITE)
        self.screen.blit(apples_text, (10, 130))
        
        # Draw level passed message
        if self.level_passed:
            level_passed_text = self.font.render("LEVEL PASSED!", True, YELLOW)
            text_rect = level_passed_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30))
            self.screen.blit(level_passed_text, text_rect)
            
            next_level_text = self.font.render("Press SPACE to enter next level", True, WHITE)
            text_rect2 = next_level_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30))
            self.screen.blit(next_level_text, text_rect2)
        
        # Draw game over message
        if self.game_over:
            game_over_text = self.font.render("GAME OVER!", True, YELLOW)
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30))
            self.screen.blit(game_over_text, text_rect)
            
            restart_text = self.font.render("Press SPACE to start over", True, WHITE)
            text_rect2 = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30))
            self.screen.blit(restart_text, text_rect2)
        
        pygame.display.flip()
        return True
    
    def get_fps(self):
        """Calculate FPS based on current level"""
        # Each level increases speed by 10%
        return int(BASE_FPS * (1.1 ** (self.level - 1)))
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.handle_input()
            if not running:
                break
            
            self.update()
            running = self.draw()
            
            self.clock.tick(self.get_fps())
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = SnakeGame()
    game.run()
