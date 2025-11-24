import sys
import math
import random
import os
import socket
import threading
import json
import time
import pygame
from pygame.locals import *

# Basic display / timing constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Fullscreen flag shorthand (used when toggling)
FULLSCREEN = pygame.FULLSCREEN

# Common colors
BACKGROUND_COLOR = (10, 10, 20)
FONT_COLOR = (220, 220, 220)
BORDER_COLOR = (60, 60, 60)
HIGHLIGHT_COLOR = (255, 215, 0)

# Help / UI palette
HELP_BG_COLOR = (8, 10, 20)
HELP_TEXT_COLOR = (230, 230, 230)

# Settings UI colors and defaults
SETTINGS_BG_COLOR = (30, 30, 30)
SETTINGS_TEXT_COLOR = (230, 230, 230)
SETTINGS_BAR_BG = (60, 60, 60)
SETTINGS_BAR_FG = (120, 180, 220)
SETTINGS_HIGHLIGHT = (100, 100, 180)

# Game metadata
GAME_VERSION = "0.9"

# Default settings (volumes + key bindings)
DEFAULT_SETTINGS = {
    "music_volume": 0.5,
    "sfx_volume": 0.8,
    # Player 1 keys
    "p1_up": K_w,
    "p1_down": K_s,
    "p1_left": K_a,
    "p1_right": K_d,
    "p1_fire": K_SPACE,
    # Player 2 keys
    "p2_up": K_UP,
    "p2_down": K_DOWN,
    "p2_left": K_LEFT,
    "p2_right": K_RIGHT,
    "p2_fire": K_RETURN,
}


# Ship appearance
SHIP_OUTLINE_COLOR = (255, 255, 255)
BULLET_COLOR = (255, 255, 255)
SHIP_SIZE = 40
BULLET_SIZE = 6
UNFIRED_BULLET_COLOR = (200, 200, 200)

# Available colors
SHIP_COLORS = [
    (255, 165, 0),    # Orange
    (255, 0, 0),      # Red
    (0, 0, 255),      # Blue
    (0, 255, 0),      # Green
    (128, 0, 128),    # Purple
    (255, 255, 0),    # Yellow
    (173, 216, 230),  # Light Blue
    (144, 238, 144),  # Light Green
    (255, 20, 147),   # Deep Pink
    (0, 191, 255),    # Deep Sky Blue
    (255, 69, 0),     # Red-Orange
    (138, 43, 226),   # Blue Violet
    (50, 205, 50),    # Lime Green
    (255, 140, 0),    # Dark Orange
    (70, 130, 180),   # Steel Blue
    (218, 112, 214),  # Orchid
]

# Default colors per ship
DEFAULT_SHIP_COLORS = {
    "Zaba": (50, 205, 50),      # lime green (frog-like)
    "Rekin": (70, 130, 180),    # steel blue (shark-like)
    "Komar": (138, 43, 226),    # blue violet (mosquito-like)
    "Osa": (255, 165, 0),       # orange (wasp-like)
    "Kombuz": (255, 69, 0),     # red-orange (explosion-themed)
    "Gwiazdka": (0, 191, 255),  # deep sky blue (star-like)
    "Rift": (255, 20, 147),     # deep pink (rift-like energy)
    "Nexus": (218, 112, 214)    # orchid (energy cross)
}

# Asset paths configuration
# Default assets dir (local)
LOCAL_ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
# Project-specific packaged assets for the new port
FLOX_ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "2d_flox", "assets")
# Extracted APK assets (user provided)
DUAL_ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dual", "assets")

# Resolve ASSETS_DIR in order of preference: packaged FLOX assets -> extracted dual assets -> local assets
if os.path.exists(FLOX_ASSETS_DIR):
    ASSETS_DIR = FLOX_ASSETS_DIR
elif os.path.exists(DUAL_ASSETS_DIR):
    ASSETS_DIR = DUAL_ASSETS_DIR
else:
    ASSETS_DIR = LOCAL_ASSETS_DIR

# Optional asset paths 
BACKGROUND_IMAGE_PATH = None  # e.g. os.path.join(ASSETS_DIR, "background.png")
# If extracted APK assets exist, prefer a background pattern from them
_candidate_backgrounds = [
    os.path.join(DUAL_ASSETS_DIR, "BackgroundPattern11.png"),
    os.path.join(DUAL_ASSETS_DIR, "BackgroundPattern.png"),
    os.path.join(DUAL_ASSETS_DIR, "WIFI_Background.png"),
]
for _c in _candidate_backgrounds:
    if os.path.exists(_c):
        BACKGROUND_IMAGE_PATH = _c
        break

# Sound configuration
SOUND_PATHS = {
    # Global sounds (prefer extracted APK assets if present)
    'menu_click': os.path.join(DUAL_ASSETS_DIR, "sfxButtonPress2.ogg"),
    'background': os.path.join(DUAL_ASSETS_DIR, "mzkDefendAmbient1.ogg"),
    'ship_explosion': os.path.join(DUAL_ASSETS_DIR, "boomboom.ogg"),
    
    # Ship-specific sounds (map to closest matches in APK assets)
    'zaba_shoot': os.path.join(DUAL_ASSETS_DIR, "shoot.ogg"),
    'zaba_hit': os.path.join(DUAL_ASSETS_DIR, "hithh2.ogg"),
    'zaba_charge': os.path.join(DUAL_ASSETS_DIR, "shoot_laser_repeat.ogg"),
    
    'rekin_shoot': os.path.join(DUAL_ASSETS_DIR, "shoot2.ogg"),
    'rekin_hit': os.path.join(DUAL_ASSETS_DIR, "hithh2.ogg"),
    'rekin_charge': os.path.join(DUAL_ASSETS_DIR, "shoot_laser_repeat.ogg"),
    
    'osa_shoot': os.path.join(DUAL_ASSETS_DIR, "shooti2.ogg"),
    'osa_hit': os.path.join(DUAL_ASSETS_DIR, "hithh2.ogg"),
    'osa_charge': os.path.join(DUAL_ASSETS_DIR, "shoot_laser_repeat.ogg"),
    
    'komar_shoot': os.path.join(DUAL_ASSETS_DIR, "shooti4.ogg"),
    'komar_hit': os.path.join(DUAL_ASSETS_DIR, "hithh2.ogg"),
    'komar_charge': os.path.join(DUAL_ASSETS_DIR, "shoot_laser_repeat.ogg"),
    'komar_beam': os.path.join(DUAL_ASSETS_DIR, "shoot_laser_repeat.ogg"),
    
    'kombuz_shoot': os.path.join(DUAL_ASSETS_DIR, "shoot_i1.ogg"),
    'kombuz_hit': os.path.join(DUAL_ASSETS_DIR, "hithh2.ogg"),
    'kombuz_charge': os.path.join(DUAL_ASSETS_DIR, "shoot_i3.ogg"),
    'kombuz_mine_arm': os.path.join(DUAL_ASSETS_DIR, "sfxScaleIn.ogg"),
    'kombuz_mine_explode': os.path.join(DUAL_ASSETS_DIR, "boomboom.ogg"),
    
    # Gwiazdka ship sounds
    'gwiazdka_shoot': os.path.join(DUAL_ASSETS_DIR, "shoot_i4.ogg"),
    'gwiazdka_hit': os.path.join(DUAL_ASSETS_DIR, "hithh2.ogg"),
    'gwiazdka_charge': os.path.join(DUAL_ASSETS_DIR, "shoot_laser_repeat.ogg"),
    'gwiazdka_nova': os.path.join(DUAL_ASSETS_DIR, "shoott2.ogg"),
    
    # Rift ship sounds
    'rift_shoot': os.path.join(DUAL_ASSETS_DIR, "shoott2.ogg"),
    'rift_hit': os.path.join(DUAL_ASSETS_DIR, "hithh2.ogg"),
    'rift_charge': os.path.join(DUAL_ASSETS_DIR, "shoot_laser_repeat.ogg"),
    'rift_sweep': os.path.join(DUAL_ASSETS_DIR, "mzkSquareDuel1.ogg"),
    
    # Nexus ship sounds
    'nexus_shoot': os.path.join(DUAL_ASSETS_DIR, "shoot_i5.ogg"),
    'nexus_hit': os.path.join(DUAL_ASSETS_DIR, "hithh2.ogg"),
    'nexus_charge': os.path.join(DUAL_ASSETS_DIR, "shoot_laser_repeat.ogg"),
    'nexus_cross': os.path.join(DUAL_ASSETS_DIR, "mzkCircleDuel1.ogg")
}


def safe_load_sound(path):
    if not path:
        return None
    # Try the provided path first; if not present, try to find the file in the local `assets/` dir
    try:
        if os.path.exists(path):
            return pygame.mixer.Sound(path)
        # fallback to ASSETS_DIR with same basename
        base = os.path.basename(path)
        alt = os.path.join(ASSETS_DIR, base)
        if os.path.exists(alt):
            return pygame.mixer.Sound(alt)
        return None
    except Exception:
        return None

# Load sounds (safe)
SOUNDS = {name: safe_load_sound(path) for name, path in SOUND_PATHS.items()}

# ----------------- Image / Sprite Loading Helpers -----------------
# Load images preferring extracted APK assets then local assets directory.
SPRITE_CACHE = {}
def load_image(filename, alpha=True):
    # Try dual assets then local assets
    paths = [os.path.join(DUAL_ASSETS_DIR, filename), os.path.join(ASSETS_DIR, filename)]
    for p in paths:
        if p and os.path.exists(p):
            try:
                img = pygame.image.load(p)
                if alpha:
                    return img.convert_alpha()
                return img.convert()
            except Exception:
                continue
    return None

def tint_image(img, color):
    if img is None:
        return None
    # Create a tinted copy using BLEND_MULT
    try:
        tinted = img.copy()
        tint_surf = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
        tint_surf.fill(color + (0,))
        tinted.blit(tint_surf, (0,0), special_flags=pygame.BLEND_RGB_MULT)
        return tinted
    except Exception:
        return img

# Preload ship sprite filenames by shape
SHIP_SHAPE_ASSET = {
    'square': 'shipSquareBodyFill.png',
    'triangle': 'shipTriangleBodyFill.png',
    'circle': 'shipCircleBodyFill.png',
    'hexagon': 'shipHexagonBodyFill.png',
    'kite': 'shipKiteBodyFill.png',
    'star': 'shipStarBodyFill.png',
    'chevron': 'shipChevronBodyFill.png',
    'cross': 'shipCrossBodyFill.png',
    'nexus': 'shipCrossBodyFill.png',
    'boomerang': 'shipChevronBodyFill.png'
}

# Direct mapping from ship type names to asset filenames (from APK assets)
SHIP_TYPE_ASSET = {
    'Zaba': 'shipSquareBodyFill.png',
    'Rekin': 'shipTriangleBodyFill.png',
    'Komar': 'shipKiteBodyFill.png',
    'Osa': 'shipChevronBodyFill.png',
    'Kombuz': 'shipCircleBodyFill.png',
    'Gwiazdka': 'shipStarBodyFill.png',
    'Rift': 'shipHexagonBodyFill.png',
    'Nexus': 'shipCrossBodyFill.png'
}

def get_ship_sprite(ship_type, color, size):
    key = (ship_type, color, size)
    if key in SPRITE_CACHE:
        return SPRITE_CACHE[key]
    # prefer explicit ship-type asset mapping, then fall back to shape mapping
    fname = SHIP_TYPE_ASSET.get(ship_type)
    if not fname:
        config = SHIPS.get(ship_type, {})
        shape = config.get('shape', 'square')
        fname = SHIP_SHAPE_ASSET.get(shape, 'shipSquareBodyFill.png')
    img = load_image(fname)
    if img:
        img = pygame.transform.smoothscale(img, (size, size))
        img = tint_image(img, color)
    SPRITE_CACHE[key] = img
    return img

# Bullet sprites mapping
BULLET_SPRITE_MAP = {
    'circle': 'bulletCircleBodyOutline.png',
    'square': 'bulletSquareBodyOutline.png',
    'triangle': 'bulletTriangleBodyOutline.png',
    'hexagon': 'bulletHexagonBodyOutline.png',
    'kite': 'bulletKiteBody.png',
    'cross': 'bulletCrossBodyFill.png',
    'diamond': 'bulletKiteBody.png'
}

def get_bullet_sprite(bullet_shape, size, color):
    key = (bullet_shape, size, color)
    if key in SPRITE_CACHE:
        return SPRITE_CACHE[key]
    fname = BULLET_SPRITE_MAP.get(bullet_shape)
    img = None
    if fname:
        img = load_image(fname)
    if img:
        img = pygame.transform.smoothscale(img, (int(size), int(size)))
        img = tint_image(img, color)
    SPRITE_CACHE[key] = img
    return img

def play_sound(sound_name, ship_type=None):
    """Helper to safely play sounds by name, with optional ship-specific variant"""
    # If ship type is provided, try to play ship-specific sound first
    if ship_type:
        ship_sound_name = f"{ship_type.lower()}_{sound_name}"
        if ship_sound_name in SOUNDS and SOUNDS[ship_sound_name]:
            try:
                SOUNDS[ship_sound_name].play()
                return
            except Exception:
                pass
    
    # Fall back to generic sound if ship-specific one not available
    if sound_name in SOUNDS and SOUNDS[sound_name]:
        try:
            SOUNDS[sound_name].play()
        except Exception:
            pass

