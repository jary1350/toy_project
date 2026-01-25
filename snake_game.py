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
        # Level N: 4N apples, 2N rivals
        num_apples = self.level * 4
        num_rivals = self.level * 2
        
        # Create apples
        self.apples = []
        for _ in range(num_apples):
            self.apples.append(self.spawn_apple(RED))
        
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
    
    def get_safe_respawn_position(self, preferred_pos):
        """Find a safe respawn position, starting with preferred position, then searching randomly"""
        # Check if preferred position is safe
        if self._is_position_safe(preferred_pos):
            return preferred_pos
        
        # If not, search for a safe random position
        max_attempts = 100
        for _ in range(max_attempts):
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            pos = (x, y)
            if self._is_position_safe(pos):
                return pos
        
        # If no safe position found after attempts, return preferred anyway
        return preferred_pos
    
    def _is_position_safe(self, pos):
        """Check if a position is safe (not occupied by any snake or apple)"""
        # Check player snake
        if pos in self.snake:
            return False
        
        # Check all rival snakes
        for rival in self.rival_snakes:
            if pos in rival:
                return False
        
        # Check all apples
        apple_positions = [apple['pos'] if isinstance(apple, dict) else apple for apple in self.apples]
        if pos in apple_positions:
            return False
        
        return True
    
    def spawn_apple(self, color=None):
        """Spawn apple at random location not occupied by any snake or apple"""
        if color is None:
            color = RED
        
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
            if hasattr(self, 'apples'):
                apple_positions = [apple['pos'] if isinstance(apple, dict) else apple for apple in self.apples]
                if pos in apple_positions:
                    continue
            
            return {'pos': pos, 'color': color}
    
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
        """AI to move rival snake - gets smarter at higher levels"""
        head_x, head_y = self.rival_snakes[rival_idx][0]
        current_dir = self.rival_directions[rival_idx]
        
        # Difficulty increases with level
        # Level 1: 10% apple pursuit
        # Level 5: 33.3% apple pursuit
        # Level 10: 66.7% apple pursuit
        apple_pursuit_chance = min(2/3, 0.10 + (self.level - 1) * 0.063)
        danger_zone = max(1, 3 - (self.level - 1) // 3)
        
        # Check which directions lead to boundaries
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
        
        # Try to pursue apple with level-dependent probability
        if random.random() < apple_pursuit_chance and self.apples:
            # Find nearest apple
            nearest_apple = min(self.apples, key=lambda a: abs(head_x - a['pos'][0]) + abs(head_y - a['pos'][1]))
            target_x, target_y = nearest_apple['pos']
            
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
            
            # At higher levels, prefer unsafe directions if they lead to apple
            good_choices = [d for d in toward_apple if d in safe_directions]
            if good_choices:
                return random.choice(good_choices)
            elif toward_apple:
                # At level 5+, prefer toward_apple even if unsafe
                if self.level >= 5:
                    return random.choice(toward_apple)
                # Otherwise only pick unsafe if no safe directions exist
                elif not safe_directions:
                    return random.choice(toward_apple)
        
        # Prefer safe directions, but at high levels be more aggressive
        if safe_directions and (self.level < 8 or random.random() < 0.7):
            return random.choice(safe_directions)
        
        # Default: pick any valid direction
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
            # Respawn at size 1 at starting position
            death_pos = self.snake[0]
            self.apples.append({'pos': death_pos, 'color': GREEN})
            respawn_pos = self.get_safe_respawn_position((GRID_WIDTH // 3, GRID_HEIGHT // 2))
            self.snake = [respawn_pos]
            self.apples_eaten_this_level = 0  # Reset score
            return
        
        # Check player self collision
        if new_head in self.snake:
            # Respawn at size 1
            death_pos = self.snake[0]
            self.apples.append({'pos': death_pos, 'color': GREEN})
            respawn_pos = self.get_safe_respawn_position((GRID_WIDTH // 3, GRID_HEIGHT // 2))
            self.snake = [respawn_pos]
            self.apples_eaten_this_level = 0  # Reset score
            return
        
        # Check if player hits any rival snake
        for i, rival in enumerate(self.rival_snakes):
            if new_head in rival:
                player_size = len(self.snake)
                rival_size = len(rival)
                
                if player_size > rival_size:
                    # Player is larger - rival respawns
                    rival_death_pos = rival[0]
                    rival_color = self.rival_colors[i]
                    self.apples.append({'pos': rival_death_pos, 'color': rival_color})
                    start_x = GRID_WIDTH // 2 + (i + 1) * (GRID_WIDTH // (len(self.rival_snakes) + 2))
                    start_y = GRID_HEIGHT // 2 + (i % 3 - 1) * 5
                    respawn_pos = self.get_safe_respawn_position((start_x % GRID_WIDTH, start_y % GRID_HEIGHT))
                    self.rival_snakes[i] = [respawn_pos]
                    self.rival_apples_eaten[i] = 0  # Reset rival score
                else:
                    # Rival is larger or equal - player respawns
                    player_death_pos = self.snake[0]
                    self.apples.append({'pos': player_death_pos, 'color': GREEN})
                    respawn_pos = self.get_safe_respawn_position((GRID_WIDTH // 3, GRID_HEIGHT // 2))
                    self.snake = [respawn_pos]
                    self.apples_eaten_this_level = 0  # Reset player score
                return
        
        # Update all rival snakes
        new_rival_heads = []
        rivals_to_remove = []
        rivals_to_respawn = []  # Track rivals that need to respawn
        
        for i, rival in enumerate(self.rival_snakes):
            # Update rival direction
            self.rival_directions[i] = self.get_rival_direction(i)
            
            # Calculate new head position
            rival_head_x, rival_head_y = rival[0]
            rival_dx, rival_dy = self.rival_directions[i].value
            new_rival_head = (rival_head_x + rival_dx, rival_head_y + rival_dy)
            new_rival_heads.append(new_rival_head)
            
            # Check rival wall collision - respawn instead of removing
            if new_rival_head[0] < 0 or new_rival_head[0] >= GRID_WIDTH or \
               new_rival_head[1] < 0 or new_rival_head[1] >= GRID_HEIGHT:
                rival_color = self.rival_colors[i]
                rival_death_pos = rival[0]
                self.apples.append({'pos': rival_death_pos, 'color': rival_color})
                rivals_to_respawn.append(i)
                rivals_to_remove.append(i)
                continue
            
            # Check rival self collision - respawn instead of removing
            if new_rival_head in rival:
                rival_color = self.rival_colors[i]
                rival_death_pos = rival[0]
                self.apples.append({'pos': rival_death_pos, 'color': rival_color})
                rivals_to_respawn.append(i)
                rivals_to_remove.append(i)
                continue
            
            # Check if rival hits player snake
            if new_rival_head in self.snake:
                rival_size = len(rival)
                player_size = len(self.snake)
                
                if rival_size > player_size:
                    # Rival is larger - player dies
                    rivals_to_remove.append(i)
                    continue
                else:
                    # Player is larger or equal - rival respawns
                    rival_color = self.rival_colors[i]
                    rival_death_pos = rival[0]
                    self.apples.append({'pos': rival_death_pos, 'color': rival_color})
                    rivals_to_respawn.append(i)
                    rivals_to_remove.append(i)
                    continue
            
            # Check if rival hits another rival
            for j, other_rival in enumerate(self.rival_snakes):
                if i != j and new_rival_head in other_rival:
                    rival_i_size = len(rival)
                    rival_j_size = len(other_rival)
                    
                    if rival_i_size > rival_j_size:
                        # Current rival is larger, other rival respawns
                        if j not in rivals_to_remove:
                            other_rival_color = self.rival_colors[j]
                            other_rival_death_pos = other_rival[0]
                            self.apples.append({'pos': other_rival_death_pos, 'color': other_rival_color})
                            rivals_to_respawn.append(j)
                            rivals_to_remove.append(j)
                    else:
                        # Other rival is larger or equal, current rival respawns
                        rival_color = self.rival_colors[i]
                        rival_death_pos = rival[0]
                        self.apples.append({'pos': rival_death_pos, 'color': rival_color})
                        rivals_to_respawn.append(i)
                        rivals_to_remove.append(i)
                    break
        
        # Check head-to-head collision with player
        for i, new_rival_head in enumerate(new_rival_heads):
            if i not in rivals_to_remove and new_rival_head == new_head:
                rival_size = len(self.rival_snakes[i])
                player_size = len(self.snake)
                
                if rival_size > player_size:
                    # Rival is larger - player dies
                    self.game_over = True
                    self.player_won = False
                    return
                else:
                    # Player is larger - rival respawns
                    rival_color = self.rival_colors[i]
                    rival_death_pos = self.rival_snakes[i][0]
                    self.apples.append({'pos': rival_death_pos, 'color': rival_color})
                    rivals_to_respawn.append(i)
                    rivals_to_remove.append(i)
        
        # Add new player head
        self.snake.insert(0, new_head)
        
        # Check if player ate apple
        player_ate = False
        for i, apple in enumerate(self.apples):
            apple_pos = apple['pos'] if isinstance(apple, dict) else apple
            if new_head == apple_pos:
                self.score += 10
                self.apples_eaten_this_level += 1
                self.apples[i] = self.spawn_apple(RED)
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
                apple_pos = apple['pos'] if isinstance(apple, dict) else apple
                if new_rival_heads[i] == apple_pos:
                    self.rival_apples_eaten[i] += 1
                    self.apples[j] = self.spawn_apple(RED)
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
        
        # Respawn rivals that died
        for i in rivals_to_respawn:
            start_x = GRID_WIDTH // 2 + (i + 1) * (GRID_WIDTH // (len(self.rival_snakes) + 2))
            start_y = GRID_HEIGHT // 2 + (i % 3 - 1) * 5
            respawn_pos = self.get_safe_respawn_position((start_x % GRID_WIDTH, start_y % GRID_HEIGHT))
            self.rival_snakes[i] = [respawn_pos]
            self.rival_apples_eaten[i] = 0
        
        # Remove any rivals that were marked for removal but didn't respawn
        truly_removed = [i for i in rivals_to_remove if i not in rivals_to_respawn]
        for i in sorted(truly_removed, reverse=True):
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
            if isinstance(apple, dict):
                apple_pos = apple['pos']
                apple_color = apple['color']
            else:
                apple_pos = apple
                apple_color = RED
            
            apple_x, apple_y = apple_pos
            apple_rect = pygame.Rect(apple_x * GRID_SIZE + 2, apple_y * GRID_SIZE + 2, 
                                      GRID_SIZE - 4, GRID_SIZE - 4)
            pygame.draw.rect(self.screen, apple_color, apple_rect)
        
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
