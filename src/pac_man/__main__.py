from . import const
from . import sprites
from . import gamemap

from importlib.resources import as_file, files

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

# Statische Sprites und Rects der Kreuzungen aus dem Map-Inhalt laden
walls_group = pygame.sprite.Group()
pellets_group = pygame.sprite.Group()
power_pellets_group = pygame.sprite.Group()
crossing_rects: list[pygame.Rect] = []

gamemap.load_all(MAPWIDTH, MAPHEIGHT, mapcontent, walls_group, pellets_group, power_pellets_group, crossing_rects)

# Bewegliche Sprites laden
entities_group = pygame.sprite.Group()

pacman = sprites.Pacman(const.PACMAN_START_POS)
pacman_direction = sprites.PacmanDirection()  # Pfeil, der die ausgewählte Richtung für Pacman anzeigt
pacman_direction.update(pacman=pacman)

ghosts_group = pygame.sprite.Group()
ghost1 = sprites.Ghost1(const.GHOST1_START_POS)
ghost2 = sprites.Ghost2(const.GHOST2_START_POS)
ghost3 = sprites.Ghost3(const.GHOST3_START_POS)
ghost4 = sprites.Ghost4(const.GHOST4_START_POS)
ghosts_group.add(ghost1, ghost2, ghost3, ghost4)

entities_group.add(pacman, pacman_direction, ghost1, ghost2, ghost3, ghost4)

# Textur für Pac-Mans Leben
with as_file(files("pac_man").joinpath(f"resources/pacman/1.png")) as path:
    life_texture = pygame.transform.scale(pygame.image.load(path), (const.UNIT*2, const.UNIT*2))

# Fenster erstellen
SCREEN = pygame.display.set_mode((WINWIDTHPX, WINHEIGHTPX))
pygame.display.set_caption("Pac-Man")

# Highscore auslesen
if const.HIGHSCORE_PATH.exists():
    with open(const.HIGHSCORE_PATH) as file:
        highscore = int(file.read())
else:
    highscore = 0

# Daten während des Spiels
game_data = {
    "score": 0,
    "level": 1,
    "lives": 2,
    "ghost_mode": const.GhostMode.SCATTER,
    "ghost_mode_cycle": 1,
    "frightened_ghosts_eaten": 0,
}

phase_timer = const.READY_INTERVAL
ghost_mode_timer = const.GHOST_MODE_INTERVAL(game_data)

# Main-Loop
clock = pygame.time.Clock()
phase = const.Phase.READY

def reset_entity_sprites(dt):
    ghost1.set_pos(const.GHOST1_START_POS)
    ghost2.set_pos(const.GHOST2_START_POS)
    ghost3.set_pos(const.GHOST3_START_POS)
    ghost4.set_pos(const.GHOST4_START_POS)

    ghost1.try_direction = 'r'
    ghost2.start, ghost3.start, ghost4.start = True, True, True

    for ghost in ghosts_group:
        ghost.frightened = False
        ghost.update_image(pacman.rect.center[0])

    pacman.set_pos(const.PACMAN_START_POS)
    pacman.try_direction = 'l'
    pacman.curr_direction = 'l'
    pacman.texture_num = 1

    pacman.update(dt=dt, move=False)
    pacman_direction.update(pacman=pacman)


def normal_phase(dt):
    global phase_timer, ghost_mode_timer, phase, running

    # Pellets neu laden, wenn alle gegessen wurden
    if len(pellets_group) == 0:
        phase_timer = const.ALL_PELLETS_INTERVAL
        phase = const.Phase.ALL_PELLETS
    
    for power_pellet in power_pellets_group:
        if pacman.hitbox.colliderect(power_pellet.rect):
            game_data["frightened_ghosts_eaten"] = 0
            for ghost in ghosts_group:
                ghost.frightened = True
                ghost.frightened_timer = 0.0
    
    for ghost in ghosts_group:
        if pacman.hitbox.colliderect(ghost.hitbox):
            if ghost.frightened:
                game_data["frightened_ghosts_eaten"] += 1
                game_data["score"] += 100 * 2 ** game_data["frightened_ghosts_eaten"]
                ghost.reset_frightened()
            else:
                if game_data["lives"] > 0:
                    phase_timer = const.DEATH_INTERVAL
                    phase = const.Phase.DEATH
                else:
                    if game_data["score"] > highscore:
                        with open(const.HIGHSCORE_PATH, "w") as file:
                            file.write(str(game_data["score"]))

                    phase_timer = const.DEATH_INTERVAL
                    phase = const.Phase.ABS_DEATH
    
    no_frightened = True
    for ghost in ghosts_group:
        if ghost.frightened:
            no_frightened = False
            break
    if no_frightened:
        game_data["frightened_ghosts_eaten"] = 0
    
    if ghost_mode_timer <= 0.0:
        match game_data["ghost_mode"]:
            case const.GhostMode.SCATTER:
                game_data["ghost_mode"] = const.GhostMode.CHASE
            case const.GhostMode.CHASE:
                game_data["ghost_mode"] = const.GhostMode.SCATTER
                game_data["ghost_mode_cycle"] += 1
        
        ghost_mode_timer = const.GHOST_MODE_INTERVAL(game_data)

    ghost_mode_timer -= dt
   
    # Pellets updaten: Löschen sich, wenn von Pac-Man berührt
    pellets_group.update(pacman=pacman, game_data=game_data, dt=dt, pellets_group=pellets_group)
    # Bewegliche Sprites updaten: KI der Ghosts usw...
    entities_group.update(windowsize=(WINWIDTHPX, WINHEIGHTPX),
                          dt=dt, walls_group=walls_group,
                          pacman=pacman, pacman_direction=pacman_direction,
                          ghost1=ghost1, num_pellets=len(pellets_group),
                          crossing_rects=crossing_rects, game_data=game_data)


