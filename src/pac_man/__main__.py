from . import const
from . import sprites
from . import gamemap

from importlib.resources import files

import pygame
pygame.init()
pygame.font.init()

font = pygame.font.SysFont("Liberation Mono", const.UNIT * 2)

# Map auslesen
mapcontent = files("pac_man").joinpath("resources/map.txt").read_text().split("\n")

# Fenstergröße anhand der Größe der Map bestimmen (in Blöcken und Pixeln)
MAPWIDTH,   MAPHEIGHT   = len(mapcontent[0]), len(mapcontent)
WINWIDTH,   WINHEIGHT   = MAPWIDTH, MAPHEIGHT + 4
WINWIDTHPX, WINHEIGHTPX = WINWIDTH * const.UNIT, WINHEIGHT * const.UNIT

# Statische Sprites aus dem Map-Inhalt laden
walls_group = pygame.sprite.Group()
pellets_group = pygame.sprite.Group()

gamemap.load_all(MAPWIDTH, MAPHEIGHT, mapcontent, walls_group, pellets_group)

# Bewegliche Sprites laden
entities_group = pygame.sprite.Group()

pacman = sprites.Pacman((const.UNIT*14, const.UNIT*23))
pacman_direction = sprites.PacmanDirection()  # Pfeil, der die ausgewählte Richtung für Pacman anzeigt

ghosts_group = pygame.sprite.Group()
ghost1 = sprites.Ghost1((const.UNIT*15, const.UNIT*14))
ghost2 = sprites.Ghost2((const.UNIT*12, const.UNIT*14))
ghosts_group.add(ghost1, ghost2)

entities_group.add(pacman, pacman_direction, ghost1, ghost2)

# Fenster erstellen
SCREEN = pygame.display.set_mode((WINWIDTHPX, WINHEIGHTPX))
pygame.display.set_caption("Pac-Man")

game_data = {
    "score": 0
}

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
        gamemap.load_pellets(MAPWIDTH, MAPHEIGHT, mapcontent, pellets_group)
    
    for ghost in ghosts_group:
        if pacman.hitbox.colliderect(ghost.hitbox):
            running = False
    
    # Schwarzer Hintergrund
    SCREEN.fill((0, 0, 0))

    score_text = font.render(f"Score: {game_data['score']}", True, (255, 255, 255))
    SCREEN.blit(score_text, score_text.get_rect(center=(WINWIDTHPX/2, (WINHEIGHT-2)*const.UNIT)))

    # Pellets updaten: Löschen sich, wenn von Pac-Man berührt
    pellets_group.update(pacman=pacman, game_data=game_data, dt=dt, pellets_group=pellets_group)
    # Bewegliche Sprites updaten: KI der Ghosts usw...
    entities_group.update(windowsize=(WINWIDTHPX, WINHEIGHTPX),
                          dt=dt, walls_group=walls_group,
                          pacman=pacman, pacman_direction=pacman_direction,
                          game_data=game_data)
    
    # Alle Sprites zeichnen
    walls_group.draw(SCREEN)
    pellets_group.draw(SCREEN)
    entities_group.draw(SCREEN)

    pygame.display.flip()
