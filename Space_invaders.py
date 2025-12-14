import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants - These define our game's basic parameters
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Game settings
PLAYER_SPEED = 5
BULLET_SPEED = 7
ALIEN_SPEED = 1
ALIEN_DROP_SPEED = 20

class Player:
    """Player class representing our rocket ship"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 40
        self.speed = PLAYER_SPEED
        
    def move_left(self):
        """Move player left, but don't go off screen"""
        if self.x > 0:
            self.x -= self.speed
            
    def move_right(self):
        """Move player right, but don't go off screen"""
        if self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
            
    def draw(self, screen):
        """Draw the player as a simple rocket shape"""
        # Main body (rectangle)
        pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))
        # Rocket tip (triangle)
        tip_points = [
            (self.x + self.width//2, self.y - 10),
            (self.x + 10, self.y),
            (self.x + self.width - 10, self.y)
        ]
        pygame.draw.polygon(screen, GREEN, tip_points)
        
    def get_rect(self):
        """Return rectangle for collision detection"""
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Bullet:
    """Bullet class for player missiles"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 5
        self.height = 10
        self.speed = BULLET_SPEED
        
    def move(self):
        """Move bullet upward"""
        self.y -= self.speed
        
    def draw(self, screen):
        """Draw the bullet"""
        pygame.draw.rect(screen, YELLOW, (self.x, self.y, self.width, self.height))
        
    def is_off_screen(self):
        """Check if bullet has gone off screen"""
        return self.y < 0
        
    def get_rect(self):
        """Return rectangle for collision detection"""
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Alien:
    """Alien UFO class"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 30
        self.speed = ALIEN_SPEED
        self.direction = 1  # 1 for right, -1 for left
        
    def move(self):
        """Move alien horizontally"""
        self.x += self.speed * self.direction
        
    def drop_down(self):
        """Move alien down and reverse direction"""
        self.y += ALIEN_DROP_SPEED
        self.direction *= -1
        
    def draw(self, screen):
        """Draw the alien UFO"""
        # Main body (ellipse)
        pygame.draw.ellipse(screen, RED, (self.x, self.y, self.width, self.height))
        # UFO dome
        pygame.draw.ellipse(screen, (150, 0, 0), (self.x + 5, self.y - 10, self.width - 10, 20))
        
    def get_rect(self):
        """Return rectangle for collision detection"""
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Game:
    """Main game class that handles all game logic"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()
        
        # Initialize game objects
        self.player = Player(SCREEN_WIDTH // 2 - 25, SCREEN_HEIGHT - 80)
        self.bullets = []
        self.aliens = []
        
        # Game state variables
        self.score = 0
        self.lives = 3
        self.game_over = False
        
        # Font for text display
        self.font = pygame.font.Font(None, 36)
        
        # Create initial alien formation
        self.create_alien_formation()
        
    def create_alien_formation(self):
        """Create a formation of aliens"""
        self.aliens = []
        rows = 5
        cols = 10
        
        for row in range(rows):
            for col in range(cols):
                x = col * 60 + 50
                y = row * 50 + 50
                self.aliens.append(Alien(x, y))
                
    def handle_events(self):
        """Handle all pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    # Create a bullet at player position
                    bullet_x = self.player.x + self.player.width // 2 - 2
                    bullet_y = self.player.y
                    self.bullets.append(Bullet(bullet_x, bullet_y))
                elif event.key == pygame.K_r and self.game_over:
                    # Restart game
                    self.restart_game()
                    
        return True
    
    def handle_input(self):
        """Handle continuous keyboard input"""
        if not self.game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player.move_left()
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player.move_right()
    
    def update_bullets(self):
        """Update all bullets"""
        # Move bullets and remove those off screen
        self.bullets = [bullet for bullet in self.bullets if not bullet.is_off_screen()]
        
        for bullet in self.bullets:
            bullet.move()
    
    def update_aliens(self):
        """Update all aliens"""
        if not self.aliens:
            # If all aliens destroyed, create new formation
            self.create_alien_formation()
            
        # Check if any alien has hit the screen edge
        hit_edge = False
        for alien in self.aliens:
            alien.move()
            if alien.x <= 0 or alien.x >= SCREEN_WIDTH - alien.width:
                hit_edge = True
                
        # If edge hit, make all aliens drop down and reverse direction
        if hit_edge:
            for alien in self.aliens:
                alien.drop_down()
    
    def check_collisions(self):
        """Check for collisions between bullets and aliens"""
        for bullet in self.bullets[:]:  # Use slice copy to safely modify list
            for alien in self.aliens[:]:
                if bullet.get_rect().colliderect(alien.get_rect()):
                    # Remove both bullet and alien
                    self.bullets.remove(bullet)
                    self.aliens.remove(alien)
                    self.score += 10
                    break  # Break inner loop since bullet is gone
    
    def check_alien_collision_with_player(self):
        """Check if any alien has reached the player"""
        player_rect = self.player.get_rect()
        
        for alien in self.aliens:
            if alien.get_rect().colliderect(player_rect) or alien.y >= SCREEN_HEIGHT - 100:
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over = True
                else:
                    # Reset alien formation when player is hit
                    self.create_alien_formation()
                break
    
    def draw(self):
        """Draw everything on the screen"""
        # Fill screen with black
        self.screen.fill(BLACK)
        
        if not self.game_over:
            # Draw game objects
            self.player.draw(self.screen)
            
            for bullet in self.bullets:
                bullet.draw(self.screen)
                
            for alien in self.aliens:
                alien.draw(self.screen)
        
        # Draw UI elements
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        self.screen.blit(lives_text, (10, 50))
        
        if self.game_over:
            # Draw game over screen
            game_over_text = self.font.render("GAME OVER!", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(game_over_text, text_rect)
            
            restart_text = self.font.render("Press 'R' to restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            self.screen.blit(restart_text, restart_rect)
        
        # Update display
        pygame.display.flip()
    
    def restart_game(self):
        """Restart the game"""
        self.player = Player(SCREEN_WIDTH // 2 - 25, SCREEN_HEIGHT - 80)
        self.bullets = []
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.create_alien_formation()
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            # Handle events
            running = self.handle_events()
            
            if not self.game_over:
                # Handle input
                self.handle_input()
                
                # Update game objects
                self.update_bullets()
                self.update_aliens()
                
                # Check collisions
                self.check_collisions()
                self.check_alien_collision_with_player()
            
            # Draw everything
            self.draw()
            
            # Control frame rate (60 FPS)
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

# Main execution
if __name__ == "__main__":
    print("Welcome to Space Invaders!")
    print("Controls:")
    print("- Use LEFT/RIGHT arrow keys or A/D to move")
    print("- Press SPACE to shoot")
    print("- Press R to restart when game over")
    print("- Close window or Ctrl+C to quit")
    
    game = Game()
    game.run()