import pygame

from . import const
from . import sprites

def load_all(width, height, mapcontent, walls_group, pellets_group, power_pellets_group, fruits_group, crossing_rects):
    """Alle statischen Sprites aus dem Map-Inhalt laden"""

    for y in range(height):
        for x in range(width):
            match mapcontent[y][x]:
                case '#': walls_group.add(sprites.Wall((x * const.UNIT, y * const.UNIT)))
                case '-': walls_group.add(sprites.Wall((x * const.UNIT, y * const.UNIT), ghost=True))
                case '.': pellets_group.add(sprites.NormalPellet((x * const.UNIT, y * const.UNIT)))
                case '+': crossing_rects.append(pygame.Rect(x * const.UNIT, y * const.UNIT, const.UNIT*2, const.UNIT*2))
                case ':':
                    crossing_rects.append(pygame.Rect(x * const.UNIT, y * const.UNIT, const.UNIT*2, const.UNIT*2))
                    pp = sprites.PowerPellet((x * const.UNIT, y * const.UNIT))
                    pellets_group.add(pp)
                    power_pellets_group.add(pp)
                case 'x':
                    crossing_rects.append(pygame.Rect(x * const.UNIT, y * const.UNIT, const.UNIT*2, const.UNIT*2))
                    pellets_group.add(sprites.NormalPellet((x * const.UNIT, y * const.UNIT)))
                case 'o':
                    fruits_group.add(sprites.Fruit((x * const.UNIT, y * const.UNIT)))


def load_pellets(width, height, mapcontent, pellets_group, power_pellets_group):
    """Nur Pellets aus dem Map-Inhalt laden"""
    
    for y in range(height):
        for x in range(width):         
            match mapcontent[y][x]:
                case '.': pellets_group.add(sprites.NormalPellet((x * const.UNIT, y * const.UNIT)))
                case 'x': pellets_group.add(sprites.NormalPellet((x * const.UNIT, y * const.UNIT)))
                case ':':
                    pp = sprites.PowerPellet((x * const.UNIT, y * const.UNIT))
                    pellets_group.add(pp)
                    power_pellets_group.add(pp)
