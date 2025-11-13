"""
Game entities: platforms, enemies, coins, and boss
"""
import pygame
import random
from config import *
from assets import get_assets


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width):
        super().__init__()
        # Load platform sprite and tile it
        assets = get_assets()
        if assets:
            sprite = assets.get_sprite('platform')
            # Tile the platform sprite to match the width
            self.image = pygame.Surface((width, PLATFORM_HEIGHT))
            for i in range(0, width, sprite.get_width()):
                tile = pygame.transform.scale(sprite, (min(sprite.get_width(), width - i), PLATFORM_HEIGHT))
                self.image.blit(tile, (i, 0))
        else:
            self.image = pygame.Surface((width, PLATFORM_HEIGHT))
            self.image.fill(GRAY)

        self.rect = self.image.get_rect()
        self.rect.x = x + PLATFORM_HORIZONTAL_OFFSET
        self.rect.y = y


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Load coin sprite with animation support
        assets = get_assets()
        self.animations = None
        self.has_animations = False
        self.animation_frame = 0
        self.animation_counter = 0
        self.animation_speed = 0.15

        if assets:
            # Try to load diamond animation first
            diamond_frames = assets.get_sprite('coin_diamond')
            if diamond_frames and isinstance(diamond_frames, list):
                self.animations = diamond_frames
                self.has_animations = True
                # Set initial image from first frame (scaled up 2x for visibility)
                frame = self.animations[0]
                self.image = pygame.transform.scale(frame, (36, 28))  # 18x14 scaled 2x
            else:
                # Fallback to static coin sprite
                sprite = assets.get_sprite('coin')
                if sprite:
                    self.image = pygame.transform.scale(sprite, (20, 20))
                else:
                    self.image = pygame.Surface((20, 20))
                    self.image.fill(YELLOW)
        else:
            self.image = pygame.Surface((20, 20))
            self.image.fill(YELLOW)

        self.rect = self.image.get_rect()
        self.rect.x = x + PLATFORM_HORIZONTAL_OFFSET
        self.rect.y = y

    def update(self):
        """Update coin animation"""
        if not self.has_animations:
            return

        # Cycle through animation frames
        self.animation_counter += self.animation_speed
        if self.animation_counter >= 1:
            self.animation_counter = 0
            self.animation_frame = (self.animation_frame + 1) % len(self.animations)

        # Get current frame and scale it
        frame = self.animations[int(self.animation_frame)]
        self.image = pygame.transform.scale(frame, (36, 28))  # 18x14 scaled 2x