# Game mechanics
MAX_CHARGE_TIME = 60
MINE_EXPLOSION_TIME = 3 * FPS
CHARGED_MINE_EXPLOSION_TIME = 4 * FPS
BULLET_OFFSET = 20
BULLET_SPACING = 8
# Bullet speed multiplier to make bullets feel snappier
GLOBAL_BULLET_SPEED_MULT = 1.5

# Ship configurations - EVERYTHING IS CONFIGURABLE HERE
SHIPS = {
    "Zaba": {
        # Core stats
        "health": 7,
        "bullets": 6,
        "shape": "square",
        
        # Movement configuration
        "speed": 3,
        "acceleration": 0.5,
        "deceleration": 0.3,
        
        # Bullet configuration
        "bullet_shape": "square",
        "bullet_size": 6,
        "bullet_speed": 5,
        "bullet_damage": 1,
        "bullet_recharge_time": 20,
        
        # Charge attack configuration
        "charged_bullet_speed": 7,
        "charged_bullet_size": 12,
        "charged_damage_multiplier": 2,
        "charge_rate": 1.0,  # Full charge in MAX_CHARGE_TIME frames
        
        # Sound configuration
        "shoot_sound": "zaba_shoot",
        "charge_sound": "zaba_charge",
        "hit_sound": "zaba_hit",
        
        # Visual effects
        "muzzle_flash_size": 4,
        "muzzle_flash_count": 3,
        "hit_particle_size": 3,
        "hit_particle_count": 4,
        "charge_particle_size": 2,
        "charge_particle_rate": 5,  # Frames between particles
        
        "description": "Square ship with charged block attack"
    },
    "Rekin": {
        # Core stats
        "health": 6,
        "bullets": 6,
        "shape": "triangle",
        
        # Movement configuration
        "speed": 5,
        "acceleration": 0.8,
        "deceleration": 0.4,
        
        # Bullet configuration
        "bullet_shape": "triangle",
        "bullet_size": 5,
        "bullet_speed": 6,
        "bullet_damage": 1,
        "bullet_recharge_time": 25,
        "bullet_spread": 8,  # Spacing for dual shot
        
        # Charge attack configuration
        "charged_bullet_speed": 8,
        "charged_bullet_size": 10,
        "charged_damage_multiplier": 1.5,
        "charge_rate": 1.2,  # Faster charge than other ships
        "spread_angle": 15,  # Degrees between spread shots
        
        # Sound configuration
        "shoot_sound": "rekin_shoot",
        "charge_sound": "rekin_charge",
        "hit_sound": "rekin_hit",
        
        # Visual effects
        "muzzle_flash_size": 3,
        "muzzle_flash_count": 4,
        "hit_particle_size": 3,
        "hit_particle_count": 5,
        "charge_particle_size": 2,
        "charge_particle_rate": 4,
        
        "description": "Fast triangular ship with triple shot"
    },
    "Osa": {
        # Core stats
        "health": 5,
        "bullets": 16,
        "shape": "circle",
        
        # Movement configuration
        "speed": 4,
        "acceleration": 0.6,
        "deceleration": 0.3,
        
        # Bullet configuration
        "bullet_shape": "circle",
        "bullet_size": 4,
        "bullet_speed": 7,
        "bullet_damage": 0.5,  # Lower damage but rapid fire
        "bullet_recharge_time": 15,
        
        # Charge attack configuration
        "charged_bullet_speed": 12,
        "charged_bullet_size": 8,
        "charged_damage_multiplier": 1.5,
        "charge_rate": 1.5,  # Fastest charge
        "spread_count": 5,  # Number of bullets in spread
        
        # Sound configuration
        "shoot_sound": "osa_shoot",
        "charge_sound": "osa_charge",
        "hit_sound": "osa_hit",
        
        # Visual effects
        "muzzle_flash_size": 2,
        "muzzle_flash_count": 2,
        "hit_particle_size": 2,
        "hit_particle_count": 3,
        "charge_particle_size": 2,
        "charge_particle_rate": 3,
        
        "description": "Rapid-fire circular ship"
    },
    "Komar": {
        # Core stats
        "health": 5,
        "bullets": 4,
        "shape": "kite",
        
        # Movement configuration
        "speed": 4,
        "acceleration": 0.5,
        "deceleration": 0.3,
        
        # Bullet configuration
        "bullet_shape": "line",
        "bullet_size": 4,
        "bullet_speed": 8,
        "bullet_damage": 1,
        "bullet_recharge_time": 30,
        "bullet_length": 30,  # Length of laser line
        "side_line_length": 40,  # Length of side indicator lines
        "front_line_width": 15,  # Width of front indicator line
        
        # Charge attack configuration (beam)
        "charged_bullet_speed": 6,
        "charged_beam_width": 8,
        "charged_damage_multiplier": 2,
        "charge_rate": 0.8,
        "beam_fade_time": 15,  # Frames for beam to fade
        "beam_damage_delay": 3,  # Frames between damage ticks
        
        # Sound configuration
        "shoot_sound": "komar_shoot",
        "charge_sound": "komar_charge",
        "hit_sound": "komar_hit",
        "beam_sound": "komar_beam",
        
        # Visual effects
        "muzzle_flash_size": 6,
        "muzzle_flash_count": 6,
        "hit_particle_size": 4,
        "hit_particle_count": 8,
        "charge_particle_size": 3,
        "charge_particle_rate": 6,
        "beam_particle_rate": 2,
        
        "description": "Laser-based kite ship"
    },
    "Kombuz": {
        # Core stats
        "health": 7,
        "bullets": 6,
        "shape": "hexagon",
        
        # Movement configuration
        "speed": 3,
        "acceleration": 0.4,
        "deceleration": 0.2,
        
        # Mine configuration
        "bullet_shape": "hexagon",
        "bullet_size": 8,
        "bullet_speed": 4,
        "bullet_damage": 1,
        "bullet_recharge_time": 40,
        "bullet_count": 4,  # Number of hexagonal bullets
        
        # Mine behavior
        "mine_arm_time": 90,  # Frames before mine can explode (1.5 seconds)
        "mine_pulse_rate": 8,  # Faster pulse rate
        "mine_pulse_size": 12,  # Larger pulse outline
        # Reasonable travel fraction so mines settle before crossing entire screen
        "mine_travel_distance": 0.60,  # Goes into enemy territory (fraction of screen width)
        "aim_outline_size": 16,  # Size of aiming outline
        "aim_rotation_speed": 0.1,  # Speed of outline rotation
        "mine_explosion_time": 30,  # Frames for explosion animation
        
        # Charge attack configuration (super mine)
        "charged_bullet_speed": 5,
        "charged_bullet_size": 12,
        "charged_damage_multiplier": 2,
        "charge_rate": 0.7,  # Slower charge
        "charged_mine_arm_time": 120,  # 2 seconds
        "charged_explosion_radius": 150,
        "damage_falloff": 0.5,  # Damage reduction per distance unit
        
        # Sound configuration
        "shoot_sound": "kombuz_shoot",
        "charge_sound": "kombuz_charge",
        "hit_sound": "kombuz_hit",
        "mine_arm_sound": "kombuz_mine_arm",
        "mine_explode_sound": "kombuz_mine_explode",
        
        # Visual effects
        "muzzle_flash_size": 4,
        "muzzle_flash_count": 3,
        "hit_particle_size": 3,
        "hit_particle_count": 6,
        "charge_particle_size": 3,
        "charge_particle_rate": 8,
        "explosion_particle_count": 12,
        "explosion_particle_speed": 5,
        
        "description": "Hexagonal mine-layer ship"
    },
    
    "Gwiazdka": {
        # Core stats
        "health": 6,
        "bullets": 8,
        "shape": "star",
        
        # Movement configuration
        "speed": 4,
        "acceleration": 0.6,
        "deceleration": 0.3,
        
        # Bullet configuration
        "bullet_shape": "star",
        "bullet_size": 5,
        "bullet_speed": 6,
        "bullet_damage": 0.75,
        "bullet_recharge_time": 25,
        "scatter_angle": 30,  # Degree spread for scatter shot
        
        # Charge attack configuration (nova burst)
        "charged_bullet_speed": 8,
        "charged_bullet_size": 8,
        "charged_damage_multiplier": 1.5,
        "charge_rate": 1.0,
        "nova_rays": 8,  # Number of bullets in charged nova burst
        "nova_delay": 5,  # Frames between each ray in nova sequence
        
        # Sound configuration
        "shoot_sound": "gwiazdka_shoot",
        "charge_sound": "gwiazdka_charge",
        "hit_sound": "gwiazdka_hit",
        "nova_sound": "gwiazdka_nova",
        
        # Visual effects
        "muzzle_flash_size": 4,
        "muzzle_flash_count": 5,
        "hit_particle_size": 3,
        "hit_particle_count": 5,
        "charge_particle_size": 2,
        "charge_particle_rate": 6,
        "nova_particle_count": 16,
        "nova_particle_speed": 4,
        
        "description": "Star ship with scatter shot and nova burst"
    },
    
    "Rift": {
        # Core stats
        "health": 5,
        "bullets": 8,
        "shape": "boomerang",
        
        # Movement configuration
        "speed": 4,
        "acceleration": 0.6,
        "deceleration": 0.3,
        
        # Bullet configuration
        "bullet_shape": "boomerang",
        "bullet_size": 8,
        "bullet_speed": 6,
        "bullet_damage": 1,
        "bullet_recharge_time": 25,
        
        # Charge attack configuration
        "charged_bullet_speed": 8,
        "charged_bullet_size": 12,
        "charged_damage_multiplier": 1.5,
        "charge_rate": 1.2,
        "sweep_angle": 120,  # Degrees for charged sweep attack
        
        # Sound configuration
        "shoot_sound": "rift_shoot",
        "charge_sound": "rift_charge",
        "hit_sound": "rift_hit",
        "sweep_sound": "rift_sweep",
        
        # Visual effects
        "muzzle_flash_size": 4,
        "muzzle_flash_count": 4,
        "hit_particle_size": 3,
        "hit_particle_count": 5,
        "charge_particle_size": 2,
        "charge_particle_rate": 6,
        
        "description": "Boomerang ship with returning projectiles",
        
        # Boomerang behavior
        "return_distance": 300,  # Distance before boomerang returns
        "return_speed": 4,      # Speed during return flight
        "return_damage": 1.5    # Damage multiplier when hit during return
    },
    
    "Nexus": {
        # Core stats
        "health": 6,
        "bullets": 8,  # Increased to 8 bullets
        "shape": "nexus",
        
        # Movement configuration
        "speed": 4,
        "acceleration": 0.5,
        "deceleration": 0.3,
        
        # Bullet configuration
        "bullet_shape": "diamond",  # Changed to diamond shape
        "bullet_size": 6,
        "bullet_speed": 6,
        "bullet_damage": 1,
        "bullet_recharge_time": 25,
        "dual_shot_spacing": 20,  # Spacing between dual shots
        "front_line_width": 15,  # Width of front indicator line
        
        # Charge attack configuration
        "charged_bullet_speed": 7,
        "charged_bullet_size": 10,
        "charged_damage_multiplier": 2,
        "charge_rate": 1.0,
        "cross_pattern_size": 4,  # Number of bullets in cross pattern
        "cross_pattern_spread": 30,  # Degrees between cross shots
        
        # Sound configuration
        "shoot_sound": "nexus_shoot",
        "charge_sound": "nexus_charge",
        "hit_sound": "nexus_hit",
        "cross_sound": "nexus_cross",
        
        # Visual effects
        "muzzle_flash_size": 4,
        "muzzle_flash_count": 4,
        "hit_particle_size": 3,
        "hit_particle_count": 5,
        "charge_particle_size": 2,
        "charge_particle_rate": 6,
        
        "description": "X-shaped ship with cross-pattern attacks"
    }
}

