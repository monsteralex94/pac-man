from . import const
from . import sprites
from . import gamemap

import pygame
pygame.init()

# Map auslesen
with open(f"{const.CWD}/map.txt") as mapfile:
    mapcontent = mapfile.read().split('\n')

# Fenstergröße anhand der Größe der Map bestimmen (in Blöcken und Pixeln)
WIDTH, HEIGHT = len(mapcontent[0]), len(mapcontent)
PXWIDTH, PXHEIGHT = WIDTH * const.UNIT, HEIGHT * const.UNIT

# Statische Sprites aus dem Map-Inhalt laden
blocks_group = pygame.sprite.Group()
pellets_group = pygame.sprite.Group()

gamemap.load_all(WIDTH, HEIGHT, mapcontent, blocks_group, pellets_group)

# Bewegliche Sprites laden
entities_group = pygame.sprite.Group()

pacman = sprites.Pacman((const.UNIT*14, const.UNIT*23))
pacman_direction = sprites.PacmanDirection()  # Pfeil, der die ausgewählte Richtung für Pacman anzeigt
# ghost1 = sprites.Ghost((const.UNIT*14, const.UNIT))
entities_group.add(pacman, pacman_direction)

# Fenster erstellen
SCREEN = pygame.display.set_mode((PXWIDTH, PXHEIGHT))
pygame.display.set_caption("Pac-Man")

# Main-Loop
clock = pygame.time.Clock()
running = True

while running:
    # Zeitlicher Abstand zwischen Frames
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        # Spiel beenden
        if event.type == pygame.QUIT:
            running = False
        
        # Tasteneingabe des Benutzers lesen
        if event.type == pygame.KEYDOWN:
            match event.key:
                case pygame.K_RIGHT:
                    pacman.try_direction = 'r'
                case pygame.K_UP:
                    pacman.try_direction = 'u'
                case pygame.K_LEFT:
                    pacman.try_direction = 'l'
                case pygame.K_DOWN:
                    pacman.try_direction = 'd'
    
    # Pellets neu laden, wenn alle gegessen wurden
    if len(pellets_group) == 0:
        gamemap.load_pellets(WIDTH, HEIGHT, mapcontent, pellets_group)
    
    # Schwarzer Hintergrund
    SCREEN.fill((0, 0, 0))

    # Pellets updaten: Löschen sich, wenn von Pac-Man berührt
    pellets_group.update(pacman)
    # Bewegliche Sprites updaten: KI der Ghosts usw...
    entities_group.update(windowsize=(PXWIDTH, PXHEIGHT),
                          dt=dt, blocks_group=blocks_group,
                          pacman=pacman, pacman_direction=pacman_direction)
    
    # Alle Sprites zeichnen
    blocks_group.draw(SCREEN)
    pellets_group.draw(SCREEN)
    entities_group.draw(SCREEN)

    pygame.display.flip()
