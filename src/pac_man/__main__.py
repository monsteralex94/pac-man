from .const import *
from . import sprites
from . import gamemap

from importlib.resources import as_file, files

import pygame
pygame.init()
pygame.font.init()

font = pygame.font.SysFont("Liberation Mono", int(UNIT*1.5))

# Map auslesen
mapcontent = files("pac_man").joinpath("resources/map.txt").read_text().split("\n")

# Fenstergröße anhand der Größe der Map bestimmen (in Blöcken und Pixeln)
MAPWIDTH,   MAPHEIGHT   = len(mapcontent[0]), len(mapcontent)
WINWIDTH,   WINHEIGHT   = MAPWIDTH, MAPHEIGHT + 6
WINWIDTHPX, WINHEIGHTPX = WINWIDTH * UNIT, WINHEIGHT * UNIT

# Statische Sprites und Rects der Kreuzungen aus dem Map-Inhalt laden
walls_group = pygame.sprite.Group()
pellets_group = pygame.sprite.Group()
power_pellets_group = pygame.sprite.Group()
fruits_group = pygame.sprite.Group()
powerups_group = pygame.sprite.Group()
crossing_rects: list[pygame.Rect] = []

gamemap.load_all(MAPWIDTH, MAPHEIGHT, mapcontent, walls_group, pellets_group,
                 power_pellets_group, fruits_group, powerups_group, crossing_rects)

# Bewegliche Sprites laden
entities_group = pygame.sprite.Group()

pacman = sprites.Pacman(PACMAN_START_POS)
pacman_direction = sprites.PacmanDirection()  # Pfeil, der die ausgewählte Richtung für Pacman anzeigt
pacman_gun = sprites.PacmanGun()  # Pacmans Pistole, mit denen er Geister zum Regenerieren zwingt

ghosts_group = pygame.sprite.Group()
ghost1 = sprites.Ghost1(GHOST1_START_POS, (WINWIDTHPX, 0))
ghost2 = sprites.Ghost2(GHOST2_START_POS, (0, 0))
ghost3 = sprites.Ghost3(GHOST3_START_POS, (WINWIDTHPX, WINHEIGHTPX))
ghost4 = sprites.Ghost4(GHOST4_START_POS, (0, WINHEIGHTPX))

ghosts_group.add(ghost1, ghost2, ghost3, ghost4)
entities_group.add(pacman, pacman_direction, pacman_gun, ghost1, ghost2, ghost3, ghost4)

# Textur für Pac-Mans Leben / Shadow Dashes / Kugeln
with as_file(files("pac_man").joinpath(f"resources/powerups/extralife.png")) as path:
    life_texture = pygame.transform.scale(pygame.image.load(path), (UNIT*2, UNIT*2))

with as_file(files("pac_man").joinpath(f"resources/powerups/shadowdash.png")) as path:
    sd_texture = pygame.transform.scale(pygame.image.load(path), (UNIT*2, UNIT*2))

with as_file(files("pac_man").joinpath(f"resources/powerups/dart.png")) as path:
    dart_texture = pygame.transform.scale(pygame.image.load(path), (UNIT*2, UNIT*2))

# Fenster erstellen
SCREEN = pygame.display.set_mode((WINWIDTHPX, WINHEIGHTPX))
pygame.display.set_caption("Pac-Man")

# Highscore auslesen
if HIGHSCORE_PATH.exists():
    with open(HIGHSCORE_PATH) as file:
        highscore = int(file.read())
else:
    highscore = float('-inf')

# Daten während des Spiels
game_data = {}

def reset_game_data():
    global game_data

    game_data = {
        "phase": Phase.READY,
        "score": 0,
        "level": 1,
        "lives": 3,
        "ghost_mode": GhostMode.SCATTER,
        "ghost_mode_cycle": 1,
        "frightened_ghosts_eaten": 0,
        "shadow_dashes_left": 0,
        "darts_left": 0,
    }

reset_game_data()

phase_timer = READY_INTERVAL
ghost_mode_timer = GHOST_MODE_INTERVAL(game_data)

# Main-Loop
clock = pygame.time.Clock()

def reset_entity_sprites():
    ghost1.set_pos(GHOST1_START_POS)
    ghost2.set_pos(GHOST2_START_POS)
    ghost3.set_pos(GHOST3_START_POS)
    ghost4.set_pos(GHOST4_START_POS)

    ghost1.try_direction = 'r'
    ghost2.start, ghost3.start, ghost4.start = True, True, True

    for ghost in ghosts_group:
        ghost.fright_stage = GhostFrightStage.LEAVING_ARENA
        ghost.update_image(pacman.rect.center[0])

    pacman.set_pos(PACMAN_START_POS)
    pacman.try_direction = 'l'
    pacman.curr_direction = 'l'
    pacman.texture_num = 1

    pacman.update_image()


