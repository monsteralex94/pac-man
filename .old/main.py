for y in range(HEIGHT):
    for x in range(WIDTH):
        block = mapcontent[y][x]

        if block == '#':
            bl = sprites.Block((x * const.UNIT, y * const.UNIT), 0, "blue")
            blocks_group.add(bl)
            mapblocks[y][x] = True