from pathlib import Path

FPS = 60
UNIT = 16

HIGHSCORE_PATH = Path.home() / "pacman_highscore.txt"

PACMAN_START_POS = UNIT*14, UNIT*23
GHOST1_START_POS = UNIT*13.5, UNIT*11
GHOST2_START_POS = UNIT*12, UNIT*14
GHOST3_START_POS = UNIT*13.5, UNIT*14
GHOST4_START_POS = UNIT*15, UNIT*14

GHOST1_SPEEDUP_PELLET_NUM = 150

EXIT_PHASE = 0
NORMAL_PHASE = 1
READY_PHASE = 2
DEATH_PHASE = 3
ABS_DEATH_PHASE = 4
ALL_PELLETS_PHASE = 5

GHOST_SCATTER_MODE = 0
GHOST_CHASE_MODE = 1

READY_INTERVAL = 1.5
DEATH_INTERVAL = 1.0
ALL_PELLETS_INTERVAL = 1.0
PACMAN_TEXTURE_SWITCH_INTERVAL = 0.1
POWER_PELLET_BLINK_INTERVAL = 0.15

def GHOST_MODE_INTERVAL(game_data):
    if game_data["ghost_mode"] == GHOST_SCATTER_MODE:
        if game_data["ghost_mode_cycle"] <= 2:
            return 7.0
        elif game_data["ghost_mode_cycle"] == 3:
            return 5.0
        elif game_data["ghost_mode_cycle"] >= 4:
            return 0.0
    elif game_data["ghost_mode"] == GHOST_CHASE_MODE:
        if game_data["ghost_mode_cycle"] <= 3:
            return 20.0
        else:
            return float('inf')
    
    return 0.0


def SPEED(game_data, pacman):
    base_speed = UNIT * 12

    if pacman:
        if game_data["level"] < 5: return base_speed * 0.8
        elif game_data["level"] < 9: return base_speed * 0.9
        elif game_data["level"] < 21: return base_speed * 1.0
        else: return base_speed * 0.9
    else:
        if game_data["level"] < 5: return base_speed * 0.75
        elif game_data["level"] < 9: return base_speed * 0.85
        elif game_data["level"] < 21: return base_speed * 0.95
        else: return base_speed * 0.95