def reset_powerups_and_fruits():
    for fruit in fruits_group:
        fruit.active = False
        fruit.timer = 0.0
    
    for powerup in powerups_group:
        powerup.active = False
        powerup.timer = 0.0


def normal_phase(dt):
    global phase_timer, ghost_mode_timer, highscore, running

    # Pellets neu laden, wenn alle gegessen wurden
    if len(pellets_group) == 0:
        phase_timer = ALL_PELLETS_INTERVAL
        game_data["phase"] = Phase.ALL_PELLETS
    
    for power_pellet in power_pellets_group:
        if pacman.hitbox.colliderect(power_pellet.rect):
            for ghost in ghosts_group:
                ghost.fright_stage = GhostFrightStage.FRIGHTENED
                ghost.frightened_timer = 0.0
            game_data["frightened_ghosts_eaten"] = 0
    
    for fruit in fruits_group:
        if len(pellets_group) in (188, 88):
            fruit.active = True
            fruit.timer = FRUIT_INTERVAL
        
        if pacman.hitbox.colliderect(fruit.rect) and fruit.active:
            game_data["score"] += fruit.points
            fruit.active = False
    
    for ghost in ghosts_group:
        if pacman.hitbox.colliderect(ghost.hitbox):
            if ghost.fright_stage == GhostFrightStage.FRIGHTENED:
                game_data["frightened_ghosts_eaten"] += 1
                game_data["score"] += 100 * 2 ** game_data["frightened_ghosts_eaten"]
                ghost.reset()
            else:
                if game_data["lives"] > 0:
                    phase_timer = DEATH_INTERVAL
                    game_data["phase"] = Phase.DEATH
                else:
                    if game_data["score"] > highscore:
                        highscore = game_data["score"]
                        with open(HIGHSCORE_PATH, "w") as file:
                            file.write(str(highscore))

                    phase_timer = ABS_DEATH_INTERVAL
                    game_data["phase"] = Phase.ABS_DEATH
    
    no_frightened = True
    for ghost in ghosts_group:
        if ghost.fright_stage == GhostFrightStage.FRIGHTENED:
            no_frightened = False
            break
    if no_frightened:
        game_data["frightened_ghosts_eaten"] = 0
    
    if ghost_mode_timer <= 0.0:
        match game_data["ghost_mode"]:
            case GhostMode.SCATTER:
                game_data["ghost_mode"] = GhostMode.CHASE
            case GhostMode.CHASE:
                game_data["ghost_mode"] = GhostMode.SCATTER
                game_data["ghost_mode_cycle"] += 1
        
        ghost_mode_timer = GHOST_MODE_INTERVAL(game_data)

    ghost_mode_timer -= dt
   
    # Pellets updaten: Löschen sich, wenn von Pac-Man berührt
    pellets_group.update(pacman=pacman, game_data=game_data, dt=dt, pellets_group=pellets_group)
    # Früchte updaten: Art und Punktzahl
    fruits_group.update(game_data=game_data, dt=dt)
    # Power-Ups updaten
    powerups_group.update(pacman=pacman, game_data=game_data, dt=dt)
    # Bewegliche Sprites updaten: KI der Ghosts usw...
    entities_group.update(windowsize=(WINWIDTHPX, WINHEIGHTPX),
                          dt=dt, walls_group=walls_group,
                          pacman=pacman, pacman_direction=pacman_direction,
                          ghost1=ghost1, num_pellets=len(pellets_group),
                          crossing_rects=crossing_rects, game_data=game_data)


def ready_phase(dt):
    global phase_timer

    score_text = font.render(f"READY!", True, (255, 255, 0))
    SCREEN.blit(score_text, score_text.get_rect(center=(WINWIDTHPX/2, 18*UNIT)))

    if phase_timer <= 0.0:
        game_data["phase"] = Phase.NORMAL
        return

    phase_timer -= dt


def death_phase(dt):
    global phase_timer

    if phase_timer <= 0.0:
        reset_entity_sprites()
        game_data["lives"] -= 1
        for ghost in ghosts_group:
            ghost.fright_stage = GhostFrightStage.LEAVING_ARENA
            ghost.update_image(pacman.rect.center[0])
        phase_timer = READY_INTERVAL
        game_data["phase"] = Phase.READY
        return
    
    phase_timer -= dt


def abs_death_phase(dt):
    global ghost_mode_timer, phase_timer, game_data

    score_text = font.render(f"GAME OVER", True, (255, 0, 0))
    SCREEN.blit(score_text, score_text.get_rect(center=(WINWIDTHPX/2, 18*UNIT)))

    if phase_timer <= 0.0:
        reset_game_data()
        reset_entity_sprites()
        reset_powerups_and_fruits()
        gamemap.load_pellets(MAPWIDTH, MAPHEIGHT, mapcontent, pellets_group, power_pellets_group)
        ghost_mode_timer = GHOST_MODE_INTERVAL(game_data)
        phase_timer = READY_INTERVAL
        game_data["phase"] = Phase.READY
        return
    
    phase_timer -= dt


