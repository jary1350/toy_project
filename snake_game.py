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
BASE_FPS = 5  # Level 1 speed (slower movement)
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
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
PINK = (255, 192, 203)

def get_random_rival_color():
    """Generate a random color for rival that's not green or red"""
    rival_colors = [BLUE, CYAN, MAGENTA, ORANGE, PURPLE, PINK, YELLOW, 
                    (100, 100, 255), (255, 100, 100), (100, 255, 255)]
    return random.choice(rival_colors)

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
        
        # Score and level
        self.score = 0
        self.level = 1
        self.apples_eaten_this_level = 0
        
        # Initialize dynamic rivals and apples
        self.initialize_level()
        
        self.game_over = False
        self.level_passed = False
        self.player_won = True  # Track if player won or lost
        
    def initialize_level(self):
        """Initialize apples and rivals based on current level"""
        # Level N: N apples, N-1 rivals (min 0 rivals)
        num_apples = self.level
        num_rivals = max(0, self.level - 1)
        
        # Create apples
        self.apples = []
        for _ in range(num_apples):
            self.apples.append(self.spawn_apple())
        
        # Create rival snakes
        self.rival_snakes = []
        self.rival_directions = []
        self.rival_apples_eaten = []
        self.rival_colors = []  # Store random colors for each rival
        
        for i in range(num_rivals):
            # Spread rivals across the screen
            start_x = GRID_WIDTH // 2 + (i + 1) * (GRID_WIDTH // (num_rivals + 2))
            start_y = GRID_HEIGHT // 2 + (i % 3 - 1) * 5  # Stagger vertically
            self.rival_snakes.append([(start_x % GRID_WIDTH, start_y % GRID_HEIGHT)])
            self.rival_directions.append(Direction.LEFT)
            self.rival_apples_eaten.append(0)
            self.rival_colors.append(get_random_rival_color())  # Random color
    
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
            
            # Check if position is free from player snake
            if pos in self.snake:
                continue
            
            # Check all rival snakes
            occupied = False
            if hasattr(self, 'rival_snakes'):
                for rival in self.rival_snakes:
                    if pos in rival:
                        occupied = True
                        break
            
            if occupied:
                continue
            
            # Check all existing apples
            if hasattr(self, 'apples') and pos in self.apples:
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
        self.level_passed = False
        
        # Reset player snake to size 1 (keep position)
        if self.snake:
            self.snake = [self.snake[0]]
        
        # Initialize new level with more apples and rivals
        self.initialize_level()
    
    def get_rival_direction(self, rival_idx):
        """AI to move rival snake - avoid boundaries but not too smart about apples"""
        head_x, head_y = self.rival_snakes[rival_idx][0]
        current_dir = self.rival_directions[rival_idx]
        
        # Check which directions lead to boundaries (within 3 cells)
        danger_zone = 3
        safe_directions = []
        unsafe_directions = []
        
        all_dirs = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
        
        for d in all_dirs:
            # Don't reverse direction
            if (current_dir == Direction.UP and d == Direction.DOWN) or \
               (current_dir == Direction.DOWN and d == Direction.UP) or \
               (current_dir == Direction.LEFT and d == Direction.RIGHT) or \
               (current_dir == Direction.RIGHT and d == Direction.LEFT):
                continue
            
            # Check if this direction is near a boundary
            dx, dy = d.value
            new_x = head_x + dx
            new_y = head_y + dy
            
            is_safe = True
            if new_x < danger_zone or new_x >= GRID_WIDTH - danger_zone:
                is_safe = False
            if new_y < danger_zone or new_y >= GRID_HEIGHT - danger_zone:
                is_safe = False
            
            if is_safe:
                safe_directions.append(d)
            else:
                unsafe_directions.append(d)
        
        # 70% of the time, prefer safe directions if available
        if safe_directions and random.random() < 0.7:
            return random.choice(safe_directions)
        
        # 30% of the time, or if no safe directions, try toward apple (but not too smart)
        if random.random() < 0.5 and self.apples:  # Only 50% chance to even try for apple
            # Find nearest apple
            nearest_apple = min(self.apples, key=lambda a: abs(head_x - a[0]) + abs(head_y - a[1]))
            target_x, target_y = nearest_apple
            
            # Add directions toward target
            toward_apple = []
            if target_x < head_x and current_dir != Direction.RIGHT:
                toward_apple.append(Direction.LEFT)
            if target_x > head_x and current_dir != Direction.LEFT:
                toward_apple.append(Direction.RIGHT)
            if target_y < head_y and current_dir != Direction.DOWN:
                toward_apple.append(Direction.UP)
            if target_y > head_y and current_dir != Direction.UP:
                toward_apple.append(Direction.DOWN)
            
            # Prefer directions that are both toward apple and safe
            good_choices = [d for d in toward_apple if d in safe_directions]
            if good_choices:
                return random.choice(good_choices)
            elif toward_apple:
                return random.choice(toward_apple)
        
        # Default: pick any valid direction, preferring safe ones
        all_valid = safe_directions + unsafe_directions
        if all_valid:
            return random.choice(all_valid)
        
        return current_dir
    
    def update(self):
        """Update game state"""
        if self.game_over or self.level_passed:
            return
        
        # Update player direction
        self.direction = self.next_direction
        
        # Calculate new head position for player
        head_x, head_y = self.snake[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)
        
        # Check player wall collision
        if new_head[0] < 0 or new_head[0] >= GRID_WIDTH or \
           new_head[1] < 0 or new_head[1] >= GRID_HEIGHT:
            self.game_over = True
            self.player_won = False
            return
        
        # Check player self collision
        if new_head in self.snake:
            self.game_over = True
            self.player_won = False
            return
        
        # Check if player hits any rival snake
        for rival in self.rival_snakes:
            if new_head in rival:
                self.game_over = True
                self.player_won = False
                return
        
        # Update all rival snakes
        new_rival_heads = []
        rivals_to_remove = []
        
        for i, rival in enumerate(self.rival_snakes):
            # Update rival direction
            self.rival_directions[i] = self.get_rival_direction(i)
            
            # Calculate new head position
            rival_head_x, rival_head_y = rival[0]
            rival_dx, rival_dy = self.rival_directions[i].value
            new_rival_head = (rival_head_x + rival_dx, rival_head_y + rival_dy)
            new_rival_heads.append(new_rival_head)
            
            # Check rival wall collision
            if new_rival_head[0] < 0 or new_rival_head[0] >= GRID_WIDTH or \
               new_rival_head[1] < 0 or new_rival_head[1] >= GRID_HEIGHT:
                rivals_to_remove.append(i)
                continue
            
            # Check rival self collision
            if new_rival_head in rival:
                rivals_to_remove.append(i)
                continue
            
            # Check if rival hits player snake
            if new_rival_head in self.snake:
                rivals_to_remove.append(i)
                continue
            
            # Check if rival hits another rival
            for j, other_rival in enumerate(self.rival_snakes):
                if i != j and new_rival_head in other_rival:
                    rivals_to_remove.append(i)
                    break
        
        # Check head-to-head collision with player
        for i, new_rival_head in enumerate(new_rival_heads):
            if i not in rivals_to_remove and new_rival_head == new_head:
                self.game_over = True
                self.player_won = False
                return
        
        # Add new player head
        self.snake.insert(0, new_head)
        
        # Check if player ate apple
        player_ate = False
        for i, apple in enumerate(self.apples):
            if new_head == apple:
                self.score += 10
                self.apples_eaten_this_level += 1
                self.apples[i] = self.spawn_apple()
                player_ate = True
                
                # Play beep sound
                if self.beep_sound:
                    self.beep_sound.play()
                
                # Check if player won level
                if self.apples_eaten_this_level >= APPLES_PER_LEVEL:
                    self.level_passed = True
                    self.player_won = True
                break
        
        if not player_ate:
            # Remove tail if didn't eat apple
            self.snake.pop()
        
        # Update rival snakes
        for i, rival in enumerate(self.rival_snakes):
            if i in rivals_to_remove:
                continue
            
            # Add new head
            rival.insert(0, new_rival_heads[i])
            
            # Check if rival ate apple
            rival_ate = False
            for j, apple in enumerate(self.apples):
                if new_rival_heads[i] == apple:
                    self.rival_apples_eaten[i] += 1
                    self.apples[j] = self.spawn_apple()
                    rival_ate = True
                    
                    # Check if any rival won
                    if self.rival_apples_eaten[i] >= APPLES_PER_LEVEL:
                        self.game_over = True
                        self.player_won = False
                        return
                    break
            
            if not rival_ate:
                # Remove tail if didn't eat apple
                rival.pop()
        
        # Remove dead rivals
        for i in sorted(rivals_to_remove, reverse=True):
            del self.rival_snakes[i]
            del self.rival_directions[i]
            del self.rival_apples_eaten[i]
            del self.rival_colors[i]
    
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
        
        # Draw all rival snakes with random colors
        for rival_idx, rival in enumerate(self.rival_snakes):
            rival_color = self.rival_colors[rival_idx] if rival_idx < len(self.rival_colors) else BLUE
            for i, (x, y) in enumerate(rival):
                rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE - 2, GRID_SIZE - 2)
                if i == 0:  # Head - use rival's color
                    pygame.draw.rect(self.screen, rival_color, rect)
                else:  # Body - lighter version
                    pygame.draw.rect(self.screen, LIGHT_GRAY, rect)
        
        # Draw all apples
        for apple in self.apples:
            apple_x, apple_y = apple
            apple_rect = pygame.Rect(apple_x * GRID_SIZE + 2, apple_y * GRID_SIZE + 2, 
                                      GRID_SIZE - 4, GRID_SIZE - 4)
            pygame.draw.rect(self.screen, RED, apple_rect)
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Draw level and info
        level_text = self.font.render(f"Level {self.level}: {len(self.apples)} apples, {len(self.rival_snakes)} rivals", True, WHITE)
        self.screen.blit(level_text, (10, 50))
        
        # Draw player progress (green color)
        player_text = self.font.render(f"You: {self.apples_eaten_this_level}/{APPLES_PER_LEVEL}", True, GREEN)
        self.screen.blit(player_text, (10, 90))
        
        # Draw rival progress (show max rival progress)
        if self.rival_apples_eaten:
            max_rival_apples = max(self.rival_apples_eaten)
            rival_text = self.font.render(f"Best Rival: {max_rival_apples}/{APPLES_PER_LEVEL}", True, BLUE)
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
