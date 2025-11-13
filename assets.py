"""
Asset loading and management
"""
import pygame
import os
from config import *


class AssetManager:
    """Manages loading and caching of game assets"""

    def __init__(self):
        self.sprites = {}
        self.backgrounds = {}
        self.load_assets()

    def load_assets(self):
        """Load all game assets"""
        # Check if assets directory exists
        assets_dir = os.path.join(os.path.dirname(__file__), 'assets')

        if not os.path.exists(assets_dir):
            print("Assets directory not found. Using colored rectangles.")
            self.create_placeholder_assets()
            return

        # Try to load sprite images
        self.load_sprites()

        # Try to load background images
        self.load_backgrounds()

        # Create placeholders for missing assets
        self.create_placeholder_assets()

    def load_sprites(self):
        """Load sprite images and animations"""
        sprites_dir = os.path.join(os.path.dirname(__file__), 'assets', 'sprites')

        if not os.path.exists(sprites_dir):
            return

        # Try to load animation folders first
        self.load_player_animations(sprites_dir)
        self.load_enemy_animations(sprites_dir)
        self.load_coin_animations(sprites_dir)

        # Load single sprite files
        sprite_files = {
            'player': 'player.png',
            'enemy': 'enemy.png',
            'coin': 'coin.png',
            'platform': 'platform.png',
            'boss': 'boss.png'
        }

        for name, filename in sprite_files.items():
            filepath = os.path.join(sprites_dir, filename)
            if os.path.exists(filepath):
                try:
                    self.sprites[name] = pygame.image.load(filepath).convert_alpha()
                    print(f"Loaded sprite: {name}")
                except pygame.error as e:
                    print(f"Could not load {filename}: {e}")

    def load_player_animations(self, sprites_dir):
        """Load player animation frames from folders"""
        animation_folders = {
            'player_idle': 'Captain Clown Nose without Sword/01-Idle',
            'player_walk': 'Captain Clown Nose without Sword/02-Run',
            'player_jump': 'Captain Clown Nose without Sword/03-Jump'
        }

        for anim_name, folder_name in animation_folders.items():
            folder_path = os.path.join(sprites_dir, folder_name)
            if os.path.exists(folder_path):
                frames = []
                # Load all PNG files in the folder, sorted
                files = sorted([f for f in os.listdir(folder_path) if f.endswith('.png')])
                for filename in files:
                    filepath = os.path.join(folder_path, filename)
                    try:
                        frame = pygame.image.load(filepath).convert_alpha()
                        frames.append(frame)
                    except pygame.error as e:
                        print(f"Could not load {filename}: {e}")

                if frames:
                    self.sprites[anim_name] = frames
                    print(f"Loaded {len(frames)} frames for {anim_name}")

    def load_enemy_animations(self, sprites_dir):
        """Load enemy animation frames from folders"""
        enemy_folders = {
            'enemy_green': 'SlimeGreen',
            'enemy_orange': 'SlimeOrange',
            'enemy_cucumber_idle': '3-Enemy-Cucumber/1-Idle',
            'enemy_cucumber_run': '3-Enemy-Cucumber/2-Run'
        }

        for anim_name, folder_name in enemy_folders.items():
            folder_path = os.path.join(sprites_dir, folder_name)
            if os.path.exists(folder_path):
                frames = []
                # Load all PNG files in the folder, sorted by number
                files = sorted([f for f in os.listdir(folder_path) if f.endswith('.png')],
                             key=lambda x: int(x.split('.')[0]) if x.split('.')[0].isdigit() else 0)
                for filename in files:
                    filepath = os.path.join(folder_path, filename)
                    try:
                        frame = pygame.image.load(filepath).convert_alpha()
                        frames.append(frame)
                    except pygame.error as e:
                        print(f"Could not load {filename}: {e}")

                if frames:
                    self.sprites[anim_name] = frames
                    print(f"Loaded {len(frames)} frames for {anim_name}")

    def load_coin_animations(self, sprites_dir):
        """Load coin animation frames from sprite sheet"""
        diamond_path = os.path.join(sprites_dir, 'big diamond idles', 'Big Diamond Idle (18x14).png')

        if os.path.exists(diamond_path):
            try:
                sprite_sheet = pygame.image.load(diamond_path).convert_alpha()

                # The sprite sheet has frames of 18x14 pixels arranged horizontally
                frame_width = 18
                frame_height = 14
                sheet_width = sprite_sheet.get_width()
                num_frames = sheet_width // frame_width

                frames = []
                for i in range(num_frames):
                    # Extract each frame from the sprite sheet
                    frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                    frame.blit(sprite_sheet, (0, 0), (i * frame_width, 0, frame_width, frame_height))
                    frames.append(frame)

                if frames:
                    self.sprites['coin_diamond'] = frames
                    print(f"Loaded {len(frames)} frames for diamond coin animation")
            except pygame.error as e:
                print(f"Could not load diamond sprite sheet: {e}")

    def load_backgrounds(self):
        """Load background images"""
        bg_dir = os.path.join(os.path.dirname(__file__), 'assets', 'backgrounds')

        if not os.path.exists(bg_dir):
            return

        # Try to load demo.png as the main background
        demo_bg_path = os.path.join(bg_dir, 'demo.png')
        if os.path.exists(demo_bg_path):
            try:
                bg = pygame.image.load(demo_bg_path).convert_alpha()
                # DON'T scale - use original size for zoom effect
                # The game will crop/scroll through this larger image
                # Use this background for all levels
                self.backgrounds['level1'] = bg
                self.backgrounds['level2'] = bg
                self.backgrounds['level3'] = bg
                print(f"Loaded demo.png background (original size: {bg.get_width()}x{bg.get_height()})")
            except pygame.error as e:
                print(f"Could not load demo.png: {e}")

        # Try to load individual level backgrounds
        bg_files = {
            'level1': 'level1.png',
            'level2': 'level2.png',
            'level3': 'level3.png'
        }

        for name, filename in bg_files.items():
            filepath = os.path.join(bg_dir, filename)
            if os.path.exists(filepath):
                try:
                    bg = pygame.image.load(filepath).convert()
                    # Scale to screen size
                    bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
                    self.backgrounds[name] = bg
                    print(f"Loaded background: {name}")
                except pygame.error as e:
                    print(f"Could not load {filename}: {e}")

    def create_tiled_background(self, tile_image, width, height):
        """Create a tiled background surface from a tile image (like Godot)"""
        surface = pygame.Surface((width, height))
        tile_width = tile_image.get_width()
        tile_height = tile_image.get_height()

        # Tile the image across the entire surface
        for x in range(0, width, tile_width):
            for y in range(0, height, tile_height):
                surface.blit(tile_image, (x, y))

        return surface

    def create_placeholder_assets(self):
        """Create colored rectangles as placeholders for missing assets"""
        # Player placeholder
        if 'player' not in self.sprites:
            surf = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
            surf.fill(BLUE)
            self.sprites['player'] = surf

        # Enemy placeholder
        if 'enemy' not in self.sprites:
            surf = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
            surf.fill(RED)
            self.sprites['enemy'] = surf

        # Coin placeholder
        if 'coin' not in self.sprites:
            surf = pygame.Surface((20, 20))
            surf.fill(YELLOW)
            self.sprites['coin'] = surf

        # Platform placeholder
        if 'platform' not in self.sprites:
            surf = pygame.Surface((100, PLATFORM_HEIGHT))
            surf.fill(GRAY)
            self.sprites['platform'] = surf

        # Boss placeholder
        if 'boss' not in self.sprites:
            surf = pygame.Surface((BOSS_WIDTH, BOSS_HEIGHT))
            surf.fill((128, 0, 128))  # Purple
            self.sprites['boss'] = surf

        # Background placeholders
        for level in ['level1', 'level2', 'level3']:
            if level not in self.backgrounds:
                surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                # Different colors for different levels
                if level == 'level1':
                    surf.fill((135, 206, 235))  # Sky blue
                elif level == 'level2':
                    surf.fill((100, 149, 237))  # Cornflower blue
                else:
                    surf.fill((70, 70, 100))    # Dark blue-gray
                self.backgrounds[level] = surf

    def get_sprite(self, name):
        """Get a sprite by name"""
        return self.sprites.get(name)

    def get_background(self, level_name):
        """Get a background by level name"""
        return self.backgrounds.get(level_name)


# Global asset manager instance
asset_manager = None

def init_assets():
    """Initialize the asset manager"""
    global asset_manager
    asset_manager = AssetManager()
    return asset_manager

def get_assets():
    """Get the global asset manager"""
    return asset_manager
