from pathlib import Path

FPS = 60
UNIT = 16
PACMAN_SPEED = UNIT * 10
GHOST_SPEED = UNIT * 7

HIGHSCORE_PATH = Path.home() / "pacman_highscore.txt"

PACMAN_START_POS = UNIT*14, UNIT*23
GHOST1_START_POS = UNIT*13.5, UNIT*11
GHOST2_START_POS = UNIT*12, UNIT*14
GHOST3_START_POS = UNIT*13.5, UNIT*14
GHOST4_START_POS = UNIT*15, UNIT*14

EXIT_MODE = 0
NORMAL_MODE = 1
READY_MODE = 2
DEATH_MODE = 3
ABS_DEATH_MODE = 4
ALL_PELLETS_MODE = 5

GHOST_SCATTER_MODE = 0
GHOST_CHASE_MODE = 1

READY_INTERVAL = 1.5
DEATH_INTERVAL = 1.0
ALL_PELLETS_INTERVAL = 1.0
PACMAN_TEXTURE_SWITCH_INTERVAL = 0.1
GHOST_CHASE_DIRECTION_SWITCH_INTERVAL = 0.3
GHOST_SCATTER_DIRECTION_SWITCH_INTERVAL = 0.6

def GHOST_INTERVAL(ghost_mode, ghost_mode_cycle):
    if ghost_mode == GHOST_SCATTER_MODE:
        if ghost_mode_cycle <= 2:
            return 7.0
        elif ghost_mode_cycle == 3:
            return 5.0
        elif ghost_mode_cycle >= 4:
            return 0.0
    elif ghost_mode == GHOST_CHASE_MODE:
        if ghost_mode_cycle <= 3:
            return 20.0
        else:
            return float('inf')
    
    return 0.0


POWER_PELLET_BLINK_INTERVAL = 0.15