class Ship:
    def __init__(self, x, y, ship_type, color, controls, is_left):
        config = SHIPS[ship_type]
        self.x = x
        self.y = y
        self.type = ship_type
        self.color = color
        self.original_color = color
        self.controls = controls
        self.is_left = is_left
        self.width = SHIP_SIZE
        self.height = SHIP_SIZE
        self.speed = config["speed"]
        self.health = config["health"]
        self.max_health = config["health"]
        self.bullets = config["bullets"]
        self.max_bullets = config["bullets"]
        self.bullet_shape = config["bullet_shape"]
        self.shape = config["shape"]
        self.bullet_speed = config["bullet_speed"]
        self.charged_bullet_speed = config["charged_bullet_speed"]
        self.bullet_cooldown = 0
        self.bullet_recharge_time = config["bullet_recharge_time"]
        self.charging = False
        self.charge_time = 0
        self.max_charge_time = MAX_CHARGE_TIME
        self.charging_consumed = 0  # bullets consumed progressively while charging
        self.bullets_visible = []
        
        self.update_bullet_positions()
        # runtime refs
        self.game = None
        
    def update_bullet_positions(self):
        # Generalize bullet placement: place bullets symmetrically on left and right sides
        # from the ship's perspective so they appear outside the hull and do not overlap.
        self.bullets_visible = []
        if self.bullets <= 0:
            return
        # split counts so extra bullet goes to the right side for visual balance
        half = self.bullets // 2
        left_count = half
        right_count = self.bullets - half

        # compute horizontal offsets allowing per-ship override
        side_offset = getattr(self, 'bullet_side_offset', 0)
        left_x = int(self.x - (self.width // 2) - BULLET_OFFSET - side_offset)
        right_x = int(self.x + (self.width // 2) + BULLET_OFFSET + side_offset)

        # Distribute bullets evenly along the ship height, but with a minimum spacing
        def y_for(index, count):
            if count <= 0:
                return int(self.y)
            padding = max(6, int(self.height * 0.15))
            usable = max(1, self.height - padding * 2)
            step = float(usable) / (count + 1)
            return int(self.y - usable/2 + (index + 1) * step)

        for i in range(left_count):
            self.bullets_visible.append((left_x, y_for(i, left_count)))

        for i in range(right_count):
            self.bullets_visible.append((right_x, y_for(i, right_count)))
    
    def move(self, keys):
        # Movement with boundary checking
        if keys[self.controls["up"]] and self.y > 50:
            self.y -= self.speed
        if keys[self.controls["down"]] and self.y < SCREEN_HEIGHT - 50:
            self.y += self.speed
        if keys[self.controls["left"]]:
            if self.is_left and self.x > 50:
                self.x -= self.speed
            elif not self.is_left and self.x > SCREEN_WIDTH//2 + 50:
                self.x -= self.speed
        if keys[self.controls["right"]]:
            if self.is_left and self.x < SCREEN_WIDTH//2 - 50:
                self.x += self.speed
            elif not self.is_left and self.x < SCREEN_WIDTH - 50:
                self.x += self.speed
                
        self.update_bullet_positions()
        
        # Bullet recharge with cooldown (do NOT recharge while actively charging)
        if hasattr(self, 'bullet_cooldown') and self.bullet_cooldown > 0:
            self.bullet_cooldown -= 1
        elif self.bullets < self.max_bullets and not getattr(self, 'charging', False):
            self.bullets += 1
            self.update_bullet_positions()
            # reset cooldown using per-ship config
            self.bullet_cooldown = getattr(self, 'bullet_recharge_time', 20)
        # If charging, produce particles but DO NOT consume bullets while holding.
        if self.charging:
            if hasattr(self, 'game') and self.charge_time % 5 == 0:  # Every 5 frames
                charge_x = self.x + (self.width//2 if self.is_left else -self.width//2)
                self.game.particles.append(
                    Particle(charge_x, self.y, self.color,
                            lifetime=8, size=2)
                )
    
    def start_charging(self):
        if self.bullets > 0 and not self.charging:
            self.charging = True
            self.charge_time = 0
            # do not consume bullets while charging; compute on release
            play_sound('charge', self.type)  # Ship-specific charge sound
            
            # Add charging start particle effect
            if hasattr(self, 'game'):  # Need to pass game reference for particles
                config = SHIPS[self.type]
                particle_x = self.x + (self.width//2 if self.is_left else -self.width//2)
                for _ in range(config['muzzle_flash_count']):
                    self.game.particles.append(
                        Particle(particle_x, self.y, self.color, 
                               lifetime=15, size=config['charge_particle_size'])
                    )
    
    def stop_charging(self):
        if self.charging:
            self.charging = False
            # Compute bullets used based on charge_time proportion of max_charge_time
            config = SHIPS[self.type]
            max_bullets = getattr(self, 'max_bullets', self.bullets)
            charge_ratio = min(1.0, self.charge_time / float(self.max_charge_time))
            # At minimum use 1, at maximum use up to current bullets or ship's max
            bullets_used = max(1, int(round(charge_ratio * max_bullets)))
            bullets_used = min(bullets_used, self.bullets)
            # consume bullets now
            self.bullets -= bullets_used
            self.update_bullet_positions()
            return bullets_used
        return 0
    
    def update_charge(self):
        if self.charging and self.charge_time < self.max_charge_time:
            self.charge_time += 1
    
    def shoot_single(self):
        # Different ships consume a different number of bullets for a single tap
        if self.bullets <= 0:
            return 0
        if self.type == "Rekin":
            # Rekin fires 2 bullets per tap if available
            if self.bullets >= 2:
                self.bullets -= 2
                self.update_bullet_positions()
                return 2
            else:
                self.bullets -= 1
                self.update_bullet_positions()
                return 1
        else:
            self.bullets -= 1
            self.update_bullet_positions()
            return 1
    
    def take_damage(self):
        self.health -= 1
        health_ratio = self.health / self.max_health
        self.color = (
            max(0, int(self.original_color[0] * health_ratio)),
            max(0, int(self.original_color[1] * health_ratio)),
            max(0, int(self.original_color[2] * health_ratio))
        )
        return self.health <= 0
    
    def draw(self, screen):
        # Draw ship using sprite from extracted APK assets when available.
        # apply tilt visual offset if present
        tilt_offset = getattr(self, 'tilt', 0)
        if hasattr(self, 'tilt_timer') and self.tilt_timer > 0:
            # slowly decay tilt towards 0
            self.tilt_timer -= 1
            self.tilt = int(self.tilt * 0.85)
            if abs(self.tilt) < 1:
                self.tilt = 0

        y_offset = int(tilt_offset)

        # Try to get a preloaded sprite; falls back to vector drawing
        sprite = get_ship_sprite(self.type, self.color, self.width)
        if sprite:
            try:
                img = sprite
                if not self.is_left:
                    img = pygame.transform.flip(img, True, False)
                rect = img.get_rect(center=(int(self.x), int(self.y + y_offset)))
                screen.blit(img, rect)
            except Exception:
                pygame.draw.rect(screen, self.color, (self.x - self.width//2, self.y - self.height//2 + y_offset, self.width, self.height))
        else:
            # Fallback simple rectangle with outline
            pygame.draw.rect(screen, self.color, (self.x - self.width//2, self.y - self.height//2 + y_offset, self.width, self.height))
            pygame.draw.rect(screen, SHIP_OUTLINE_COLOR, (self.x - self.width//2, self.y - self.height//2 + y_offset, self.width, self.height), 2)

        # Health bar above ship
        try:
            bar_w = self.width
            bar_h = 6
            hp_ratio = max(0.0, min(1.0, float(self.health) / float(self.max_health)))
            bar_x = int(self.x - bar_w // 2)
            bar_y = int(self.y - self.height//2 - 12 + y_offset)
            pygame.draw.rect(screen, (80,80,80), (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(screen, (0,200,0), (bar_x, bar_y, int(bar_w * hp_ratio), bar_h))
            pygame.draw.rect(screen, SHIP_OUTLINE_COLOR, (bar_x, bar_y, bar_w, bar_h), 1)
        except Exception:
            pass

        # Draw bullets on sides: use bullet sprites if available
        for bullet_pos in self.bullets_visible:
            bshape = self.bullet_shape or SHIPS.get(self.type, {}).get('bullet_shape', 'circle')
            sprite = get_bullet_sprite(bshape, BULLET_SIZE, UNFIRED_BULLET_COLOR)
            bx, by = int(bullet_pos[0]), int(bullet_pos[1])
            if sprite:
                try:
                    rect = sprite.get_rect(center=(bx, by))
                    screen.blit(sprite, rect)
                except Exception:
                    pygame.draw.circle(screen, UNFIRED_BULLET_COLOR, (bx, by), BULLET_SIZE//2)
            else:
                # simple fallback
                pygame.draw.circle(screen, UNFIRED_BULLET_COLOR, (bx, by), BULLET_SIZE//2)

        # Small vertical direction indicator drawn inside the ship
        try:
            front_x = int(self.x + (self.width//3 if self.is_left else -self.width//3))
            pygame.draw.line(screen, SHIP_OUTLINE_COLOR, (front_x, int(self.y - self.height//6)), (front_x, int(self.y + self.height//6)), 2)
        except Exception:
            pass


class Bullet:
    def __init__(self, x, y, direction, ship_type, is_charged=False, charge_level=1):
        config = SHIPS[ship_type]
        self.x = x
        self.y = y
        self.direction = direction
        self.ship_type = ship_type
        self.color = None
        self.is_charged = is_charged
        self.charge_level = charge_level
        base_speed = config["charged_bullet_speed"] if is_charged else config["bullet_speed"]
        self.speed = base_speed * GLOBAL_BULLET_SPEED_MULT
        self.timer = 0
        
        # Set size based on charge level
        # Size scaling: charged bullets grow but capped to avoid massive bullets
        base_size = BULLET_SIZE * 2
        if is_charged:
            extra = (charge_level - 1)
            self.width = base_size + extra * BULLET_SIZE
            self.height = base_size + extra * BULLET_SIZE
            if ship_type == "Komar":
                # Komar beam is tall but cap it
                self.height = min(200, base_size + extra * BULLET_SIZE * 4)
        else:
            self.width = base_size
            self.height = base_size
            if ship_type == "Komar":
                self.height = 30
        
        if ship_type == "Kombuz":
            self.exploding = False
            self.explosion_timer = 0
        # for mines: whether it has settled (stops moving) in enemy area
        self.settled = False
        # flag to ensure explosion damage is applied once
        self.explosion_applied = False
    
    def move(self):
        # Komar charged laser is instant beam - it doesn't move like normal bullet
        if self.ship_type == "Komar" and self.is_charged:
            # keep position static; laser effective instantly
            pass
        
        elif self.ship_type == "Rift":
            # Track distance traveled for boomerang return
            if not hasattr(self, 'distance_traveled'):
                self.distance_traveled = 0
                self.base_damage = self.damage if hasattr(self, 'damage') else 1
                self.is_returning = False
            
            # Check if bullet should return
            if not self.is_returning and self.distance_traveled > SHIPS["Rift"]["return_distance"]:
                self.is_returning = True
                self.direction = -self.direction  # Reverse direction
                self.damage = self.base_damage * SHIPS["Rift"]["return_damage"]
                # Visual effect for return
                if hasattr(self, 'game'):
                    # Create return flash effect
                    for _ in range(4):
                        self.game.particles.append(
                            Particle(self.x, self.y, self.color,
                                   lifetime=10, size=4)
                        )
        elif self.ship_type == "Rift" and self.is_charged:
            # Charged bullets move in an arc pattern
            if hasattr(self, 'angle'):
                # Arc shots don't return
                base_move = self.direction * self.speed
                self.x += base_move * math.cos(self.angle)
                self.y += base_move * math.sin(self.angle)
            else:
                # Move boomerang with return behavior
                if not self.is_returning:
                    self.x += self.direction * self.speed
                else:
                    self.x += self.direction * SHIPS["Rift"]["return_speed"]
                self.distance_traveled += abs(self.speed)
        elif self.ship_type == "Gwiazdka" and (getattr(self, 'nova', False) or getattr(self, 'scatter', False)):
            # Handle nova burst and scatter shot movement
            base_move = self.direction * self.speed
            if hasattr(self, 'angle'):
                # Add angular component to movement
                self.x += base_move * math.cos(self.angle)
                self.y += base_move * math.sin(self.angle)
            else:
                self.x += base_move
                
        elif self.ship_type == "Rift" and not self.is_charged:
            # Regular Rift shots use boomerang behavior
            if not self.is_returning:
                self.x += self.direction * self.speed
                self.distance_traveled += abs(self.speed)
            else:
                self.x += self.direction * SHIPS["Rift"]["return_speed"]
        else:
            if not getattr(self, 'settled', False):
                self.x += self.direction * self.speed
        self.timer += 1
        
        # Handle Kombuz mine explosion
        if self.ship_type == "Kombuz":
            explosion_time = CHARGED_MINE_EXPLOSION_TIME if self.is_charged else MINE_EXPLOSION_TIME
            if self.timer > explosion_time:
                self.exploding = True
                self.explosion_timer += 1
            
            if self.exploding and self.explosion_timer > FPS//2:
                return True
        
            # Kombuz mines settle when reaching desired distance into enemy territory
            if self.ship_type == "Kombuz" and not self.settled:
                config = SHIPS["Kombuz"]
                target_distance = SCREEN_WIDTH * config["mine_travel_distance"]
                
                if self.direction == 1:  # Moving right
                    settle_x = target_distance
                    if self.x > settle_x:
                        self.settled = True
                        self.speed = 0
                        play_sound('mine_arm', 'Kombuz')  # Play arming sound
                else:  # Moving left
                    settle_x = SCREEN_WIDTH * (1 - config["mine_travel_distance"])
                    if self.x < settle_x:
                        self.settled = True
                        self.speed = 0
                        play_sound('mine_arm', 'Kombuz')  # Play arming sound        if self.x < -200 or self.x > SCREEN_WIDTH + 200:
            return True
        
        return False

    def draw(self, screen):
        # Try to draw a bullet sprite if available; otherwise fallback to vector shapes per ship type.
        bcolor = self.color or BULLET_COLOR
        bshape = SHIPS.get(self.ship_type, {}).get('bullet_shape', 'circle')
        sprite = get_bullet_sprite(bshape, max(4, int(max(self.width, self.height))), bcolor)
        if sprite:
            try:
                angle_deg = -math.degrees(getattr(self, 'angle', 0)) if hasattr(self, 'angle') else 0
                img = pygame.transform.rotate(sprite, angle_deg)
                rect = img.get_rect(center=(int(self.x), int(self.y)))
                screen.blit(img, rect)
                return
            except Exception:
                pass

        # Fallback vector drawing
        if self.ship_type == "Zaba":
            pygame.draw.rect(screen, bcolor, (self.x - self.width//2, self.y - self.height//2, self.width, self.height))
        elif self.ship_type == "Rift":
            # Draw fired boomerang bullet
            width = self.width * 1.5
            height = self.height
            points = []
            if self.direction == 1:
                points.append((self.x + width//2, self.y))
                points.append((self.x, self.y - height//2))
                points.append((self.x - width//2, self.y))
                points.append((self.x, self.y + height//2))
            else:
                points.append((self.x - width//2, self.y))
                points.append((self.x, self.y - height//2))
                points.append((self.x + width//2, self.y))
                points.append((self.x, self.y + height//2))
            pygame.draw.polygon(screen, bcolor, points)
        elif self.ship_type == "Rekin":
            if self.direction == 1:
                points = [
                    (self.x + self.width//2, self.y),
                    (self.x - self.width//2, self.y - self.height//2),
                    (self.x - self.width//2, self.y + self.height//2)
                ]
            else:
                points = [
                    (self.x - self.width//2, self.y),
                    (self.x + self.width//2, self.y - self.height//2),
                    (self.x + self.width//2, self.y + self.height//2)
                ]
            pygame.draw.polygon(screen, bcolor, points)
        
        elif self.ship_type == "Osa":
            pygame.draw.circle(screen, self.color or BULLET_COLOR, (int(self.x), int(self.y)), self.width//2)
        
        elif self.ship_type == "Komar":
            if self.is_charged:
                # Draw full-screen beam from origin to edge
                beam_width = max(8, self.width)
                beam_alpha = max(0, 255 - (self.timer * 4))  # Fade out
                
                # Create temporary surface for alpha
                beam_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                base_color = self.color or BULLET_COLOR
                beam_color = (base_color[0], base_color[1], base_color[2], beam_alpha)
                
                if self.direction == 1:  # Right-facing beam
                    pygame.draw.rect(beam_surface, beam_color, 
                                   (self.x, 0, SCREEN_WIDTH - self.x, SCREEN_HEIGHT))
                else:  # Left-facing beam
                    pygame.draw.rect(beam_surface, beam_color, 
                                   (0, 0, self.x, SCREEN_HEIGHT))
                
                # Draw crisp center line
                center_x = self.x
                line_color = (base_color[0], base_color[1], base_color[2], beam_alpha)
                pygame.draw.line(beam_surface, line_color,
                               (center_x, 0), (center_x, SCREEN_HEIGHT), 2)
                
                screen.blit(beam_surface, (0, 0))
            else:
                # Normal shots are vertical lines
                pygame.draw.line(screen, self.color or BULLET_COLOR, 
                               (self.x, self.y - self.height//2),
                               (self.x, self.y + self.height//2), 4)
        
        elif self.ship_type == "Kombuz":
            points = []
            for i in range(6):
                angle = 2 * math.pi * i / 6
                points.append((
                    self.x + math.cos(angle) * self.width//2,
                    self.y + math.sin(angle) * self.height//2
                ))
            pygame.draw.polygon(screen, self.color or BULLET_COLOR, points)
            
            # Pulsing hexagonal outline before explosion
            if self.timer > (CHARGED_MINE_EXPLOSION_TIME if self.is_charged else MINE_EXPLOSION_TIME) - 30:
                pulse = abs(math.sin(self.timer * 0.2)) * 10 + 5  # Faster pulse
                pulse_points = []
                for i in range(6):
                    angle = 2 * math.pi * i / 6
                    pulse_points.append((
                        self.x + math.cos(angle) * (self.width//2 + pulse),
                        self.y + math.sin(angle) * (self.width//2 + pulse)
                    ))
                pygame.draw.polygon(screen, self.color or BULLET_COLOR, pulse_points, 2)
            
            # Explosion visualization
            if self.exploding:
                explosion_radius = self.explosion_timer * 4  # Larger radius
                # Draw multiple hexagonal rings
                for ring in range(3):
                    ring_points = []
                    ring_radius = explosion_radius * (1 - ring * 0.2)  # Decreasing sizes
                    for i in range(6):
                        angle = 2 * math.pi * i / 6 + (self.explosion_timer * 0.1)  # Rotating
                        ring_points.append((
                            self.x + math.cos(angle) * ring_radius,
                            self.y + math.sin(angle) * ring_radius
                        ))
                    alpha = max(0, 255 - self.explosion_timer * 8)  # Fade out
                    explosion_color = self.color or BULLET_COLOR
                    pygame.draw.polygon(screen, (*explosion_color, alpha), ring_points, 2)


class Particle:
    def __init__(self, x, y, color, lifetime=20, size=6):
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = lifetime
        self.age = 0
        self.size = size

    def update(self):
        self.age += 1
        return self.age >= self.lifetime

    def draw(self, screen):
        alpha = max(0, 255 - int(255 * (self.age / self.lifetime)))
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        s.fill((*self.color, alpha))
        screen.blit(s, (int(self.x - self.size//2), int(self.y - self.size//2)))
        

class TouchController:
    """Simple on-screen joystick + fire button for touch input (mouse-friendly)."""
    def __init__(self, x, y, radius=60, fire_x=None, fire_y=None, fire_radius=36):
        self.cx = x
        self.cy = y
        self.radius = radius
        self.knob_x = x
        self.knob_y = y
        self.active = False
        self.dx = 0.0
        self.dy = 0.0
        # fire button
        self.fire_x = fire_x if fire_x is not None else x + 160
        self.fire_y = fire_y if fire_y is not None else y
        self.fire_radius = fire_radius
        self.fire_pressed = False

    def draw(self, screen):
        # base circle
        pygame.draw.circle(screen, (40,40,40), (self.cx, self.cy), self.radius)
        pygame.draw.circle(screen, (120,120,120), (self.cx, self.cy), self.radius, 3)
        # knob
        pygame.draw.circle(screen, (200,200,200), (int(self.knob_x), int(self.knob_y)), int(self.radius*0.45))
        # fire button
        fcol = (200,60,60) if self.fire_pressed else (120,30,30)
        pygame.draw.circle(screen, fcol, (self.fire_x, self.fire_y), self.fire_radius)
        pygame.draw.circle(screen, (255,160,160), (self.fire_x, self.fire_y), int(self.fire_radius*0.6))

    def start(self, x, y):
        # if touch inside joystick
        if math.hypot(x - self.cx, y - self.cy) <= self.radius:
            self.active = True
            self.update(x, y)
            return 'joystick'
        if math.hypot(x - self.fire_x, y - self.fire_y) <= self.fire_radius:
            self.fire_pressed = True
            return 'fire'
        return None

    def update(self, x, y):
        if not self.active:
            return
        ox = x - self.cx
        oy = y - self.cy
        dist = math.hypot(ox, oy)
        if dist > self.radius:
            ox = ox / dist * self.radius
            oy = oy / dist * self.radius
        self.knob_x = self.cx + ox
        self.knob_y = self.cy + oy
        # normalized -1..1
        self.dx = ox / float(self.radius)
        self.dy = oy / float(self.radius)

    def stop(self):
        self.active = False
        self.knob_x = self.cx
        self.knob_y = self.cy
        self.dx = 0.0
        self.dy = 0.0
        self.fire_pressed = False


# ----------------- Networking (basic LAN host/client) -----------------
class NetworkHost(threading.Thread):
    def __init__(self, game, port=50007):
        super().__init__(daemon=True)
        self.game = game
        self.port = port
        self.sock = None
        self.client = None
        self.running = True
        self.start()

    def run(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(('0.0.0.0', self.port))
            self.sock.listen(1)
            self.sock.settimeout(1.0)
            while self.running:
                try:
                    if not self.client:
                        client, addr = self.sock.accept()
                        self.client = client
                        self.client.settimeout(0.5)
                except socket.timeout:
                    pass

                # Receive client inputs
                if self.client:
                    try:
                        data = self.client.recv(4096)
                        if data:
                            try:
                                for line in data.split(b"\n"):
                                    if not line.strip():
                                        continue
                                    msg = json.loads(line.decode('utf-8'))
                                    # store last client input
                                    self.game.client_remote_input = msg.get('input')
                            except Exception:
                                pass
                    except socket.timeout:
                        pass
                    except Exception:
                        try:
                            self.client.close()
                        except Exception:
                            pass
                        self.client = None

                # Periodically send authoritative state to client
                if self.client:
                    try:
                        state = self.game.snapshot_state()
                        payload = (json.dumps({'type':'state','state':state}) + "\n").encode('utf-8')
                        self.client.sendall(payload)
                    except Exception:
                        try:
                            self.client.close()
                        except Exception:
                            pass
                        self.client = None

                time.sleep(0.05)
        finally:
            try:
                if self.client:
                    self.client.close()
                if self.sock:
                    self.sock.close()
            except Exception:
                pass

    def stop(self):
        self.running = False


class NetworkClient(threading.Thread):
    def __init__(self, game, host_ip, port=50007):
        super().__init__(daemon=True)
        self.game = game
        self.host_ip = host_ip
        self.port = port
        self.sock = None
        self.running = True
        self.last_recv = b""
        self.connected = False
        self.connecting = False
        self.should_reconnect = True
        self.reconnect_delay = 1.0
        self.reconnect_max = 8.0
        self.last_error = None
        self.start()

    def run(self):
        try:
            # Main client loop: attempt to connect and, on failure, retry with exponential backoff
            while self.running and self.should_reconnect:
                try:
                    self.connecting = True
                    self.last_error = None
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.sock.settimeout(5.0)
                    self.sock.connect((self.host_ip, self.port))
                    self.sock.settimeout(0.5)
                    self.connected = True
                    self.connecting = False
                    self.reconnect_delay = 1.0
                    # notify game
                    try:
                        self.game.connect_error = None
                        self.game.connect_status = 'connected'
                    except Exception:
                        pass

                    while self.running and self.connected:
                        # Send local input if available
                        try:
                            inp = getattr(self.game, 'client_local_input', None)
                            if inp is not None:
                                payload = (json.dumps({'type':'input','input':inp}) + "\n").encode('utf-8')
                                try:
                                    self.sock.sendall(payload)
                                except Exception:
                                    # broken pipe -> mark disconnected and break to reconnect
                                    self.connected = False
                                    break
                        except Exception:
                            pass

                        # Receive authoritative state
                        try:
                            data = self.sock.recv(8192)
                            if data:
                                self.last_recv += data
                                while b"\n" in self.last_recv:
                                    line, self.last_recv = self.last_recv.split(b"\n",1)
                                    if not line.strip():
                                        continue
                                    try:
                                        msg = json.loads(line.decode('utf-8'))
                                        if msg.get('type') == 'state':
                                            # store as target for interpolation
                                            try:
                                                self.game.remote_state_target = msg.get('state')
                                                self.game.remote_state_time = time.time()
                                            except Exception:
                                                self.game.remote_state = msg.get('state')
                                    except Exception:
                                        pass
                        except socket.timeout:
                            pass
                        except Exception as e:
                            # Connection lost; break to reconnect
                            self.last_error = str(e)
                            self.connected = False
                            break

                        time.sleep(0.05)

                except Exception as e:
                    # Connection attempt failed
                    self.last_error = str(e)
                    try:
                        self.game.connect_error = f"Connect failed: {self.last_error}"
                        self.game.connect_status = 'disconnected'
                    except Exception:
                        pass
                    # exponential backoff before retry
                    time.sleep(self.reconnect_delay)
                    self.reconnect_delay = min(self.reconnect_delay * 2.0, self.reconnect_max)
                finally:
                    try:
                        if self.sock:
                            self.sock.close()
                    except Exception:
                        pass
                    self.connected = False
                    self.connecting = False
                    # short pause before next attempt if still running
                    time.sleep(0.2)
        finally:
            try:
                if self.sock:
                    self.sock.close()
            except Exception:
                pass

    def stop(self):
        self.should_reconnect = False
        self.running = False
        try:
            if self.sock:
                self.sock.close()
        except Exception:
            pass

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("2D-Flox")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        
        # Game state
        self.state = "menu"  # menu, playing, game_over, help
        
        # Settings
        self.settings = DEFAULT_SETTINGS.copy()
        self.settings_open = False
        self.remapping_key = None  # Tracks which key is being remapped
        self.apply_volume_settings()
        # Preload background music if available
        bg_path = SOUND_PATHS.get('background')
        if bg_path and os.path.exists(bg_path):
            try:
                pygame.mixer.music.load(bg_path)
            except Exception:
                pass
        
        # Player information
        self.player1_name = "Player 1"
        self.player2_name = "Player 2"
        self.player1_ship = "Zaba"
        self.player2_ship = "Zaba"
        self.player1_color = SHIP_COLORS[0]
        self.player2_color = SHIP_COLORS[1]
        self.player1_color_index = 0
        self.player2_color_index = 1
        
        # Ship selection
        self.ship_names = list(SHIPS.keys())
        self.player1_ship_index = 0
        # Default player2 to a different ship so Nexus and others appear in menu
        self.player2_ship_index = 1 if len(self.ship_names) > 1 else 0
        # Ensure selected ship names reflect indices
        self.player1_ship = self.ship_names[self.player1_ship_index]
        self.player2_ship = self.ship_names[self.player2_ship_index]
        
        # Input handling defaults
        self.input_active = "player1"  # which menu field is active
        self.fullscreen = False
        
        # Game objects
        self.ship1 = None
        self.ship2 = None
        self.bullets = []
        self.particles = []
        self.winner = None
        # interactive state
        self.dragging_volume = None  # 'music' | 'sfx' | None
        # tap-vs-hold threshold (frames) to distinguish single tap vs charged shot
        self.tap_threshold = 6
        # Networking state
        self.network_role = None  # None | 'host' | 'client'
        self.network_peer = None
        self.remote_state = None
        # For smoother client rendering we interpolate towards the authoritative target
        self.remote_state_target = None
        self.remote_state_interp = None
        self.remote_state_time = 0.0
        self.interp_alpha = 0.22  # smoothing factor (0 - no interp, 1 - snap)
        self.client_remote_input = None
        self.client_local_input = None
        # Menu connect IP buffer
        self.connect_ip = ""
        # Connection UI/status
        self.connect_status = None
        self.connect_error = None
        # menu clickable regions (populated by draw_menu)
        self.menu_regions = {}
        # Input mode: 'keyboard' or 'touch'
        self.input_mode = 'keyboard'
        # Touch controllers will be created when needed (placed relative to screen)
        self.touch_left = None
        self.touch_right = None
        # Previous fire states for touch controllers to detect press/release
        self.touch_left_prev_fire = False
        self.touch_right_prev_fire = False
        
    def apply_volume_settings(self):
        """Apply volume settings to pygame mixer"""
        pygame.mixer.music.set_volume(self.settings["music_volume"])
        # Apply to sound effects
        for sound in SOUNDS.values():
            if sound:
                sound.set_volume(self.settings["sfx_volume"])
                
    def draw_settings_icon(self):
        """Draw gear icon in top left corner"""
        center = (30, 30)
        radius = 15
        pygame.draw.circle(self.screen, SETTINGS_TEXT_COLOR, center, radius, 2)
        # Draw gear teeth
        for i in range(8):
            angle = i * math.pi / 4
            x = center[0] + math.cos(angle) * radius
            y = center[1] + math.sin(angle) * radius
            pygame.draw.line(self.screen, SETTINGS_TEXT_COLOR,
                           (x, y),
                           (x + math.cos(angle) * 5, y + math.sin(angle) * 5),
                           2)
                           
    def draw_volume_bar(self, x, y, width, height, value, label):
        """Draw a volume control bar with label and percentage"""
        # Draw label
        text = self.small_font.render(label, True, SETTINGS_TEXT_COLOR)
        self.screen.blit(text, (x, y - 20))
        
        # Draw bar background with border
        pygame.draw.rect(self.screen, SETTINGS_BAR_BG, (x, y, width, height))
        pygame.draw.rect(self.screen, SETTINGS_TEXT_COLOR, (x, y, width, height), 1)
        
        # Draw filled portion
        if value > 0:
            pygame.draw.rect(self.screen, SETTINGS_BAR_FG, 
                           (x, y, width * value, height))
        
        # Draw percentage
        percentage = f"{int(value * 100)}%"
        percent_text = self.small_font.render(percentage, True, SETTINGS_TEXT_COLOR)
        self.screen.blit(percent_text, (x + width + 10, y - 3))
        
    def handle_settings_click(self, pos):
        """Handle clicks in settings menu"""
        x, y = pos
        if not self.settings_open:
            # Check if settings icon clicked
            if (x - 30)**2 + (y - 30)**2 <= 15**2:
                self.settings_open = True
                return True
        else:
            # Handle volume bar clicks (compute positions to match draw_settings_menu)
            panel_width = 700
            panel_height = 520
            panel_x = SCREEN_WIDTH//2 - panel_width//2
            panel_y = 40
            title_y = panel_y + 20
            volume_y = title_y + 70
            bar_width = 400
            bar_height = 15
            bar_x = panel_x + (panel_width - bar_width) // 2
            music_y = volume_y + 50
            sfx_y = music_y + 60

            music_bar = pygame.Rect(bar_x, music_y, bar_width, bar_height)
            sfx_bar = pygame.Rect(bar_x, sfx_y, bar_width, bar_height)

            if music_bar.collidepoint(pos):
                self.settings["music_volume"] = max(0.0, min(1.0, (x - music_bar.x) / music_bar.width))
                self.apply_volume_settings()
                self.dragging_volume = 'music'
                return True

            if sfx_bar.collidepoint(pos):
                self.settings["sfx_volume"] = max(0.0, min(1.0, (x - sfx_bar.x) / sfx_bar.width))
                self.apply_volume_settings()
                self.dragging_volume = 'sfx'
                return True
                
            # Check reset button
            reset_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 500, 200, 40)
            if reset_rect.collidepoint(pos):
                self.settings = DEFAULT_SETTINGS.copy()
                self.apply_volume_settings()
                return True
                
            # Check for key remap buttons
            key_areas = self.get_key_remap_areas()
            for key, rect in key_areas.items():
                if rect.collidepoint(pos):
                    self.remapping_key = key
                    return True
            # Close button area (top-right of panel)
            panel_x = SCREEN_WIDTH//2 - 350
            panel_width = 700
            panel_y = 40
            close_rect = pygame.Rect(panel_x + panel_width - 34, panel_y + 6, 28, 28)
            if close_rect.collidepoint(pos):
                self.settings_open = False
                self.dragging_volume = None
                return True

            return False

    def handle_menu_click(self, pos):
        # keep legacy behavior but also handle host/join areas
        x, y = pos
        # check host/join special areas first
        if hasattr(self, 'menu_regions') and self.menu_regions:
            if 'host' in self.menu_regions and self.menu_regions['host'].collidepoint(pos):
                # start hosting
                try:
                    self.start_host()
                    self.connect_error = None
                    self.settings_open = False
                except Exception:
                    pass
                return
            if 'join' in self.menu_regions and self.menu_regions['join'].collidepoint(pos):
                # If IP already entered, try to connect; otherwise focus entry
                if self.connect_ip:
                    try:
                        self.connect_to(self.connect_ip)
                        self.connect_error = None
                    except Exception as e:
                        self.connect_error = f"Connect failed: {str(e) or 'error'}"
                else:
                    self.input_active = 'connect_ip'
                return
            if 'ip_field' in self.menu_regions and self.menu_regions['ip_field'].collidepoint(pos):
                self.input_active = 'connect_ip'
                return
            # Start / Info / Stop buttons
            if 'start' in self.menu_regions and self.menu_regions['start'].collidepoint(pos):
                try:
                    self.start_game()
                except Exception:
                    pass
                return
            if 'info' in self.menu_regions and self.menu_regions['info'].collidepoint(pos):
                self.state = 'help'
                return
            if 'stop' in self.menu_regions and self.menu_regions['stop'].collidepoint(pos):
                # Stop hosting or disconnect client
                try:
                    self.stop_network()
                    self.connect_error = None
                except Exception as e:
                    self.connect_error = f"Stop failed: {str(e)}"
                return

        # Fallback to existing simple click areas
        # Player 1 area (left side)
        if x < SCREEN_WIDTH // 2:
            # Name field
            if 150 <= y <= 180:
                self.input_active = "player1"
            # Ship selection
            elif 220 <= y <= 250:
                self.input_active = "ship1"
            # Color selection
            elif 290 <= y <= 320:
                self.input_active = "color1"

        # Player 2 area (right side)
        else:
            # Name field
            if 150 <= y <= 180:
                self.input_active = "player2"
            # Ship selection
            elif 220 <= y <= 250:
                self.input_active = "ship2"
            # Color selection
            elif 290 <= y <= 320:
                self.input_active = "color2"

        # Start button
        if 450 <= y <= 490 and SCREEN_WIDTH//2 - 100 <= x <= SCREEN_WIDTH//2 + 100:
            self.start_game()
        
        # Help button
        if 520 <= y <= 560 and SCREEN_WIDTH//2 - 100 <= x <= SCREEN_WIDTH//2 + 100:
            self.state = "help"
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            # Mouse handling: unified branch for clicking/dragging
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # If settings overlay open, let it handle clicks first
                    if self.settings_open:
                        if self.handle_settings_click(event.pos):
                            continue
                    # Otherwise, if we're in menu, handle menu clicks
                    if self.state == 'menu':
                        self.handle_menu_click(event.pos)
                        continue
                    # In-game: allow clicks for future UI (none currently)

            elif event.type == MOUSEBUTTONUP:
                # stop dragging volume when mouse released
                if event.button == 1:
                    self.dragging_volume = None
                    # No touch-release handling: mouse releases are ignored for gameplay (keyboard-only controls)

            elif event.type == MOUSEMOTION:
                # If dragging a volume slider, update value dynamically
                if self.settings_open and self.dragging_volume:
                    mx, my = event.pos
                    panel_width = 700
                    panel_x = SCREEN_WIDTH//2 - panel_width//2
                    bar_width = 400
                    bar_x = panel_x + (panel_width - bar_width) // 2
                    # compute y positions consistent with draw_settings_menu
                    panel_y = 40
                    title_y = panel_y + 20
                    volume_y = title_y + 70
                    music_y = volume_y + 50
                    sfx_y = music_y + 60
                    if self.dragging_volume == 'music':
                        rel = (mx - bar_x) / bar_width
                        self.settings['music_volume'] = max(0.0, min(1.0, rel))
                        self.apply_volume_settings()
                    elif self.dragging_volume == 'sfx':
                        rel = (mx - bar_x) / bar_width
                        self.settings['sfx_volume'] = max(0.0, min(1.0, rel))
                        self.apply_volume_settings()
                # Mouse motion currently only used for UI dragging (volume sliders)

            elif event.type == KEYDOWN:
                # Handle key remapping
                if self.remapping_key:
                    self.settings[self.remapping_key] = event.key
                    self.remapping_key = None
                    continue
                if self.state == "menu":
                    # Use keyboard in menu for text input/backspace only; mouse handles selection
                    if event.key == K_BACKSPACE:
                        if self.input_active == "player1":
                            self.player1_name = self.player1_name[:-1]
                        elif self.input_active == "player2":
                            self.player2_name = self.player2_name[:-1]
                        elif self.input_active == 'connect_ip':
                            self.connect_ip = self.connect_ip[:-1]
                    else:
                        if event.unicode and event.unicode.isprintable():
                            if self.input_active == "player1" and len(self.player1_name) < 24:
                                self.player1_name += event.unicode
                            elif self.input_active == "player2" and len(self.player2_name) < 24:
                                self.player2_name += event.unicode
                            elif self.input_active == 'connect_ip' and len(self.connect_ip) < 64:
                                self.connect_ip += event.unicode
                            # If user pressed Enter while entering IP, try to connect
                            if event.key == K_RETURN and self.input_active == 'connect_ip':
                                try:
                                    self.connect_to(self.connect_ip)
                                    self.input_active = None
                                except Exception:
                                    pass
                    # Input mode toggle removed: game is keyboard-only for ship controls

                elif self.state == "playing":
                    if event.key == K_f:
                        self.toggle_fullscreen()
                    elif event.key == K_ESCAPE:
                        self.state = "menu"

                    # Start charging on keydown (we'll decide tap vs hold on keyup)
                    if event.key == K_SPACE and self.ship1:
                        if not self.ship1.charging:
                            self.ship1.start_charging()
                            # ensure ship has reference to game
                            self.ship1.game = self
                    if event.key == K_RETURN and self.ship2:
                        if not self.ship2.charging:
                            self.ship2.start_charging()
                            self.ship2.game = self

                elif self.state == "game_over" or self.state == "help":
                    if event.key == K_RETURN or event.key == K_ESCAPE:
                        self.state = "menu"
                    elif event.key == K_f:
                        self.toggle_fullscreen()
            
            elif event.type == KEYUP:
                if self.state == "playing":
                    # Player1
                    if event.key == K_SPACE and self.ship1 and self.ship1.charging:
                        # decide tap vs hold
                        if self.ship1.charge_time < self.tap_threshold:
                            # tap: single shot if available
                            bullets_used = self.ship1.shoot_single()
                            if bullets_used > 0:
                                self.shoot_bullet(self.ship1, bullets_used, False)
                        else:
                            bullets_used = self.ship1.stop_charging()
                            if bullets_used > 0:
                                self.shoot_bullet(self.ship1, bullets_used, True)

                    # Player2
                    if event.key == K_RETURN and self.ship2 and self.ship2.charging:
                        if self.ship2.charge_time < self.tap_threshold:
                            bullets_used = self.ship2.shoot_single()
                            if bullets_used > 0:
                                self.shoot_bullet(self.ship2, bullets_used, False)
                        else:
                            bullets_used = self.ship2.stop_charging()
                            if bullets_used > 0:
                                self.shoot_bullet(self.ship2, bullets_used, True)

            elif event.type == MOUSEBUTTONDOWN:
                if self.state == "menu":
                    self.handle_menu_click(event.pos)
    
    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    def start_game(self):
        self.ship1 = Ship(100, SCREEN_HEIGHT//2, self.player1_ship, self.player1_color, 
                         {"up": K_w, "down": K_s, "left": K_a, "right": K_d, "fire": K_SPACE}, True)
        self.ship2 = Ship(SCREEN_WIDTH - 100, SCREEN_HEIGHT//2, self.player2_ship, self.player2_color, 
                         {"up": K_UP, "down": K_DOWN, "left": K_LEFT, "right": K_RIGHT, "fire": K_RETURN}, False)
        
        self.bullets = []
        self.winner = None
        self.state = "playing"
        
        # Start theme music when game starts
        try:
            pygame.mixer.music.play(-1)  # -1 means loop indefinitely
        except Exception:
            pass

        # give ships a back-reference to the game for particles/effects
        self.ship1.game = self
        self.ship2.game = self

    # Networking helpers
    def snapshot_state(self):
        """Return a minimal serializable snapshot of current game state."""
        try:
            state = {
                'ship1': {'x': self.ship1.x, 'y': self.ship1.y, 'health': self.ship1.health, 'bullets': self.ship1.bullets, 'type': self.ship1.type},
                'ship2': {'x': self.ship2.x, 'y': self.ship2.y, 'health': self.ship2.health, 'bullets': self.ship2.bullets, 'type': self.ship2.type},
                'bullets': [ {'x': b.x, 'y': b.y, 'w': b.width, 'h': b.height, 'ship_type': b.ship_type, 'is_charged': b.is_charged} for b in self.bullets ],
            }
            return state
        except Exception:
            return {}

    def start_host(self, port=50007):
        if self.network_peer:
            try:
                self.network_peer.stop()
            except Exception:
                pass
        self.network_peer = NetworkHost(self, port)
        self.network_role = 'host'

    def connect_to(self, host_ip, port=50007):
        if self.network_peer:
            try:
                self.network_peer.stop()
            except Exception:
                pass
        self.network_peer = NetworkClient(self, host_ip, port)
        self.network_role = 'client'

    def stop_network(self):
        if self.network_peer:
            try:
                self.network_peer.stop()
            except Exception:
                pass
        self.network_peer = None
        self.network_role = None

    def add_bullet(self, b):
        """Helper to append a bullet and assign game reference for in-bullet effects."""
        self.bullets.append(b)
        try:
            b.game = self
        except Exception:
            pass
    
    def shoot_bullet(self, ship, bullets_used, is_charged):
        # Play ship-specific shoot sound
        play_sound('shoot', ship.type)
        # per-ship configuration for spawn offsets
        config = SHIPS.get(ship.type, {})
        spawn_forward = config.get('spawn_forward', 15)
        
        if ship.type == "Zaba":
            if is_charged:
                direction = 1 if ship.is_left else -1
                bullet_x = ship.x + (ship.width//2 + spawn_forward) * direction
                b = Bullet(bullet_x, ship.y, direction, ship.type, True, bullets_used)
                b.color = ship.color
                self.add_bullet(b)
                # small particle effect
                for _ in range(6):
                    self.particles.append(Particle(bullet_x, ship.y, ship.color, lifetime=20, size=4))
            else:
                direction = 1 if ship.is_left else -1
                bullet_x = ship.x + (ship.width//2 + spawn_forward) * direction
                b = Bullet(bullet_x, ship.y, direction, ship.type)
                b.color = ship.color
                self.add_bullet(b)
        
        elif ship.type == "Rekin":
            direction = 1 if ship.is_left else -1
            tip_x = ship.x + (ship.width//2) * direction  # ship's tip position
            
            if is_charged:
                # Charged shot: 3 bullets in spread pattern from tip
                spread = 12  # vertical spacing between bullets
                for i in range(min(3, bullets_used)):
                    bullet_x = tip_x + spawn_forward * direction  # slightly in front of tip
                    bullet_y = ship.y + (i-1) * spread  # one above, one center, one below
                    b = Bullet(bullet_x, bullet_y, direction, ship.type, True, bullets_used)
                    b.color = ship.color
                    self.add_bullet(b)
                    # particles for each bullet
                    for _ in range(4):
                        self.particles.append(Particle(bullet_x, bullet_y, ship.color, lifetime=15, size=3))
            else:
                # Single tap: two side-by-side bullets
                offset = 8  # vertical offset for symmetric placement
                bullet_x = tip_x + spawn_forward * direction  # slightly in front of tip
                # Create two bullets symmetrically above/below centerline
                b1 = Bullet(bullet_x, ship.y - offset, direction, ship.type)
                b1.color = ship.color
                b2 = Bullet(bullet_x, ship.y + offset, direction, ship.type)
                b2.color = ship.color
                self.add_bullet(b1)
                self.add_bullet(b2)
                # small particle effect at spawn points
                self.particles.append(Particle(bullet_x, ship.y - offset, ship.color, lifetime=10, size=2))
                self.particles.append(Particle(bullet_x, ship.y + offset, ship.color, lifetime=10, size=2))
        
        elif ship.type == "Osa":
            if is_charged:
                # Cap the number of spawned bullets for charged shot to avoid clustering
                max_spawn = 7
                count = min(bullets_used, max_spawn)
                spacing = 8
                for i in range(count):
                    direction = 1 if ship.is_left else -1
                    bullet_x = ship.x + (ship.width//2 + spawn_forward) * direction
                    # Symmetrical offsets around ship center
                    offset = (i - (count - 1) / 2.0) * spacing
                    b = Bullet(bullet_x, ship.y + offset, direction, ship.type, True, bullets_used)
                    b.color = ship.color
                    self.add_bullet(b)
                    for _ in range(2):
                        self.particles.append(Particle(bullet_x, ship.y + offset, ship.color, lifetime=10, size=2))
            else:
                direction = 1 if ship.is_left else -1
                bullet_x = ship.x + (ship.width//2 + spawn_forward) * direction
                b = Bullet(bullet_x, ship.y, direction, ship.type)
                b.color = ship.color
                self.add_bullet(b)
        
        elif ship.type == "Komar":
            if is_charged:
                direction = 1 if ship.is_left else -1
                bullet_x = ship.x + (ship.width//2 + spawn_forward) * direction
                b = Bullet(bullet_x, ship.y, direction, ship.type, True, bullets_used)
                b.color = ship.color
                self.add_bullet(b)
                for _ in range(6):
                    self.particles.append(Particle(bullet_x, ship.y, ship.color, lifetime=30, size=6))
            else:
                direction = 1 if ship.is_left else -1
                bullet_x = ship.x + (ship.width//2 + spawn_forward) * direction
                b = Bullet(bullet_x, ship.y, direction, ship.type)
                b.color = ship.color
                self.add_bullet(b)
        
        elif ship.type == "Kombuz":
            if is_charged:
                direction = 1 if ship.is_left else -1
                bullet_x = ship.x + (ship.width//2 + spawn_forward) * direction
                self.add_bullet(Bullet(bullet_x, ship.y, direction, ship.type, True, bullets_used))
            else:
                direction = 1 if ship.is_left else -1
                bullet_x = ship.x + (ship.width//2 + 15) * direction
                self.add_bullet(Bullet(bullet_x, ship.y, direction, ship.type))
        
        elif ship.type == "Rift":
            if is_charged:
                # Charged shot: Creates a sweeping pattern of boomerang bullets
                direction = 1 if ship.is_left else -1
                config = SHIPS["Rift"]
                bullet_x = ship.x + (ship.width//2 + 15) * direction
                sweep_angle = math.radians(config["sweep_angle"])
                
                # Fire bullets in an arc
                num_bullets = min(5, bullets_used)
                for i in range(num_bullets):
                    angle = (-sweep_angle/2) + (sweep_angle * i / (num_bullets-1))
                    b = Bullet(bullet_x, ship.y, direction, ship.type, True, bullets_used)
                    b.color = ship.color
                    b.angle = angle  # Used for movement
                    self.add_bullet(b)
                    
                    # Add particle effects for each bullet
                    self.particles.append(
                        Particle(bullet_x + math.cos(angle) * 10,
                                ship.y + math.sin(angle) * 10,
                                ship.color, lifetime=15, size=3)
                    )
                
                # Play sweep sound
                play_sound('sweep', ship.type)
            else:
                # Single shot: fires a spread of 3 boomerang bullets
                direction = 1 if ship.is_left else -1
                bullet_x = ship.x + (ship.width//2 + 15) * direction
                
                # Center bullet
                b = Bullet(bullet_x, ship.y, direction, ship.type)
                b.color = ship.color
                self.add_bullet(b)
                
                # Top and bottom bullets
                offset = 15
                b_top = Bullet(bullet_x, ship.y - offset, direction, ship.type)
                b_top.color = ship.color
                b_bottom = Bullet(bullet_x, ship.y + offset, direction, ship.type)
                b_bottom.color = ship.color
                self.add_bullet(b_top)
                self.add_bullet(b_bottom)
                
                # Add particle effects
                self.particles.append(Particle(bullet_x, ship.y, ship.color, lifetime=10, size=2))
                self.particles.append(Particle(bullet_x, ship.y - offset, ship.color, lifetime=10, size=2))
                self.particles.append(Particle(bullet_x, ship.y + offset, ship.color, lifetime=10, size=2))
                
        elif ship.type == "Gwiazdka":
            if is_charged:
                # Nova burst: fire multiple rays in sequence
                direction = 1 if ship.is_left else -1
                config = SHIPS["Gwiazdka"]
                rays = config["nova_rays"]
                bullet_x = ship.x + (ship.width//2 + 15) * direction
                
                # Calculate angles for nova burst
                for i in range(rays):
                    angle = (2 * math.pi * i) / rays
                    # Create bullet with this angle
                    b = Bullet(bullet_x, ship.y, direction, ship.type, True, bullets_used)
                    b.color = ship.color
                    b.angle = angle  # Used for both movement and rendering
                    b.nova = True    # Flag this as a nova burst bullet
                    self.add_bullet(b)
                    
                    # Particles for each ray
                    for _ in range(3):
                        self.particles.append(Particle(
                            bullet_x + math.cos(angle) * 10,
                            ship.y + math.sin(angle) * 10,
                            ship.color, lifetime=15, size=3
                        ))
                
                # Play nova burst sound
                play_sound('nova', ship.type)
            else:
                # Scatter shot: 3 bullets in a spread
                direction = 1 if ship.is_left else -1
                config = SHIPS["Gwiazdka"]
                bullet_x = ship.x + (ship.width//2 + 15) * direction
                
                # Calculate angles for scatter shot (center and offset angles)
                scatter_angle = math.radians(config["scatter_angle"])
                angles = [-scatter_angle/2, 0, scatter_angle/2]
                
                for angle in angles:
                    b = Bullet(bullet_x, ship.y, direction, ship.type)
                    b.color = ship.color
                    b.angle = angle  # Used for movement and rendering
                    b.scatter = True  # Flag this as a scatter shot bullet
                    self.add_bullet(b)
                    
                    # Small particle effect for each bullet
                    self.particles.append(Particle(
                        bullet_x + math.cos(angle) * 10,
                        ship.y + math.sin(angle) * 10,
                        ship.color, lifetime=10, size=2
                    ))
    
    def update(self):
        if self.state == "playing":
            # Keyboard-only input: read key state directly
            keys = pygame.key.get_pressed()

            # Networking: if client, send local input to host and skip local physics
            if self.network_role == 'client':
                try:
                    self.client_local_input = {
                        'up': bool(keys[K_UP]),
                        'down': bool(keys[K_DOWN]),
                        'left': bool(keys[K_LEFT]),
                        'right': bool(keys[K_RIGHT]),
                        'fire': bool(keys[K_RETURN])
                    }
                except Exception:
                    self.client_local_input = None

                # Perform interpolation towards latest authoritative snapshot for smooth visuals
                try:
                    target = getattr(self, 'remote_state_target', None)
                    if target:
                        if not self.remote_state_interp:
                            # Initialize interp with a shallow copy of the target
                            self.remote_state_interp = {'ship1': dict(target.get('ship1', {})),
                                                        'ship2': dict(target.get('ship2', {})),
                                                        'bullets': list(target.get('bullets', []))}
                        else:
                            # Interpolate ship positions
                            for sk in ('ship1', 'ship2'):
                                tgt = target.get(sk)
                                cur = self.remote_state_interp.get(sk)
                                if not tgt or not cur:
                                    continue
                                for coord in ('x', 'y'):
                                    try:
                                        tval = float(tgt.get(coord, cur.get(coord, 0)))
                                        cval = float(cur.get(coord, tval))
                                        new = cval + (tval - cval) * self.interp_alpha
                                        self.remote_state_interp[sk][coord] = new
                                    except Exception:
                                        pass
                                # Snap health and bullets to authoritative values
                                try:
                                    self.remote_state_interp[sk]['health'] = tgt.get('health', cur.get('health'))
                                    self.remote_state_interp[sk]['bullets'] = tgt.get('bullets', cur.get('bullets'))
                                except Exception:
                                    pass
                            # Replace bullets array (interpolating bullets is expensive; use direct snapshot)
                            try:
                                self.remote_state_interp['bullets'] = list(target.get('bullets', []))
                            except Exception:
                                pass
                        self.remote_state_time = time.time()
                except Exception:
                    pass

                # Do not run authoritative physics locally; rendering will use interpolated snapshot below
                return

            # If host, apply remote client inputs (if any) to ship2
            class _KeyMap:
                def __init__(self, mapping):
                    self.mapping = mapping or {}
                def __getitem__(self, key):
                    return self.mapping.get(key, False)

            if self.network_role == 'host' and self.client_remote_input:
                # Convert client_remote_input booleans to a KeyMap for ship2
                try:
                    mapping = {}
                    remote = self.client_remote_input
                    mapping[self.ship2.controls['up']] = remote.get('up', False)
                    mapping[self.ship2.controls['down']] = remote.get('down', False)
                    mapping[self.ship2.controls['left']] = remote.get('left', False)
                    mapping[self.ship2.controls['right']] = remote.get('right', False)
                    # fire is handled via key events from remote; emulate by calling start/stop charge
                    keys_for_ship2 = _KeyMap(mapping)
                    self.ship2.move(keys_for_ship2)
                    # Handle remote fire press/release
                    prev = getattr(self, 'client_prev_fire', False)
                    now = bool(remote.get('fire', False))
                    if now and not prev:
                        # fire pressed
                        if not self.ship2.charging:
                            self.ship2.start_charging()
                    elif not now and prev:
                        # fire released - decide tap vs hold
                        if self.ship2.charge_time < self.tap_threshold:
                            bullets_used = self.ship2.shoot_single()
                            if bullets_used > 0:
                                self.shoot_bullet(self.ship2, bullets_used, False)
                        else:
                            bullets_used = self.ship2.stop_charging()
                            if bullets_used > 0:
                                self.shoot_bullet(self.ship2, bullets_used, True)
                    self.client_prev_fire = now
                except Exception:
                    pass
            else:
                self.ship2.move(keys)

            # Always update ship1 locally
            self.ship1.move(keys)
            self.ship1.update_charge()
            self.ship2.update_charge()
            
            bullets_to_remove = []
            for i, bullet in enumerate(self.bullets):
                if bullet.move():
                    bullets_to_remove.append(i)
                
                # Check collisions using rects for accuracy
                bullet_rect = pygame.Rect(int(bullet.x - bullet.width//2), int(bullet.y - bullet.height//2), int(bullet.width), int(bullet.height))
                ship2_rect = pygame.Rect(int(self.ship2.x - self.ship2.width//2), int(self.ship2.y - self.ship2.height//2), int(self.ship2.width), int(self.ship2.height))
                ship1_rect = pygame.Rect(int(self.ship1.x - self.ship1.width//2), int(self.ship1.y - self.ship1.height//2), int(self.ship1.width), int(self.ship1.height))

                if bullet.direction == 1:  # From player1
                    if bullet_rect.colliderect(ship2_rect):
                        # Apply damage and visual/physics feedback
                        if self.ship2.take_damage():
                            self.winner = self.player1_name
                            self.state = "game_over"
                            play_sound('ship_explosion')  # Fatal hit sound
                        bullets_to_remove.append(i)
                        play_sound('hit', bullet.ship_type)  # Ship-specific hit sound
                        # Knockback and tilt
                        try:
                            push = 12
                            self.ship2.x += push
                            self.ship2.tilt = 8
                            self.ship2.tilt_timer = 18
                        except Exception:
                            pass
                        # Hit particles
                        for _ in range(8):
                            angle = random.random() * 2 * math.pi
                            px = self.ship2.x + math.cos(angle) * 8
                            py = self.ship2.y + math.sin(angle) * 8
                            self.particles.append(Particle(px, py, self.ship2.color, lifetime=25, size=3))
                else:  # From player2
                    if bullet_rect.colliderect(ship1_rect):
                        if self.ship1.take_damage():
                            self.winner = self.player2_name
                            self.state = "game_over"
                            play_sound('ship_explosion')  # Fatal hit sound
                        bullets_to_remove.append(i)
                        play_sound('hit', bullet.ship_type)  # Ship-specific hit sound
                        # Knockback and tilt
                        try:
                            push = 12
                            self.ship1.x -= push
                            self.ship1.tilt = -8
                            self.ship1.tilt_timer = 18
                        except Exception:
                            pass
                        # Hit particles
                        for _ in range(8):
                            angle = random.random() * 2 * math.pi
                            px = self.ship1.x + math.cos(angle) * 8
                            py = self.ship1.y + math.sin(angle) * 8
                            self.particles.append(Particle(px, py, self.ship1.color, lifetime=25, size=3))

                # Komar charged beam: instant full-screen beam with immediate damage
                if bullet.ship_type == "Komar" and bullet.is_charged:
                    # Create beam rect that spans from bullet origin to screen edge
                    beam_width = max(8, bullet.width)
                    if bullet.direction == 1:  # Right-facing beam
                        beam_rect = pygame.Rect(bullet.x, 0, SCREEN_WIDTH - bullet.x, SCREEN_HEIGHT)
                    else:  # Left-facing beam
                        beam_rect = pygame.Rect(0, 0, bullet.x, SCREEN_HEIGHT)
                    
                    # Apply instant damage on the first frame only
                    if bullet.timer == 0:  # When beam first appears
                        target_rect = ship2_rect if bullet.direction == 1 else ship1_rect
                        if beam_rect.colliderect(target_rect):
                            if bullet.direction == 1:
                                if self.ship2.take_damage():
                                    self.winner = self.player1_name
                                    self.state = "game_over"
                                    play_sound('ship_explosion')
                            else:
                                if self.ship1.take_damage():
                                    self.winner = self.player2_name
                                    self.state = "game_over"
                                    play_sound('ship_explosion')
                    
                    # Remove beam after a short display time
                    if bullet.timer >= FPS//4:  # Show beam for 1/4 second
                        bullets_to_remove.append(i)

                # Kombuz explosion handling with distance-based damage
                if bullet.ship_type == "Kombuz" and bullet.exploding and not bullet.explosion_applied:
                    radius = bullet.explosion_timer * 4  # Match visual radius
                    for ship, name, rect in [(self.ship1, self.player1_name, ship1_rect), 
                                           (self.ship2, self.player2_name, ship2_rect)]:
                        dist = math.hypot(bullet.x - ship.x, bullet.y - ship.y)
                        if dist <= radius:
                            # Damage scales with distance (more damage closer to center)
                            damage_scale = 1.0 - (dist / radius)
                            hits = max(1, int(3 * damage_scale))  # 1-3 hits based on distance
                            
                            # Create particle effects for hit visualization
                            for _ in range(hits * 2):  # 2 particles per hit
                                angle = random.random() * 2 * math.pi
                                speed = random.randint(2, 5)
                                particle_x = ship.x + math.cos(angle) * 10
                                particle_y = ship.y + math.sin(angle) * 10
                                self.particles.append(
                                    Particle(particle_x, particle_y, ship.color,
                                           lifetime=20, size=3)
                                )
                            
                            # Apply damage hits
                            for _ in range(hits):
                                if ship.take_damage():
                                    self.winner = name
                                    self.state = "game_over"
                                    break
                    
                    # Play Kombuz-specific mine explosion sound
                    bullet.explosion_applied = True
                    play_sound('mine_explode', 'Kombuz')
            
            for i in sorted(bullets_to_remove, reverse=True):
                if i < len(self.bullets):
                    self.bullets.pop(i)

            # Update particles
            particles_to_remove = []
            for pi, p in enumerate(self.particles):
                if p.update():
                    particles_to_remove.append(pi)
            for pi in sorted(particles_to_remove, reverse=True):
                self.particles.pop(pi)
    
    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "playing":
            self.draw_game()
        elif self.state == "game_over":
            self.draw_game_over()
        elif self.state == "help":
            self.draw_help()
        
        # Draw settings overlay if open
        if self.settings_open:
            self.draw_settings_menu()
        
        pygame.display.flip()
    
    def draw_settings_menu(self):
        """Draw the settings menu overlay"""
        # Semi-transparent background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Settings panel with border
        panel_width = 700
        panel_height = 520
        panel_x = SCREEN_WIDTH//2 - panel_width//2
        panel_y = 40
        
        # Draw panel with border
        pygame.draw.rect(self.screen, SETTINGS_BG_COLOR, 
                        (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, SETTINGS_TEXT_COLOR, 
                        (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Title with underline
        title = self.font.render("Settings", True, SETTINGS_TEXT_COLOR)
        title_x = SCREEN_WIDTH//2 - title.get_width()//2
        title_y = panel_y + 20
        self.screen.blit(title, (title_x, title_y))
        
        # Underline
        pygame.draw.line(self.screen, SETTINGS_TEXT_COLOR,
                        (panel_x + 50, title_y + 35),
                        (panel_x + panel_width - 50, title_y + 35), 2)
        
        # Volume section title
        volume_title = self.font.render("Volume Controls", True, SETTINGS_TEXT_COLOR)
        volume_y = title_y + 70
        self.screen.blit(volume_title, (panel_x + 50, volume_y))
        
        # Volume controls with consistent spacing
        bar_width = 400
        bar_height = 15
        bar_x = panel_x + (panel_width - bar_width) // 2
        
        # Music volume with label and percentage
        music_y = volume_y + 50
        self.draw_volume_bar(bar_x, music_y, bar_width, bar_height, 
                           self.settings["music_volume"], "Background Music")
        
        # Sound effects volume
        sfx_y = music_y + 60
        self.draw_volume_bar(bar_x, sfx_y, bar_width, bar_height,
                           self.settings["sfx_volume"], "Sound Effects")
        
        # Key bindings
        self.draw_key_bindings()
        
        # Reset button
        pygame.draw.rect(self.screen, (100, 100, 100), 
                        (SCREEN_WIDTH//2 - 100, 500, 200, 40))
        reset_text = self.font.render("Reset to Default", True, SETTINGS_TEXT_COLOR)
        self.screen.blit(reset_text, 
                        (SCREEN_WIDTH//2 - reset_text.get_width()//2, 510))
        # Close (X) button at top-left of settings panel
        close_rect = pygame.Rect(panel_x + panel_width - 34, panel_y + 6, 28, 28)
        pygame.draw.rect(self.screen, (180, 60, 60), close_rect)
        x_text = self.font.render("X", True, (255, 255, 255))
        self.screen.blit(x_text, (close_rect.x + (close_rect.w - x_text.get_width())//2, close_rect.y + (close_rect.h - x_text.get_height())//2))
    
    def draw_key_bindings(self):
        """Draw key binding options in two columns"""
        panel_x = SCREEN_WIDTH//2 - 350  # Align with panel
        base_y = 280  # Start below volume controls
        spacing = 35
        section_spacing = 20
        
        # Controls section title
        controls_title = self.font.render("Controls", True, SETTINGS_TEXT_COLOR)
        self.screen.blit(controls_title, (panel_x + 50, base_y))
        base_y += 50
        
        # Column headers
        p1_title = self.font.render("Player 1", True, SETTINGS_TEXT_COLOR)
        p2_title = self.font.render("Player 2", True, SETTINGS_TEXT_COLOR)
        self.screen.blit(p1_title, (panel_x + 150 - p1_title.get_width()//2, base_y))
        self.screen.blit(p2_title, (panel_x + 500 - p2_title.get_width()//2, base_y))
        base_y += 30
        
        # Draw separating line
        pygame.draw.line(self.screen, SETTINGS_TEXT_COLOR,
                        (panel_x + 325, base_y - 20),
                        (panel_x + 325, base_y + spacing * 5), 1)
        
        # Key bindings in two columns
        keys = [("Up", "_up"), ("Down", "_down"), ("Left", "_left"), 
                ("Right", "_right"), ("Fire", "_fire")]
        
        for i, (label, suffix) in enumerate(keys):
            y = base_y + (spacing + section_spacing) * i
            # Player 1 controls (left column)
            self.draw_key_option(label, "p1" + suffix, panel_x + 100, y)
            # Player 2 controls (right column)
            self.draw_key_option(label, "p2" + suffix, panel_x + 450, y)
    
    def draw_key_option(self, label, key, x, y):
        """Draw a single key binding option with improved visuals"""
        # Label
        text = self.small_font.render(f"{label}: ", True, SETTINGS_TEXT_COLOR)
        text_x = x - text.get_width()
        self.screen.blit(text, (text_x, y + 2))  # Vertical align with button
        
        # Key button with border
        button_width = 120
        button_height = 25
        button_color = SETTINGS_HIGHLIGHT if self.remapping_key == key else SETTINGS_BAR_BG
        
        # Draw button background
        pygame.draw.rect(self.screen, button_color, 
                        (x, y, button_width, button_height))
        # Draw button border
        pygame.draw.rect(self.screen, SETTINGS_TEXT_COLOR, 
                        (x, y, button_width, button_height), 1)
        
        # Key name centered in button
        key_name = pygame.key.name(self.settings[key]).upper()
        key_text = self.small_font.render(key_name, True, SETTINGS_TEXT_COLOR)
        text_x = x + (button_width - key_text.get_width()) // 2
        text_y = y + (button_height - key_text.get_height()) // 2
        self.screen.blit(key_text, (text_x, text_y))
        
        # Visual indicator if being remapped
        if self.remapping_key == key:
            pygame.draw.rect(self.screen, SETTINGS_TEXT_COLOR, 
                           (x, y, button_width, button_height), 2)
    
    def get_key_remap_areas(self):
        """Get rectangles for all key remap buttons"""
        areas = {}
        panel_x = SCREEN_WIDTH//2 - 350
        # Match draw_key_bindings layout: after title+headers the first key y is 360
        base_y = 360
        button_width = 120
        button_height = 25
        row_spacing = 55  # spacing + section_spacing in draw_key_bindings

        p1_x = panel_x + 100
        p2_x = panel_x + 450

        keys_p1 = ["p1_up", "p1_down", "p1_left", "p1_right", "p1_fire"]
        keys_p2 = ["p2_up", "p2_down", "p2_left", "p2_right", "p2_fire"]

        for i, key in enumerate(keys_p1):
            areas[key] = pygame.Rect(p1_x, base_y + row_spacing * i, button_width, button_height)

        for i, key in enumerate(keys_p2):
            areas[key] = pygame.Rect(p2_x, base_y + row_spacing * i, button_width, button_height)

        return areas
    
    def draw_menu(self):
        # Title: prefer APK title image if available
        title_img = load_image('Title_Fill_A.png') or load_image('Title_Fill_L.png')
        if title_img:
            img = pygame.transform.smoothscale(title_img, (min(600, title_img.get_width()), int(title_img.get_height() * 600 / max(1, title_img.get_width()))))
            self.screen.blit(img, (SCREEN_WIDTH//2 - img.get_width()//2, 20))
            title_y = 20 + img.get_height() + 8
        else:
            # Fallback text title
            title_font = pygame.font.SysFont(None, 72)
            title = title_font.render("2D-Flox", True, FONT_COLOR)
            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
            title_y = 50 + title.get_height() + 8
        
        # Settings icon
        self.draw_settings_icon()
        
        # Version number
        version_text = self.small_font.render(f"v{GAME_VERSION}", True, (150, 150, 150))
        self.screen.blit(version_text, (SCREEN_WIDTH - version_text.get_width() - 10, 10))
        
        # Draw divider line
        pygame.draw.line(self.screen, BORDER_COLOR, (SCREEN_WIDTH//2, 100), (SCREEN_WIDTH//2, SCREEN_HEIGHT - 100), 2)
        
        # Player 1 section (left)
        p1_title = self.font.render("PLAYER 1", True, self.player1_color)
        self.screen.blit(p1_title, (SCREEN_WIDTH//4 - p1_title.get_width()//2, title_y + 10))
        
        # Player 1 name
        p1_name_text = self.font.render("Name: " + self.player1_name, True, 
                                       HIGHLIGHT_COLOR if self.input_active == "player1" else FONT_COLOR)
        self.screen.blit(p1_name_text, (SCREEN_WIDTH//4 - p1_name_text.get_width()//2, 150))
        
        # Player 1 ship and preview
        p1_ship_text = self.font.render("Ship: " + self.player1_ship, True, 
                                       HIGHLIGHT_COLOR if self.input_active == "ship1" else FONT_COLOR)
        self.screen.blit(p1_ship_text, (SCREEN_WIDTH//4 - p1_ship_text.get_width()//2, title_y + 80))
        # preview sprite
        p1_preview = get_ship_sprite(self.player1_ship, self.player1_color, 120)
        if p1_preview:
            r = p1_preview.get_rect(center=(SCREEN_WIDTH//4, title_y + 80 + 80))
            self.screen.blit(p1_preview, r)
        
        # Player 1 color
        pygame.draw.rect(self.screen, self.player1_color, (SCREEN_WIDTH//4 - 50, 290, 100, 30))
        pygame.draw.rect(self.screen, HIGHLIGHT_COLOR if self.input_active == "color1" else FONT_COLOR, 
                        (SCREEN_WIDTH//4 - 50, 290, 100, 30), 2)
        
        # Player 2 section (right)
        p2_title = self.font.render("PLAYER 2", True, self.player2_color)
        self.screen.blit(p2_title, (3*SCREEN_WIDTH//4 - p2_title.get_width()//2, title_y + 10))
        
        # Player 2 name
        p2_name_text = self.font.render("Name: " + self.player2_name, True, 
                                       HIGHLIGHT_COLOR if self.input_active == "player2" else FONT_COLOR)
        self.screen.blit(p2_name_text, (3*SCREEN_WIDTH//4 - p2_name_text.get_width()//2, 150))
        
        # Player 2 ship and preview
        p2_ship_text = self.font.render("Ship: " + self.player2_ship, True, 
                                       HIGHLIGHT_COLOR if self.input_active == "ship2" else FONT_COLOR)
        self.screen.blit(p2_ship_text, (3*SCREEN_WIDTH//4 - p2_ship_text.get_width()//2, title_y + 80))
        p2_preview = get_ship_sprite(self.player2_ship, self.player2_color, 120)
        if p2_preview:
            r2 = p2_preview.get_rect(center=(3*SCREEN_WIDTH//4, title_y + 80 + 80))
            self.screen.blit(p2_preview, r2)
        
        # Player 2 color
        pygame.draw.rect(self.screen, self.player2_color, (3*SCREEN_WIDTH//4 - 50, 290, 100, 30))
        pygame.draw.rect(self.screen, HIGHLIGHT_COLOR if self.input_active == "color2" else FONT_COLOR, 
                        (3*SCREEN_WIDTH//4 - 50, 290, 100, 30), 2)
        
        # Host / Join controls (use icons if available)
        host_w = 220
        host_h = 48
        host_x = SCREEN_WIDTH//2 - host_w - 20
        host_y = SCREEN_HEIGHT - 160
        join_x = SCREEN_WIDTH//2 + 20
        join_y = host_y

        # Draw host button
        host_rect = pygame.Rect(host_x, host_y, host_w, host_h)
        pygame.draw.rect(self.screen, (30,130,200), host_rect)
        host_text = self.small_font.render("Host (WiFi)", True, (255,255,255))
        self.screen.blit(host_text, (host_x + 12, host_y + host_h//2 - host_text.get_height()//2))

        # draw join button and IP field
        join_rect = pygame.Rect(join_x, join_y, host_w, host_h)
        pygame.draw.rect(self.screen, (50,150,50), join_rect)
        join_text = self.small_font.render("Join (IP)", True, (255,255,255))
        self.screen.blit(join_text, (join_x + 12, join_y + host_h//2 - join_text.get_height()//2))

        # IP input field under join
        ip_field = pygame.Rect(join_x, join_y + host_h + 8, host_w, 34)
        pygame.draw.rect(self.screen, (20,20,20), ip_field)
        pygame.draw.rect(self.screen, FONT_COLOR if self.input_active == 'connect_ip' else (100,100,100), ip_field, 2)
        ip_text = self.small_font.render(self.connect_ip or "Enter host IP...", True, (200,200,200))
        self.screen.blit(ip_text, (ip_field.x + 8, ip_field.y + 6))

        # store regions for click handling
        self.menu_regions['host'] = host_rect
        self.menu_regions['join'] = join_rect
        self.menu_regions['ip_field'] = ip_field

        # Preview panels (compact)
        panel_width = 150
        panel_height = 150
        panel_y = 380
        
        # Left preview panel - 30% from left edge
        left_panel_x = SCREEN_WIDTH * 0.3 - panel_width//2
        pygame.draw.rect(self.screen, (0, 0, 0), 
                        (left_panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, (50, 50, 50),  # subtle border
                        (left_panel_x, panel_y, panel_width, panel_height), 2)
        left_ship = Ship(left_panel_x + panel_width//2, panel_y + panel_height//2, 
                        self.player1_ship, self.player1_color, {}, True)
        left_ship.draw(self.screen)
        
        # Right preview panel - 70% from left edge
        right_panel_x = SCREEN_WIDTH * 0.7 - panel_width//2
        pygame.draw.rect(self.screen, (0, 0, 0),
                        (right_panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, (50, 50, 50),  # subtle border
                        (right_panel_x, panel_y, panel_width, panel_height), 2)
        right_ship = Ship(right_panel_x + panel_width//2, panel_y + panel_height//2,
                         self.player2_ship, self.player2_color, {}, False)
        right_ship.draw(self.screen)
        # Minimal descriptions below previews (avoid overlap)
        left_config = SHIPS[self.player1_ship]
        right_config = SHIPS[self.player2_ship]
        left_panel_center_x = SCREEN_WIDTH * 0.3
        right_panel_center_x = SCREEN_WIDTH * 0.7
        left_desc = self.small_font.render(left_config.get("description", ""), True, FONT_COLOR)
        right_desc = self.small_font.render(right_config.get("description", ""), True, FONT_COLOR)
        self.screen.blit(left_desc, (left_panel_center_x - left_desc.get_width()//2, panel_y + panel_height + 8))
        self.screen.blit(right_desc, (right_panel_center_x - right_desc.get_width()//2, panel_y + panel_height + 8))
        
        # Start button
        pygame.draw.rect(self.screen, (0, 150, 0), (SCREEN_WIDTH//2 - 100, 450, 200, 40))
        start_text = self.font.render("START GAME", True, FONT_COLOR)
        self.screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, 460))
        
        # Info button
        pygame.draw.rect(self.screen, (100, 100, 100), (SCREEN_WIDTH//2 - 100, 520, 200, 40))
        info_text = self.font.render("INFO", True, FONT_COLOR)
        self.screen.blit(info_text, (SCREEN_WIDTH//2 - info_text.get_width()//2, 530))
        
        # Instructions
        instr_text = self.small_font.render("Use TAB to navigate, LEFT/RIGHT to change selection, ENTER to confirm", True, (150, 150, 150))
        self.screen.blit(instr_text, (SCREEN_WIDTH//2 - instr_text.get_width()//2, SCREEN_HEIGHT - 30))
    
    def draw_game(self):
        # Draw middle border
        pygame.draw.line(self.screen, BORDER_COLOR, (SCREEN_WIDTH//2, 0), (SCREEN_WIDTH//2, SCREEN_HEIGHT), 2)
        
        # Network client: render authoritative snapshot received from host
        # Prefer interpolated state for smoother visuals, fallback to last raw state
        if self.network_role == 'client' and (self.remote_state_interp or self.remote_state):
            try:
                state = self.remote_state_interp if self.remote_state_interp else self.remote_state
                # Draw remote ships
                s1 = state.get('ship1', {})
                s2 = state.get('ship2', {})
                # Draw ship1
                img1 = get_ship_sprite(s1.get('type','Zaba'), self.player1_color, SHIP_SIZE)
                if img1:
                    r1 = img1.get_rect(center=(int(s1.get('x',100)), int(s1.get('y', SCREEN_HEIGHT//2))))
                    self.screen.blit(img1, r1)
                # Draw ship2
                img2 = get_ship_sprite(s2.get('type','Zaba'), self.player2_color, SHIP_SIZE)
                if img2:
                    r2 = img2.get_rect(center=(int(s2.get('x', SCREEN_WIDTH-100)), int(s2.get('y', SCREEN_HEIGHT//2))))
                    self.screen.blit(img2, r2)

                # Draw bullets from snapshot
                for b in state.get('bullets', []):
                    bx = b.get('x', 0)
                    by = b.get('y', 0)
                    btype = b.get('ship_type', 'Zaba')
                    bshape = SHIPS.get(btype, {}).get('bullet_shape', 'circle')
                    bsprite = get_bullet_sprite(bshape, max(4, int(b.get('w', 8))), self.player1_color)
                    if bsprite:
                        rect = bsprite.get_rect(center=(int(bx), int(by)))
                        self.screen.blit(bsprite, rect)
                    else:
                        pygame.draw.circle(self.screen, BULLET_COLOR, (int(bx), int(by)), int(max(2, b.get('w', 6)//2)))
                
                # Draw player names
                p1_name = self.small_font.render(self.player1_name, True, self.player1_color)
                p2_name = self.small_font.render(self.player2_name, True, self.player2_color)
                self.screen.blit(p1_name, (20, 20))
                self.screen.blit(p2_name, (SCREEN_WIDTH - p2_name.get_width() - 20, 20))
                return
            except Exception:
                pass

        # Draw ships
        self.ship1.draw(self.screen)
        self.ship2.draw(self.screen)
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(self.screen)
        # Draw player names only - health indicated by ship color dimming
        p1_name = self.small_font.render(self.player1_name, True, self.player1_color)
        p2_name = self.small_font.render(self.player2_name, True, self.player2_color)
        self.screen.blit(p1_name, (20, 20))
        self.screen.blit(p2_name, (SCREEN_WIDTH - p2_name.get_width() - 20, 20))
        # No on-screen touch controls rendered (keyboard-only mode)
    
    def draw_game_over(self):
        self.draw_game()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        winner_font = pygame.font.SysFont(None, 72)
        winner_text = winner_font.render(f"{self.winner} WINS!", True, HIGHLIGHT_COLOR)
        self.screen.blit(winner_text, (SCREEN_WIDTH//2 - winner_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        
        restart_text = self.font.render("Press ENTER to return to menu", True, FONT_COLOR)
        self.screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 50))
    
    def draw_help(self):
        # Fill with help screen background color
        self.screen.fill(HELP_BG_COLOR)
        
        title_font = pygame.font.SysFont(None, 72)
        title = title_font.render("INFO", True, HELP_TEXT_COLOR)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 30))
        
        help_lines = [
            "CONTROLS:",
            "Player 1: WASD to move, SPACE to shoot (tap for single, hold for charged)",
            "Player 2: ARROW KEYS to move, ENTER to shoot (tap for single, hold for charged)",
            "",
            "GAMEPLAY:",
            "- Ships cannot cross the center line",
            "- Bullets can pass through the center line",
            "- Health decreases when hit by bullets",
            "- Ships dim in color as they take damage",
            "- First to destroy the opponent wins",
            "",
            "SHIP TYPES:",
            "- Zaba: Square ship with charged block attack",
            "- Rekin: Fast triangle ship with triple shot", 
            "- Osa: Rapid-fire circular ship",
            "- Komar: Laser-based kite ship",
            "- Kombuz: Hexagonal mine-layer ship",
            "",
            "=== CREDITS ===",
            "Author: Voltsparx (AKA Niyor Kalita)",
            "Contact: voltsparx@gmail.com",
            "",
            "Dedication:",
            "Dedicated to the Voltros Community",
            "Especially dedicated to the person named Lovely Thakuria.",
            "",
            "=== AUDIO CREDITS ===",
            "Background Music: Redlight_Chill",
            "Menu Sound Effects: Voltsparx",
            "",
            f"2D-Flox v{GAME_VERSION}",
            "Based on DUAL! by Seabaa",
            "",
            "Press ENTER or ESC to return to menu"
        ]
        
        # Draw text with better vertical spacing
        for i, line in enumerate(help_lines):
            # Headers in bold (implement via larger font)
            if line.startswith("==="):
                text = self.font.render(line, True, HELP_TEXT_COLOR)
                y_offset = 100 + i * 22  # slightly tighter spacing
            else:
                text = self.small_font.render(line, True, HELP_TEXT_COLOR)
                y_offset = 100 + i * 22  # slightly tighter spacing
            self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y_offset))
    
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    game = Game()
    game.run()