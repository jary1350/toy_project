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
BLUE = (0, 100, 255)
LIGHT_GRAY = (180, 180, 180)

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
        # Initialize player snake in the middle-left
        self.snake = [(GRID_WIDTH // 3, GRID_HEIGHT // 2)]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        
        # Initialize rival snake in the middle-right
        self.rival_snake = [(2 * GRID_WIDTH // 3, GRID_HEIGHT // 2)]
        self.rival_direction = Direction.LEFT
        
        # Spawn two apples
        self.apple1 = self.spawn_apple()
        self.apple2 = self.spawn_apple()
        
        # Score and level
        self.score = 0
        self.level = 1
        self.apples_eaten_this_level = 0
        self.rival_apples_eaten = 0
        
        self.game_over = False
        self.level_passed = False
        self.player_won = True  # Track if player won or lost
        
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
        """Spawn apple at random location not occupied by any snake or apple"""
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            pos = (x, y)
            # Check if position is free
            if pos not in self.snake and pos not in self.rival_snake:
                # Also check it's not on existing apples
                if hasattr(self, 'apple1') and pos == self.apple1:
                    continue
                if hasattr(self, 'apple2') and pos == self.apple2:
                    continue
                return pos
    
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
        self.rival_apples_eaten = 0
        self.level_passed = False
        
        # Keep score and snakes, just reset apple positions
        self.apple1 = self.spawn_apple()
        self.apple2 = self.spawn_apple()
    
    def get_rival_direction(self):
        """AI to move rival snake toward nearest apple"""
        head_x, head_y = self.rival_snake[0]
        
        # Find nearest apple
        dist1 = abs(head_x - self.apple1[0]) + abs(head_y - self.apple1[1])
        dist2 = abs(head_x - self.apple2[0]) + abs(head_y - self.apple2[1])
        target = self.apple1 if dist1 <= dist2 else self.apple2
        
        # Simple AI: move toward target, avoiding reverse direction
        target_x, target_y = target
        possible_directions = []
        
        # Prioritize horizontal or vertical movement based on distance
        if target_x < head_x and self.rival_direction != Direction.RIGHT:
            possible_directions.append(Direction.LEFT)
        if target_x > head_x and self.rival_direction != Direction.LEFT:
            possible_directions.append(Direction.RIGHT)
        if target_y < head_y and self.rival_direction != Direction.DOWN:
            possible_directions.append(Direction.UP)
        if target_y > head_y and self.rival_direction != Direction.UP:
            possible_directions.append(Direction.DOWN)
        
        # If we have valid directions, choose one
        if possible_directions:
            return random.choice(possible_directions)
        
        # Otherwise keep current direction if valid, or pick random safe direction
        return self.rival_direction
    
    def update(self):
        """Update game state"""
        if self.game_over or self.level_passed:
            return
        
        # Update player direction
        self.direction = self.next_direction
        
        # Update rival direction (AI)
        self.rival_direction = self.get_rival_direction()
        
        # Calculate new head position for player
        head_x, head_y = self.snake[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)
        
        # Calculate new head position for rival
        rival_head_x, rival_head_y = self.rival_snake[0]
        rival_dx, rival_dy = self.rival_direction.value
        new_rival_head = (rival_head_x + rival_dx, rival_head_y + rival_dy)
        
        # Check player wall collision
        if new_head[0] < 0 or new_head[0] >= GRID_WIDTH or \
           new_head[1] < 0 or new_head[1] >= GRID_HEIGHT:
            self.game_over = True
            self.player_won = False
            return
        
        # Check rival wall collision
        rival_died = False
        if new_rival_head[0] < 0 or new_rival_head[0] >= GRID_WIDTH or \
           new_rival_head[1] < 0 or new_rival_head[1] >= GRID_HEIGHT:
            rival_died = True
        
        # Check player self collision
        if new_head in self.snake:
            self.game_over = True
            self.player_won = False
            return
        
        # Check rival self collision
        if not rival_died and new_rival_head in self.rival_snake:
            rival_died = True
        
        # Check collision between snakes (before adding new heads)
        # Player hits rival snake
        if new_head in self.rival_snake:
            self.game_over = True
            self.player_won = False
            return
        
        # Rival hits player snake
        if not rival_died and new_rival_head in self.snake:
            rival_died = True
        
        # Head-to-head collision
        if new_head == new_rival_head:
            self.game_over = True
            self.player_won = False
            return
        
        # Add new heads
        self.snake.insert(0, new_head)
        if not rival_died:
            self.rival_snake.insert(0, new_rival_head)
        
        # Check if player ate apple
        player_ate = False
        if new_head == self.apple1:
            self.score += 10
            self.apples_eaten_this_level += 1
            self.apple1 = self.spawn_apple()
            player_ate = True
        elif new_head == self.apple2:
            self.score += 10
            self.apples_eaten_this_level += 1
            self.apple2 = self.spawn_apple()
            player_ate = True
        
        if player_ate:
            # Play beep sound
            if self.beep_sound:
                self.beep_sound.play()
            
            # Check if player won level
            if self.apples_eaten_this_level >= APPLES_PER_LEVEL:
                self.level_passed = True
                self.player_won = True
        else:
            # Remove tail if didn't eat apple
            self.snake.pop()
        
        # Check if rival ate apple
        if not rival_died:
            rival_ate = False
            if new_rival_head == self.apple1:
                self.rival_apples_eaten += 1
                self.apple1 = self.spawn_apple()
                rival_ate = True
            elif new_rival_head == self.apple2:
                self.rival_apples_eaten += 1
                self.apple2 = self.spawn_apple()
                rival_ate = True
            
            # Check if rival won
            if self.rival_apples_eaten >= APPLES_PER_LEVEL:
                self.game_over = True
                self.player_won = False
                return
            
            if not rival_ate:
                # Remove rival tail if didn't eat apple
                self.rival_snake.pop()
    
    def draw(self):
        """Draw game screen"""
        self.screen.fill(BLACK)
        
        # Draw grid (optional)
        for x in range(0, WINDOW_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, WINDOW_HEIGHT), 1)
        for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (WINDOW_WIDTH, y), 1)
        
        # Draw player snake (green head, white body)
        for i, (x, y) in enumerate(self.snake):
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE - 2, GRID_SIZE - 2)
            if i == 0:  # Head
                pygame.draw.rect(self.screen, GREEN, rect)
            else:  # Body
                pygame.draw.rect(self.screen, WHITE, rect)
        
        # Draw rival snake (blue head, light gray body)
        for i, (x, y) in enumerate(self.rival_snake):
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE - 2, GRID_SIZE - 2)
            if i == 0:  # Head
                pygame.draw.rect(self.screen, BLUE, rect)
            else:  # Body
                pygame.draw.rect(self.screen, LIGHT_GRAY, rect)
        
        # Draw both apples
        apple1_x, apple1_y = self.apple1
        apple1_rect = pygame.Rect(apple1_x * GRID_SIZE + 2, apple1_y * GRID_SIZE + 2, 
                                   GRID_SIZE - 4, GRID_SIZE - 4)
        pygame.draw.rect(self.screen, RED, apple1_rect)
        
        apple2_x, apple2_y = self.apple2
        apple2_rect = pygame.Rect(apple2_x * GRID_SIZE + 2, apple2_y * GRID_SIZE + 2, 
                                   GRID_SIZE - 4, GRID_SIZE - 4)
        pygame.draw.rect(self.screen, RED, apple2_rect)
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Draw level
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (10, 50))
        
        # Draw player progress (green color)
        player_text = self.font.render(f"You: {self.apples_eaten_this_level}/{APPLES_PER_LEVEL}", True, GREEN)
        self.screen.blit(player_text, (10, 90))
        
        # Draw rival progress (blue color)
        rival_text = self.font.render(f"Rival: {self.rival_apples_eaten}/{APPLES_PER_LEVEL}", True, BLUE)
        self.screen.blit(rival_text, (10, 130))
        
        # Draw level passed message
        if self.level_passed:
            level_passed_text = self.font.render("YOU WON THE LEVEL!", True, YELLOW)
            text_rect = level_passed_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30))
            self.screen.blit(level_passed_text, text_rect)
            
            next_level_text = self.font.render("Press SPACE to enter next level", True, WHITE)
            text_rect2 = next_level_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30))
            self.screen.blit(next_level_text, text_rect2)
        
        # Draw game over message
        if self.game_over:
            if self.player_won:
                game_over_text = self.font.render("YOU WON!", True, GREEN)
            else:
                game_over_text = self.font.render("YOU LOST!", True, RED)
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
