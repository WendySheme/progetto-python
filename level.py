"""
Level layouts and configurations for the platform game
"""
import pygame
from config import *
from entities import Platform, Enemy, Coin, Boss, Spike
from tiled_loader import load_level_from_tiled


class Level:
    """Represents a game level with platforms, enemies, and collectibles"""

    def __init__(self, level_number):
        self.level_number = level_number
        self.platforms = []
        self.enemies = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.spikes = pygame.sprite.Group()  # Add spikes group
        self.boss = None
        self.tiled_loader = None
        self.player_spawn = None

        # Try to load from Tiled first
        tiled_data = load_level_from_tiled(level_number)
        if tiled_data:
            print(f"Loading level {level_number} from Tiled map")
            self.platforms = tiled_data['platforms']
            self.enemies = tiled_data['enemies']
            self.coins = tiled_data['coins']
            self.boss = tiled_data['boss']
            self.player_spawn = tiled_data.get('player_spawn')
            self.tiled_loader = tiled_data.get('loader')
        else:
            # Fallback to hardcoded levels
            print(f"Loading level {level_number} from hardcoded data")
            if level_number == 1:
                self.load_level_1()
            elif level_number == 2:
                self.load_level_2()
            elif level_number == 3:
                self.load_level_3()

    def update(self, player):
        """Update level entities"""
        # Update enemies
        for enemy in self.enemies:
            enemy.update()

        # Update coins (for animations)
        for coin in self.coins:
            coin.update()

        # Update boss if exists
        if self.boss:
            self.boss.update(player.rect.x)

    def draw(self, screen):
        """Draw all level entities"""
        # DEBUG: Show red boxes to see platform positions with labels
        font = pygame.font.Font(None, 16)
        for i, platform in enumerate(self.platforms):
            pygame.draw.rect(screen, (255, 0, 0), platform.rect, 2)  # Red outline
            # Draw platform info (index, x, width)
            if platform.rect.width > 10:  # Only label visible platforms
                text = font.render(f"#{i} x:{platform.rect.x} w:{platform.rect.width}", True, (255, 255, 0))
                screen.blit(text, (platform.rect.x + 2, platform.rect.y - 15))

        # Draw enemies (cucumber with animations)
        self.enemies.draw(screen)

        # Draw coins (diamond with animations)
        self.coins.draw(screen)

        # Spikes are invisible hazards (no drawing needed)

    def load_level_1(self):
        """Level 1 layout - aligned with centered demo.png background"""
        # Background is 1280x960, screen is 800x600
        # Background offset: x = -290 (shifted left by 50 from center), y = -180
        # To convert from background coords to screen coords: screen = bg - offset
        # So: screen_x = bg_x - 290, screen_y = bg_y - 180

        # Add invisible walls on left and right edges to prevent falling off
        for y in range(0, SCREEN_HEIGHT, 20):
            self.platforms.append(Platform(-50, y, 50))  # Left wall
            # Right wall is added separately below

        # Bottom left ground platform (lowest visible platform on left)
        self.platforms.append(Platform(40, 540, 350))

        # Lower middle platforms (around the small stone platforms)
        self.platforms.append(Platform(345, 510, 40))

        #piattaforme centrali
        self.platforms.append(Platform(400, 480, 40))

        self.platforms.append(Platform(455, 450, 30))
 
        self.platforms.append(Platform(476, 410, 30))
        
        self.platforms.append(Platform(600, 410, 150))  # Small platform

        # Right wall - ONLY at bottom, next to chest area
        for y in range(500, SCREEN_HEIGHT, 20):
            self.platforms.append(Platform(SCREEN_WIDTH, y, 0))  # Right wall partial


        # cucumber enemies 
        self.enemies.add(Enemy(150, 485, 80, enemy_type='cucumber'))  # First platform - patrols left side
        self.enemies.add(Enemy(460, 355, 50, enemy_type='cucumber'))  # Small platform with tree
       

        # Add coins scattered across platforms
        self.coins.add(Coin(80, 440))
        self.coins.add(Coin(325, 430))
        self.coins.add(Coin(410, 400))
       # Top platform

        

    def load_level_2(self):
        """Level 2 layout - more challenging"""
        # Ground platform
        self.platforms.append(Platform(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH))

        # Additional platforms - tighter jumps
        self.platforms.append(Platform(100, 470, 120))
        self.platforms.append(Platform(280, 410, 120))
        self.platforms.append(Platform(460, 350, 120))
        self.platforms.append(Platform(640, 290, 120))
        self.platforms.append(Platform(300, 230, 180))

        # More enemies
        self.enemies.add(Enemy(110, 430, 70))
        self.enemies.add(Enemy(290, 370, 70))
        self.enemies.add(Enemy(470, 310, 70))

        # More coins
        self.coins.add(Coin(140, 445))
        self.coins.add(Coin(320, 385))
        self.coins.add(Coin(500, 325))
        self.coins.add(Coin(680, 265))
        self.coins.add(Coin(350, 205))

    def load_level_3(self):
        """Level 3 layout - boss level"""
        # Ground platform
        self.platforms.append(Platform(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH))

        # Platforms for boss fight - positioned to allow jumping on boss
        # Left platform - for dodging
        self.platforms.append(Platform(50, 420, 120))
        # Right platform - for dodging
        self.platforms.append(Platform(630, 420, 120))
        # Center high platform - to jump down on boss
        self.platforms.append(Platform(300, 300, 200))
        # Side platforms at medium height
        self.platforms.append(Platform(100, 350, 120))
        self.platforms.append(Platform(580, 350, 120))

        # Boss - positioned lower on the ground for easier access
        # Boss will patrol the ground level
        self.boss = Boss(SCREEN_WIDTH // 2 - BOSS_WIDTH // 2, SCREEN_HEIGHT - 50 - BOSS_HEIGHT)