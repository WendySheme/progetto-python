"""
Player class with movement, jumping, and collision detection
"""
import pygame
from config import *
from assets import get_assets


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # Load player animations from asset manager
        assets = get_assets()
        self.animations = {}
        self.has_animations = False

        if assets:
            # Try to load animation frames
            idle_frames = assets.get_sprite('player_idle')
            walk_frames = assets.get_sprite('player_walk')
            jump_frames = assets.get_sprite('player_jump')

            if idle_frames and isinstance(idle_frames, list):
                self.animations['idle'] = idle_frames
                self.animations['walk'] = walk_frames if walk_frames else idle_frames
                self.animations['jump'] = jump_frames if jump_frames else idle_frames
                self.has_animations = True
                self.image = pygame.transform.scale(idle_frames[0], (PLAYER_WIDTH, PLAYER_HEIGHT))
            else:
                # Try single sprite
                sprite = assets.get_sprite('player')
                if sprite:
                    self.image = pygame.transform.scale(sprite, (PLAYER_WIDTH, PLAYER_HEIGHT))
                else:
                    self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
                    self.image.fill(GREEN)
        else:
            self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
            self.image.fill(GREEN)

        self.rect = self.image.get_rect()
        self.rect.x = x + PLATFORM_HORIZONTAL_OFFSET
        self.rect.y = y

        # Animation state
        self.current_animation = 'idle'
        self.animation_frame = 0
        self.animation_speed = 0.15  # Frames per game tick
        self.animation_counter = 0

        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.lives = STARTING_LIVES
        self.invincible = False
        self.invincible_timer = 0
        self.facing_right = True
    
    def update(self, platforms):
        """Update player position and handle physics"""
        # Handle invincibility timer
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
        
        # Apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED
        
        # Horizontal movement
        self.rect.x += self.vel_x
        self.check_collision_x(platforms)
        
        # Vertical movement
        self.rect.y += self.vel_y
        self.on_ground = False
        self.check_collision_y(platforms)
        
        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

        # Update animation
        self.update_animation()
    
    def check_collision_x(self, platforms):
        """Check for horizontal collisions with platforms"""
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0:  # Moving right
                    self.rect.right = platform.rect.left
                elif self.vel_x < 0:  # Moving left
                    self.rect.left = platform.rect.right
    
    def check_collision_y(self, platforms):
        """Check for vertical collisions with platforms"""
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:  # Falling
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:  # Jumping
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0
    
    def jump(self):
        """Make the player jump if on ground"""
        if self.on_ground:
            self.vel_y = -JUMP_STRENGTH
    
    def move_left(self):
        """Move player left"""
        self.vel_x = -PLAYER_SPEED
        self.facing_right = False
    
    def move_right(self):
        """Move player right"""
        self.vel_x = PLAYER_SPEED
        self.facing_right = True
    
    def stop(self):
        """Stop horizontal movement"""
        self.vel_x = 0
    
    def take_damage(self):
        """Player takes damage"""
        if not self.invincible:
            self.lives -= 1
            self.invincible = True
            self.invincible_timer = 120  # 2 seconds of invincibility
            return True
        return False

    def update_animation(self):
        """Update player animation based on state"""
        if not self.has_animations:
            return

        # Determine which animation to play
        if not self.on_ground:
            new_animation = 'jump'
        elif abs(self.vel_x) > 0:
            new_animation = 'walk'
        else:
            new_animation = 'idle'

        # Reset frame if animation changed
        if new_animation != self.current_animation:
            self.current_animation = new_animation
            self.animation_frame = 0
            self.animation_counter = 0

        # Update animation frame
        self.animation_counter += self.animation_speed
        if self.animation_counter >= 1:
            self.animation_counter = 0
            self.animation_frame = (self.animation_frame + 1) % len(self.animations[self.current_animation])

        # Get current frame and scale it
        frames = self.animations[self.current_animation]
        frame = frames[int(self.animation_frame)]
        scaled_frame = pygame.transform.scale(frame, (PLAYER_WIDTH, PLAYER_HEIGHT))

        # Flip if facing left
        if not self.facing_right:
            scaled_frame = pygame.transform.flip(scaled_frame, True, False)

        self.image = scaled_frame

    def draw(self, screen):
        """Draw the player with invincibility flashing effect"""
        if not self.invincible or (self.invincible_timer % 10 < 5):
            screen.blit(self.image, self.rect)
    
    def reset_position(self, x, y):
        """Reset player to starting position"""
        self.rect.x = x + PLATFORM_HORIZONTAL_OFFSET
        self.rect.y = y
        self.vel_x = 0
        self.vel_y = 0