def ready_phase(dt):
    global phase_timer, phase

    score_text = font.render(f"READY!", True, (255, 255, 0))
    SCREEN.blit(score_text, score_text.get_rect(center=(WINWIDTHPX/2, 18*const.UNIT)))

    if phase_timer <= 0.0:
        phase = const.Phase.NORMAL
        return

    phase_timer -= dt


def death_phase(dt):
    global phase_timer, phase

    if phase_timer <= 0.0:
        reset_entity_sprites(dt)
        game_data["lives"] -= 1
        for ghost in ghosts_group:
            ghost.frightened = False
            ghost.update_image(pacman.rect.center[0])
        phase_timer = const.READY_INTERVAL
        phase = const.Phase.READY
        return
    
    phase_timer -= dt


def abs_death_phase(dt):
    global phase_timer, phase

    if phase_timer <= 0.0:
        reset_entity_sprites(dt)
        game_data["lives"] -= 1
        phase = const.Phase.EXIT
        return
    
    phase_timer -= dt


def all_pellets_phase(dt):
    global phase_timer, phase

    if phase_timer <= 0.0:
        game_data["level"] += 1
        game_data["ghost_mode"] = const.GhostMode.SCATTER
        game_data["ghost_mode_cycle"] = 1
        reset_entity_sprites(dt)
        gamemap.load_pellets(MAPWIDTH, MAPHEIGHT, mapcontent, pellets_group, power_pellets_group)
        phase_timer = const.READY_INTERVAL
        phase = const.Phase.READY
        return

    phase_timer -= dt


while phase != const.Phase.EXIT:
    # Zeitlicher Abstand zwischen Frames
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        # Spiel beenden
        if event.type == pygame.QUIT:
            phase = const.Phase.EXIT
        
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
    
    # Schwarzer Hintergrund
    SCREEN.fill((0, 0, 0))
    
    match phase:
        case const.Phase.NORMAL: normal_phase(dt)
        case const.Phase.READY: ready_phase(dt)
        case const.Phase.DEATH: death_phase(dt)
        case const.Phase.ABS_DEATH: abs_death_phase(dt)
        case const.Phase.ALL_PELLETS: all_pellets_phase(dt)

    # Aktuelle Punktzahl und Highscore
    score_text = font.render(f"SCORE {game_data['score']}", True, (255, 255, 255))
    SCREEN.blit(score_text, score_text.get_rect(topleft=(WINWIDTHPX*0.2, (WINHEIGHT-4)*const.UNIT)))

    highscore_text = font.render(f"HIGHSCORE {highscore}", True, (255, 255, 255))
    SCREEN.blit(highscore_text, highscore_text.get_rect(topleft=(WINWIDTHPX*0.2, (WINHEIGHT-2)*const.UNIT)))

    level_text = font.render(f"LEVEL {game_data['level']}", True, (255, 255, 255))
    SCREEN.blit(level_text, level_text.get_rect(topleft=(WINWIDTHPX*0.7, (WINHEIGHT-4)*const.UNIT)))

    # Pac-Mans Leben
    for i in range(game_data["lives"]):
        SCREEN.blit(life_texture, pygame.Rect(i * const.UNIT*2, (WINHEIGHT-3)*const.UNIT, const.UNIT*2, const.UNIT*2))

    # Alle Sprites zeichnen
    walls_group.draw(SCREEN)
    pellets_group.draw(SCREEN)
    entities_group.draw(SCREEN)

    pygame.display.flip()
