from pathlib import Path
from enum import IntEnum

class Phase(IntEnum):
    EXIT = 0
    NORMAL = 1
    READY = 2
    DEATH = 3
    ABS_DEATH = 4
    ALL_PELLETS = 5

class GhostMode(IntEnum):
    SCATTER = 1
    CHASE = 2

class GhostFrightStage(IntEnum):
    UNFRIGHTENED = 0
    FRIGHTENED = 1
    TIMEOUT = 2
    LEAVING_HOUSE = 3


def GHOST_MODE_INTERVAL(game_data):
    match game_data["ghost_mode"]:
        case GhostMode.SCATTER:
            if game_data["ghost_mode_cycle"] <= 2:
                return 7.0
            elif game_data["ghost_mode_cycle"] == 3:
                return 5.0
            elif game_data["ghost_mode_cycle"] >= 4:
                return 0.0
        case GhostMode.CHASE:
            if game_data["ghost_mode_cycle"] <= 3:
                return 20.0
            else:
                return float('inf')
        
    return 0.0


def GHOST_FRIGHTENED_INTERVAL(game_data):
    if game_data["level"] < 5: return 6.0
    elif game_data["level"] < 9: return 3.0
    elif game_data["level"] < 21: return 1.0
    else: return 0.0


def SPEED(game_data, is_pacman, fright_stage=0):
    speed = UNIT * 12

    if is_pacman:
        if game_data["level"] < 5: speed *= 0.8
        elif game_data["level"] < 9: speed *= 0.9
        elif game_data["level"] < 21: speed *= 1.0
        else: speed *= 0.9
        return speed
    else:
        if game_data["level"] < 5: speed *= 0.75
        elif game_data["level"] < 9: speed *= 0.85
        elif game_data["level"] < 21: speed *= 0.95
        else: speed *= 0.95

        match fright_stage:
            case GhostFrightStage.UNFRIGHTENED:  return speed
            case GhostFrightStage.FRIGHTENED:    return speed * 0.6
            case GhostFrightStage.TIMEOUT:       return 0.0
            case GhostFrightStage.LEAVING_HOUSE: return speed
            case _: return 0.0


def FRUIT_TYPE_AND_POINTS(game_data):
    if game_data["level"] == 1: return 0, 100
    elif game_data["level"] == 2: return 1, 300
    elif game_data["level"] < 5: return 2, 500
    elif game_data["level"] < 7: return 3, 700
    elif game_data["level"] < 9: return 4, 1000
    elif game_data["level"] < 11: return 5, 2000
    elif game_data["level"] < 13: return 5, 3000
    else: return 5, 5000


FPS = 60
UNIT = 16

HIGHSCORE_PATH = Path.home() / "pacman_highscore.txt"

PACMAN_START_POS = UNIT*14, UNIT*23
GHOST1_START_POS = UNIT*13.5, UNIT*11
GHOST2_START_POS = UNIT*12, UNIT*14
GHOST3_START_POS = UNIT*13.5, UNIT*14
GHOST4_START_POS = UNIT*15, UNIT*14

GHOST1_SPEEDUP_PELLET_NUM = 150

READY_INTERVAL = 1.5
DEATH_INTERVAL = 1.0
ABS_DEATH_INTERVAL = 3.0
ALL_PELLETS_INTERVAL = 1.0
PACMAN_TEXTURE_SWITCH_INTERVAL = 0.1
POWER_PELLET_BLINK_INTERVAL = 0.15
FRUIT_INTERVAL = 9.0
POWER_UP_INTERVAL = 6.0
SHOOT_INTERVAL = 0.1
GHOST_TIMEOUT_INTERVAL = 1.5
GHOST_LEAVING_ARENA_INTERVAL = 0.5