class Spike(pygame.sprite.Sprite):
    """Spike hazard that damages the player"""
    def __init__(self, x, y, width=15, height=15):
        super().__init__()
        # Create invisible spike hitbox
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))  # Fully transparent

        self.rect = self.image.get_rect()
        self.rect.x = x + PLATFORM_HORIZONTAL_OFFSET
        self.rect.y = y
        self.damage = 1  # Damage dealt to player


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, movement_range=100, enemy_type='cucumber'):
        super().__init__()

        # Load enemy sprite with animation support
        assets = get_assets()
        self.animations = {}
        self.has_animations = False
        self.enemy_type = enemy_type
        self.current_animation = 'run'

        if assets:
            if enemy_type == 'cucumber':
                # Load cucumber animations
                idle_frames = assets.get_sprite('enemy_cucumber_idle')
                run_frames = assets.get_sprite('enemy_cucumber_run')

                if idle_frames and run_frames:
                    self.animations['idle'] = idle_frames
                    self.animations['run'] = run_frames
                    self.has_animations = True
                    self.animation_frame = 0
                    self.animation_counter = 0
                    self.animation_speed = 0.2

                    # Set initial image from first run frame
                    frame = self.animations['run'][0]
                    self.image = pygame.transform.scale(frame, (ENEMY_WIDTH, ENEMY_HEIGHT))
                else:
                    self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
                    self.image.fill(RED)
            else:
                # Fallback to slime or generic enemy
                slime_type = random.choice(['enemy_green', 'enemy_orange'])
                frames = assets.get_sprite(slime_type)

                if frames and isinstance(frames, list):
                    self.animations['run'] = frames
                    self.has_animations = True
                    self.animation_frame = 0
                    self.animation_counter = 0
                    self.animation_speed = 0.15

                    # Set initial image from first frame
                    frame = self.animations['run'][0]
                    self.image = pygame.transform.scale(frame, (ENEMY_WIDTH, ENEMY_HEIGHT))
                else:
                    # Try single sprite file
                    sprite = assets.get_sprite('enemy')
                    if sprite:
                        self.image = pygame.transform.scale(sprite, (ENEMY_WIDTH, ENEMY_HEIGHT))
                    else:
                        self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
                        self.image.fill(RED)
        else:
            self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
            self.image.fill(RED)

        self.rect = self.image.get_rect()
        self.rect.x = x + PLATFORM_HORIZONTAL_OFFSET
        self.rect.y = y

        self.start_x = x + PLATFORM_HORIZONTAL_OFFSET
        self.movement_range = movement_range
        self.direction = 1  # 1 for right, -1 for left
        self.speed = ENEMY_SPEED

    def update(self):
        """Update enemy movement with simple patrol AI"""
        self.rect.x += self.speed * self.direction

        # Change direction when reaching movement range
        if self.rect.x >= self.start_x + self.movement_range:
            self.direction = -1
        elif self.rect.x <= self.start_x:
            self.direction = 1

        # Update animation
        self.update_animation()

    def update_animation(self):
        """Update enemy animation"""
        if not self.has_animations:
            return

        # Get current animation frames
        if self.current_animation in self.animations:
            frames = self.animations[self.current_animation]
        else:
            return

        # Cycle through animation frames
        self.animation_counter += self.animation_speed
        if self.animation_counter >= 1:
            self.animation_counter = 0
            self.animation_frame = (self.animation_frame + 1) % len(frames)

        # Get current frame and scale it
        frame = frames[int(self.animation_frame)]
        scaled_frame = pygame.transform.scale(frame, (ENEMY_WIDTH, ENEMY_HEIGHT))

        # Flip if moving left
        if self.direction == -1:
            scaled_frame = pygame.transform.flip(scaled_frame, True, False)

        self.image = scaled_frame


class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Load boss sprite
        assets = get_assets()
        if assets:
            sprite = assets.get_sprite('boss')
            self.image = pygame.transform.scale(sprite, (BOSS_WIDTH, BOSS_HEIGHT))
        else:
            self.image = pygame.Surface((BOSS_WIDTH, BOSS_HEIGHT))
            self.image.fill((128, 0, 128))  # Purple

        self.rect = self.image.get_rect()
        self.rect.x = x + PLATFORM_HORIZONTAL_OFFSET
        self.rect.y = y

        self.health = BOSS_HEALTH
        self.max_health = BOSS_HEALTH
        self.speed = BOSS_SPEED
        self.direction = 1
        self.attack_timer = 0
        self.projectiles = pygame.sprite.Group()
    
    def update(self, player_x):
        """Update boss with advanced AI"""
        # Move towards player
        if player_x < self.rect.x:
            self.rect.x -= self.speed
        elif player_x > self.rect.x:
            self.rect.x += self.speed
        
        # Keep boss on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        
        # Attack timer
        self.attack_timer += 1
        if self.attack_timer >= 90:  # Attack every 1.5 seconds
            self.shoot_projectile()
            self.attack_timer = 0
        
        # Update projectiles
        self.projectiles.update()
    
    def shoot_projectile(self):
        """Boss shoots a projectile"""
        projectile = BossProjectile(self.rect.centerx, self.rect.centery)
        self.projectiles.add(projectile)
    
    def take_damage(self):
        """Boss takes damage"""
        self.health -= 1
        return self.health <= 0
    
    def draw_health_bar(self, screen):
        """Draw boss health bar"""
        bar_width = 200
        bar_height = 20
        bar_x = SCREEN_WIDTH // 2 - bar_width // 2
        bar_y = 20
        
        # Background
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        
        # Health
        health_width = int((self.health / self.max_health) * bar_width)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, health_width, bar_height))
        
        # Border
        pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 2)


class BossProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill((255, 100, 0))  # Orange
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = 7
    
    def update(self):
        """Move projectile downward"""
        self.rect.y += self.speed
        
        # Remove if off screen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()