from . import const
from . import sprites

def load_all(width, height, mapcontent, walls_group, pellets_group):
    """Alle statischen Sprites aus dem Map-Inhalt laden"""

    for y in range(height):
        for x in range(width):
            block = mapcontent[y][x]

            if block == '#':
                walls_group.add(sprites.Wall((x * const.UNIT, y * const.UNIT)))
            elif block == '-':
                walls_group.add(sprites.Wall((x * const.UNIT, y * const.UNIT), ghost=True))
            elif block == '.':
                pellets_group.add(sprites.NormalPellet((x * const.UNIT, y * const.UNIT)))
            elif block == ':':
                pellets_group.add(sprites.PowerPellet((x * const.UNIT, y * const.UNIT)))


def load_pellets(width, height, mapcontent, pellets_group):
    """Nur Pellets aus dem Map-Inhalt laden"""
    
    for y in range(height):
        for x in range(width):
            block = mapcontent[y][x]

            if block == '.':
                pellets_group.add(sprites.NormalPellet((x * const.UNIT, y * const.UNIT)))
            elif block == ':':
                pellets_group.add(sprites.PowerPellet((x * const.UNIT, y * const.UNIT)))
