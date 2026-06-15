import pygame

from .const import *
from . import sprites

def load_all(width, height, mapcontent, walls_group, pellets_group, power_pellets_group,
             fruits_group, powerups_group, crossing_rects):
    """Alle statischen Sprites aus dem Map-Inhalt laden"""

    for y in range(height):
        for x in range(width):
            match mapcontent[y][x]:
                case '#': walls_group.add(sprites.Wall((x * UNIT, y * UNIT)))
                case '-': walls_group.add(sprites.Wall((x * UNIT, y * UNIT), ghost=True))
                case '.': pellets_group.add(sprites.NormalPellet((x * UNIT, y * UNIT)))
                case '+': crossing_rects.append(pygame.Rect(x * UNIT, y * UNIT, UNIT*2, UNIT*2))
                case ':':
                    crossing_rects.append(pygame.Rect(x * UNIT, y * UNIT, UNIT*2, UNIT*2))
                    pp = sprites.PowerPellet((x * UNIT, y * UNIT))
                    pellets_group.add(pp)
                    power_pellets_group.add(pp)
                case 'x':
                    crossing_rects.append(pygame.Rect(x * UNIT, y * UNIT, UNIT*2, UNIT*2))
                    pellets_group.add(sprites.NormalPellet((x * UNIT, y * UNIT)))
                case 'o':
                    fruits_group.add(sprites.Fruit((x * UNIT, y * UNIT)))
                case 'e':
                    powerups_group.add(sprites.ExtraLife((x * UNIT, y * UNIT)))
                    pellets_group.add(sprites.NormalPellet((x * UNIT, y * UNIT)))
                case 'g':
                    powerups_group.add(sprites.Gambler((x * UNIT, y * UNIT)))
                    pellets_group.add(sprites.NormalPellet((x * UNIT, y * UNIT)))
                case 's':
                    powerups_group.add(sprites.ShadowDash((x * UNIT, y * UNIT)))
                    pellets_group.add(sprites.NormalPellet((x * UNIT, y * UNIT)))
                case 'b':
                    powerups_group.add(sprites.Dart((x * UNIT, y * UNIT)))
                    pellets_group.add(sprites.NormalPellet((x * UNIT, y * UNIT)))


def load_pellets(width, height, mapcontent, pellets_group, power_pellets_group):
    """Nur Pellets aus dem Map-Inhalt laden"""
    
    for y in range(height):
        for x in range(width):         
            match mapcontent[y][x]:
                case '.' | 'x' | 'e' | 'g' | 's' | 'b':
                    pellets_group.add(sprites.NormalPellet((x * UNIT, y * UNIT)))
                case ':':
                    pp = sprites.PowerPellet((x * UNIT, y * UNIT))
                    pellets_group.add(pp)
                    power_pellets_group.add(pp)
