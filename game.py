"""
Main game class with game loop and state management
"""
import pygame
from config import *
from player import Player
from level import Level
from database import Database
from UI import Button


class Game:
    def __init__(self, screen, user_id, username):
        self.screen = screen
        self.user_id = user_id
        self.username = username
        self.db = Database()
        
        # Fonts
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game state
        self.current_level = 1
        self.score = 0
        self.running = True
        self.game_over = False
        self.game_won = False
        
        # Initialize player and level
        self.player = Player(100, SCREEN_HEIGHT - 150)
        self.level = Level(self.current_level)
        
        # Clock
        self.clock = pygame.time.Clock()
    
    def handle_events(self):
        """Handle game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                # Handle game over / win restart
                if self.game_over or self.game_won:
                    if event.key == pygame.K_r:
                        self.restart_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                # Handle normal gameplay
                else:
                    if event.key == pygame.K_SPACE:
                        self.player.jump()
                    elif event.key == pygame.K_ESCAPE:
                        self.pause_menu()

    def restart_game(self):
        """Restart the game from level 1"""
        self.current_level = 1
        self.score = 0
        self.game_over = False
        self.game_won = False
        self.player = Player(100, SCREEN_HEIGHT - 150)
        self.level = Level(self.current_level)
    
    def handle_input(self):
        """Handle continuous input"""
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move_left()
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move_right()
        else:
            self.player.stop()
    
    def update(self):
        """Update game state"""
        if self.game_over or self.game_won:
            return
        
        # Update player
        self.player.update(self.level.platforms)
        
        # Update level
        self.level.update(self.player)
        
        # Check coin collection
        coins_collected = pygame.sprite.spritecollide(self.player, self.level.coins, True)
        for coin in coins_collected:
            self.score += POINTS_PER_COIN

        # Check spike collision (new enemy hazards)
        spikes_hit = pygame.sprite.spritecollide(self.player, self.level.spikes, False)
        if spikes_hit:
            if self.player.take_damage():
                if self.player.lives <= 0:
                    self.game_over = True
                else:
                    self.player.reset_position(100, SCREEN_HEIGHT - 150)

        # Check enemy collision
        enemies_hit = pygame.sprite.spritecollide(self.player, self.level.enemies, False)
        for enemy in enemies_hit:
            # Check if player is jumping on enemy (landing on top)
            if (self.player.rect.bottom <= enemy.rect.top + 15 and
                self.player.vel_y > 0):
                # Player defeats enemy by jumping on it
                enemy.kill()
                self.score += POINTS_PER_ENEMY
                self.player.vel_y = -10  # Bounce up a bit
            else:
                # Enemy damages player
                if self.player.take_damage():
                    if self.player.lives <= 0:
                        self.game_over = True
                    else:
                        self.player.reset_position(100, SCREEN_HEIGHT - 150)
                break  # Only take damage once per frame
        
        # Check boss level
        if self.level.boss:
            # Check boss collision
            if self.player.rect.colliderect(self.level.boss.rect):
                if self.player.take_damage():
                    if self.player.lives <= 0:
                        self.game_over = True
                    else:
                        self.player.reset_position(100, SCREEN_HEIGHT - 150)
            
            # Check projectile collision
            projectiles_hit = pygame.sprite.spritecollide(self.player, self.level.boss.projectiles, True)
            if projectiles_hit:
                if self.player.take_damage():
                    if self.player.lives <= 0:
                        self.game_over = True
                    else:
                        self.player.reset_position(100, SCREEN_HEIGHT - 150)
            
            # Check if player can damage boss (by jumping on it)
            # More forgiving collision - player's bottom must be near boss top
            if (self.player.rect.bottom <= self.level.boss.rect.top + 25 and
                self.player.rect.bottom >= self.level.boss.rect.top - 10 and
                self.player.rect.colliderect(self.level.boss.rect) and
                self.player.vel_y >= 0):

                if self.level.boss.take_damage():
                    self.score += POINTS_PER_BOSS
                    self.game_won = True
                else:
                    self.score += 50

                self.player.vel_y = -JUMP_STRENGTH  # Bounce off boss
        
        # Check if player fell off screen
        if self.player.rect.top > SCREEN_HEIGHT:
            if self.player.take_damage():
                if self.player.lives <= 0:
                    self.game_over = True
                else:
                    self.player.reset_position(100, SCREEN_HEIGHT - 150)
        
        # Check level completion (all coins collected and no enemies)
        if not self.level.boss and len(self.level.coins) == 0:
            self.next_level()
    
    def next_level(self):
        """Load the next level"""
        self.current_level += 1
        
        if self.current_level > NUM_LEVELS:
            self.game_won = True
        else:
            self.level = Level(self.current_level)
            self.player.reset_position(100, SCREEN_HEIGHT - 150)
            self.player.lives = min(self.player.lives + 1, STARTING_LIVES)  # Bonus life
    
    def draw(self):
        """Draw everything"""
        # Draw background based on current level
        from assets import get_assets
        assets = get_assets()
        if assets:
            bg = assets.get_background(f'level{self.current_level}')
            if bg:
                # Center the background (1280x960) on the screen (800x600)
                # Apply horizontal offset from config
                bg_x = -(bg.get_width() - SCREEN_WIDTH) // 2 + BG_HORIZONTAL_OFFSET
                bg_y = -(bg.get_height() - SCREEN_HEIGHT) // 2
                self.screen.blit(bg, (bg_x, bg_y))
            else:
                self.screen.fill((135, 206, 235))  # Sky blue background fallback
        else:
            self.screen.fill((135, 206, 235))  # Sky blue background fallback

        # Draw level
        self.level.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw HUD
        self.draw_hud()
        
        # Draw game over or win screen
        if self.game_over:
            self.draw_game_over()
        elif self.game_won:
            self.draw_game_won()
    
    def draw_hud(self):
        """Draw the heads-up display"""
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))
        
        # Lives
        lives_text = self.font.render(f"Lives: {self.player.lives}", True, BLACK)
        self.screen.blit(lives_text, (10, 50))
        
        # Level
        level_text = self.font.render(f"Level: {self.current_level}", True, BLACK)
        self.screen.blit(level_text, (SCREEN_WIDTH - 150, 10))
        
        # Username
        user_text = self.small_font.render(f"Player: {self.username}", True, BLACK)
        self.screen.blit(user_text, (SCREEN_WIDTH - 200, 50))
    
    def draw_game_over(self):
        """Draw game over screen"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = self.font.render("GAME OVER", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Final score
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)
        
        # Instructions
        instruction_text = self.small_font.render("Press R to restart or ESC to exit", True, WHITE)
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(instruction_text, instruction_rect)
    
    def draw_game_won(self):
        """Draw game won screen"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Victory text
        victory_text = self.font.render("VICTORY!", True, GREEN)
        victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(victory_text, victory_rect)
        
        # Final score
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)
        
        # Check for high score
        user_high = self.db.get_user_high_score(self.user_id)
        if self.score > user_high:
            high_score_text = self.small_font.render("NEW HIGH SCORE!", True, YELLOW)
            high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
            self.screen.blit(high_score_text, high_score_rect)
        
        # Instructions
        instruction_text = self.small_font.render("Press R to restart or ESC to exit", True, WHITE)
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        self.screen.blit(instruction_text, instruction_rect)
    
    def pause_menu(self):
        """Display pause menu"""
        paused = True
        
        resume_button = Button(SCREEN_WIDTH // 2 - 100, 250, 200, 50, "Resume", GREEN)
        quit_button = Button(SCREEN_WIDTH // 2 - 100, 320, 200, 50, "Quit", RED)
        
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    paused = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        paused = False
                
                if resume_button.handle_event(event):
                    paused = False
                
                if quit_button.handle_event(event):
                    self.running = False
                    paused = False
            
            # Draw semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(150)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            # Draw pause text
            pause_text = self.font.render("PAUSED", True, WHITE)
            pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
            self.screen.blit(pause_text, pause_rect)
            
            # Draw buttons
            resume_button.draw(self.screen, self.font)
            quit_button.draw(self.screen, self.font)
            
            pygame.display.flip()
            self.clock.tick(FPS)
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()

            if not self.game_over and not self.game_won:
                self.handle_input()
                self.update()

            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
        
        # Save score to database
        self.db.save_score(self.user_id, self.score, self.current_level)