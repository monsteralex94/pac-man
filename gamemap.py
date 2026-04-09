import const
import sprites

def load_all(height, width, mapcontent, blocks_group, pellets_group):
    """Alle statischen Sprites aus dem Map-Inhalt laden"""

    for y in range(height):
        for x in range(width):
            block = mapcontent[y][x]

            if block == '#':
                bl = sprites.Block((x * const.UNIT, y * const.UNIT))
                blocks_group.add(bl)
            elif block == '.':
                p = sprites.NormalPellet((x * const.UNIT, y * const.UNIT))
                pellets_group.add(p)
            elif block == ':':
                p = sprites.PowerPellet((x * const.UNIT, y * const.UNIT))
                pellets_group.add(p)


def load_pellets(height, width, mapcontent, pellets_group):
    """Nur Pellets aus dem Map-Inhalt laden"""
    
    for y in range(height):
        for x in range(width):
            block = mapcontent[y][x]

            if block == '.':
                p = sprites.NormalPellet((x * const.UNIT, y * const.UNIT))
                pellets_group.add(p)
            elif block == ':':
                p = sprites.PowerPellet((x * const.UNIT, y * const.UNIT))
                pellets_group.add(p)