def all_pellets_phase(dt):
    global phase_timer

    if phase_timer <= 0.0:
        game_data["level"] += 1
        game_data["ghost_mode"] = GhostMode.SCATTER
        game_data["ghost_mode_cycle"] = 1
        reset_entity_sprites()
        gamemap.load_pellets(MAPWIDTH, MAPHEIGHT, mapcontent, pellets_group, power_pellets_group)
        phase_timer = READY_INTERVAL
        game_data["phase"] = Phase.READY
        return

    phase_timer -= dt


while game_data["phase"] != Phase.EXIT:
    # Zeitlicher Abstand zwischen Frames
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        # Spiel beenden
        if event.type == pygame.QUIT:
            game_data["phase"] = Phase.EXIT
        
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
                case pygame.K_c:
                    if game_data["shadow_dashes_left"] > 0 and game_data["phase"] == Phase.NORMAL:
                        pacman.shadow_dash(game_data, (WINWIDTHPX, WINHEIGHTPX), walls_group)
                case pygame.K_x:
                    if game_data["darts_left"] > 0 and game_data["phase"] == Phase.NORMAL:
                        pacman.shoot(game_data, ghosts_group)
                        pacman_gun.shooting = True
                        pacman_gun.timer = SHOOT_INTERVAL

    # Schwarzer Hintergrund
    SCREEN.fill((0, 0, 0))

    match game_data["phase"]:
        case Phase.NORMAL: normal_phase(dt)
        case Phase.READY: ready_phase(dt)
        case Phase.DEATH: death_phase(dt)
        case Phase.ABS_DEATH: abs_death_phase(dt)
        case Phase.ALL_PELLETS: all_pellets_phase(dt)
    
    # Alle Sprites zeichnen
    walls_group.draw(SCREEN)
    pellets_group.draw(SCREEN)
    fruits_group.draw(SCREEN)
    powerups_group.draw(SCREEN)
    entities_group.draw(SCREEN)

    # Pac-Mans Leben
    SCREEN.blit(life_texture, pygame.Rect(11 * UNIT*2, (WINHEIGHT-6)*UNIT, UNIT*2, UNIT*2))
    lives_num = font.render(str(game_data["lives"]), True, (255, 255, 255))
    SCREEN.blit(lives_num, lives_num.get_rect(topleft=(25 * UNIT, (WINHEIGHT-6)*UNIT)))
    
    # Pac-Mans übrige Shadow Dashes
    SCREEN.blit(sd_texture, pygame.Rect(11 * UNIT*2, (WINHEIGHT-4)*UNIT, UNIT*2, UNIT*2))
    sd_num = font.render(str(game_data["shadow_dashes_left"]), True, (255, 255, 255))
    SCREEN.blit(sd_num, sd_num.get_rect(topleft=(25 * UNIT, (WINHEIGHT-4)*UNIT)))

    # Pac-Mans übrige Kugeln
    SCREEN.blit(dart_texture, pygame.Rect(11 * UNIT*2, (WINHEIGHT-2)*UNIT, UNIT*2, UNIT*2))
    darts_num = font.render(str(game_data["darts_left"]), True, (255, 255, 255))
    SCREEN.blit(darts_num, darts_num.get_rect(topleft=(25 * UNIT, (WINHEIGHT-2)*UNIT)))

    # Aktuelle Punktzahl, Highscore und Level
    score_text = font.render("SCORE", True, (255, 255, 255))
    SCREEN.blit(score_text, score_text.get_rect(topleft=(WINWIDTHPX*0.01, (WINHEIGHT-5)*UNIT)))

    score_num = font.render(str(game_data["score"]), True, (255, 255, 255))
    SCREEN.blit(score_num, score_num.get_rect(topleft=(WINWIDTHPX*0.01, (WINHEIGHT-3)*UNIT)))

    highscore_text = font.render("HIGHSCORE", True, (255, 255, 255))
    SCREEN.blit(highscore_text, highscore_text.get_rect(topleft=(WINWIDTHPX*0.2, (WINHEIGHT-5)*UNIT)))

    highscore_num = font.render(str(highscore) if highscore != float('inf') else '-', True, (255, 255, 255))
    SCREEN.blit(highscore_num, highscore_num.get_rect(topleft=(WINWIDTHPX*0.2, (WINHEIGHT-3)*UNIT)))

    level_text = font.render("LEVEL", True, (255, 255, 255))
    SCREEN.blit(level_text, level_text.get_rect(topleft=(WINWIDTHPX*0.5, (WINHEIGHT-5)*UNIT)))

    level_num = font.render(str(game_data['level']), True, (255, 255, 255))
    SCREEN.blit(level_num, level_num.get_rect(topleft=(WINWIDTHPX*0.5, (WINHEIGHT-3)*UNIT)))

    pygame.display.flip()
