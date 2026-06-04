from . import const
import pygame
from typing import Optional
from importlib.resources import files, as_file


dmap = {
    'u': (0, -1),
    'l': (-1, 0),
    'd': (0, 1),
    'r': (1, 0),
}

opp_d = {
    'u': 'd',
    'l': 'r',
    'd': 'u',
    'r': 'l'
}


def collision_with_wall_rect(rect, walls_group, ignore_ghost_walls) -> Optional[pygame.Rect]:
    for wall in walls_group:
        if wall.rect.colliderect(rect) and not (wall.ghost and ignore_ghost_walls):
            return wall.rect

    return None


def collision_with_wall_point(point, walls_group, ignore_ghost_walls) -> Optional[pygame.Rect]:
    for wall in walls_group:
        if wall.rect.collidepoint(point) and not (wall.ghost and ignore_ghost_walls):
            return wall.rect

    return None


def mirror_point(px, pa):
    return (2*pa[0] - px[0], 2*pa[1] - px[1])


class StaticSprite(pygame.sprite.Sprite):
    """Elternklasse für statische Sprites"""

    def __init__(self, position: tuple[int, int], texture: str, scale: tuple[int, int], rotate: float):
        super().__init__()
        with as_file(files("pac_man").joinpath(f"resources/{texture}.png")) as path:
            self.image = pygame.image.load(path)
        self.image = pygame.transform.scale(self.image, scale)
        self.image = pygame.transform.rotate(self.image, rotate * 90)
        self.rect = self.image.get_rect(topleft=position)


class Wall(StaticSprite):
    """Klasse für Wände"""

    def __init__(self, position: tuple[int, int], ghost: bool=False) -> None:
        super().__init__(position, "walls/1" if ghost else "walls/0", (const.UNIT, const.UNIT), 0)
        self.ghost = ghost


class EntitySprite(pygame.sprite.Sprite):
    """Elternklasse für bewegliche Sprites"""

    def __init__(self, start_position) -> None:
        super().__init__()

        # Aktuelles Frame
        self.image = pygame.Surface((const.UNIT * 2, const.UNIT * 2))

        # Rect (Position und Größe) des Sprites als Ganzzahlen für das Zeichnen auf den Bildschirm
        self.rect = self.image.get_rect(topleft=start_position)
        self.hitbox = self.image.get_rect(topleft=start_position)

        self.hitbox.width, self.hitbox.height = const.UNIT, const.UNIT

        # Tatsächliche Position des Sprites als Gleitkommazahlen (linke obere Ecke)
        self.float_pos = pygame.Vector2(start_position)

        # Richtung, in die Pac-Man gerade geht
        self.curr_direction = 'l'
        # Richtung, in die Pac-Man gehen will (wegen Benutzereingabe)
        self.try_direction = 'l'


    def movement(self, speed, windowsize, walls_group, dt, ignore_ghost_walls=False) -> None:
        """Kontrolliert die Steuerung mit curr_direction und try_direction"""

        ########### BEWEGUNG
        # Zurückzulegende Strecke in jede Richtung für den aktuellen Frame (x- und y-Komponenten)

        # Bewegung in Richtung curr_direction (aktuelle Richtung) und
        # try_direction (ab der nächsten Kreuzung)
        dx, dy = dmap[self.curr_direction][0] * speed * dt, dmap[self.curr_direction][1] * speed * dt
        try_dx, try_dy = dmap[self.try_direction][0] * speed * dt, dmap[self.try_direction][1] * speed * dt

        ########### Anpassen von dx und dy anhand der Wände auf der Map

        # Prüfen, ob Sprite sich noch im Screen befindet
        if self.rect.right < windowsize[0] and self.rect.left > 0:

            # Nächste Bewegung in x-Richtung?
            if self.try_direction in ('l', 'r'):

                # Prüfen aller Positionsänderungen in y-Richtung von 0 bis dy (egal ob positiv oder negativ)
                for y in range(min(0, int(dy)), max(0, int(dy))+1):

                    # Wenn Pac-Man bei der aktuellen Positionsänderung keine Wand berührt,
                    # werden dx und dy angepasst
                    if not collision_with_wall_rect(self.rect.move(try_dx, y), walls_group, ignore_ghost_walls):
                        self.curr_direction = self.try_direction
                        dx = try_dx
                        dy = y
            
            # Genauso wie davor, nur mit x und y vertauscht
            elif self.try_direction in ('u', 'd'):
                for x in range(min(0, int(dx)), max(0, int(dx))+1):
                    if not collision_with_wall_rect(self.rect.move(x, try_dy), walls_group, ignore_ghost_walls):
                        self.curr_direction = self.try_direction
                        dy = try_dy
                        dx = x

        ########### Ausführen der gewünschten Bewegung mit dx und dy

        # Bewegung in x-Richtung
        self.float_pos.x += dx    # intern als Gleitkommazahl (tatsächliche Position)
        self.rect.left = int(self.float_pos.x)   # Als ganze Zahl (für das Zeichnen)

        # Anpassung von Abweichungen
        wall_rect = collision_with_wall_rect(self.rect, walls_group, ignore_ghost_walls)
        if wall_rect:
            if dx > 0:
                self.rect.right = wall_rect.left
            elif dx < 0:
                self.rect.left = wall_rect.right
            self.float_pos.x = self.rect.left

        # Bewegung in y-Richtung
        self.float_pos.y += dy    # intern als Gleitkommazahl (tatsächliche Position)
        self.rect.top = int(self.float_pos.y)   # Als ganze Zahl (für das Zeichnen)

        # Anpassung von Abweichungen
        wall_rect = collision_with_wall_rect(self.rect, walls_group, ignore_ghost_walls)
        if wall_rect:
            if dy > 0:
                self.rect.bottom = wall_rect.top
            elif dy < 0:
                self.rect.top = wall_rect.bottom
            self.float_pos.y = self.rect.top
    
        if self.float_pos.x > windowsize[0]:
            self.float_pos.x = -self.rect.width 
        if self.float_pos.x < -self.rect.width:
            self.float_pos.x = windowsize[0]
        
        # Neue, angepasste Position
        self.rect.topleft = (int(self.float_pos.x), int(self.float_pos.y))
        self.hitbox.center = self.rect.center
    
    def set_pos(self, pos):
        self.rect.left, self.rect.top = pos
        self.hitbox.left, self.hitbox.top = pos
        self.float_pos.x, self.float_pos.y = pos

    def update(self, **kwargs):
        """Update-Funktion des Entity Sprites"""
        self.hitbox.center = self.rect.center


class Pacman(EntitySprite):
    "Klasse für Pac-Man"

    def __init__(self, start_position) -> None:
        super().__init__(start_position)

        self.start_position = start_position

        # Frames für die Animation
        with as_file(files("pac_man").joinpath(f"resources/pacman/0.png")) as path0:
            with as_file(files("pac_man").joinpath(f"resources/pacman/1.png")) as path1:
                frame0 = pygame.transform.scale(pygame.image.load(path0), (const.UNIT*2, const.UNIT*2))
                frame1 = pygame.transform.scale(pygame.image.load(path1), (const.UNIT*2, const.UNIT*2))

        # Rotationswinkel in Grad für jede Richtung
        rotations = {'r': 0, 'u': 90, 'l': 180, 'd': 270}

        # Erstellt Texturen für jede Animationsphase und Richtung
        self.frames = [
            {d: pygame.transform.rotate(frame, angle) for d, angle in rotations.items()}
            for frame in (frame0, frame1)
        ]

        self.image = self.frames[0]['l']

        # Timer und Texturzahl für Animation
        self.texture_timer = 0
        self.texture_num = 0
    
    def update(self, **kwargs):
        ########### ANIMATION
        # Wenn der Timer überschritten wird, wechselt das Frame der Animation
        # und der Timer wird zurückgesetzt
        if self.texture_timer > const.PACMAN_TEXTURE_SWITCH_INTERVAL:
            self.texture_timer = 0
            self.texture_num = int(not self.texture_num)

        # Auswählen der Textur innerhalb der Animation und Aktualisierung des Timers
        self.image = self.frames[self.texture_num][self.curr_direction]
        self.texture_timer += kwargs["dt"]

        ########### BEWEGUNG
        if "move" not in kwargs or kwargs["move"]:
            self.movement(const.SPEED(kwargs["game_data"], True), kwargs["windowsize"], kwargs["walls_group"], kwargs["dt"])


class Ghost(EntitySprite):
    "Klasse für Geist"

    def __init__(self, start_position) -> None:
        super().__init__(start_position)

        self.is_frightened = False
        self.frightened_timer = 0.0
        self.start = True

        self.frames = (())
    
    def load_frames(self, color):
        with as_file(files("pac_man").joinpath(f"resources/ghosts/{color}.png")) as path:
            orig_image = pygame.transform.scale(pygame.image.load(path), (const.UNIT*2, const.UNIT*2))
        
        with as_file(files("pac_man").joinpath(f"resources/ghosts/frightened.png")) as path:
            image_frightened = pygame.transform.scale(pygame.image.load(path), (const.UNIT*2, const.UNIT*2))
        
        self.frames = (orig_image, pygame.transform.flip(orig_image, True, False)), \
            (image_frightened, image_frightened)

        self.image = self.frames[0][0]
    
    def update_image(self, pacman_x):
        self.image = self.frames \
            [int(self.is_frightened)] \
                [int(self.rect.center[0] < pacman_x)]

    def starting(self, kwargs_dict):
        pos = self.rect.center
        self.try_direction = 'u'

        self.movement(const.SPEED(kwargs_dict["game_data"], False), kwargs_dict["windowsize"],
                      kwargs_dict["walls_group"], kwargs_dict["dt"], True)

        if self.rect.center == pos:
            self.try_direction = 'l'
            self.start = False
    
    def run_frightened_timer(self, kwargs_dict):
        if self.frightened_timer > const.GHOST_FRIGHTENED_INTERVAL(kwargs_dict["game_data"]):
            self.frightened_timer = 0.0
            self.is_frightened = False
        
        self.frightened_timer += kwargs_dict["dt"]
    
    def reset_frightened(self):
        self.set_pos(const.GHOST3_START_POS)
        self.is_frightened = False
        self.start = True
        self.try_direction = 'u'

    def direct_follow(self, follow_pos, walls_group):
        min_distance = float('inf')
        min_direction = 'u'

        for direction_let, direction_num in dmap.items():
            if direction_let == opp_d[self.curr_direction]:
                continue

            new_x = self.rect.center[0] + direction_num[0] * (const.UNIT + 1)
            new_y = self.rect.center[1] + direction_num[1] * (const.UNIT + 1)

            if collision_with_wall_point((new_x, new_y), walls_group, False):
                continue
            
            distance = ((follow_pos[0] - new_x)**2
                        + (follow_pos[1] - new_y)**2) ** 0.5

            if distance < min_distance:
                min_distance = distance
                min_direction = direction_let
        
        self.try_direction = min_direction


class Ghost1(Ghost):
    def __init__(self, start_position) -> None:
        super().__init__(start_position)
        self.load_frames()
        self.angry = False
        self.try_direction = 'r'
    
    def load_frames(self):
        with as_file(files("pac_man").joinpath(f"resources/ghosts/red.png")) as path:
            orig_image = pygame.transform.scale(pygame.image.load(path), (const.UNIT*2, const.UNIT*2))
        
        with as_file(files("pac_man").joinpath(f"resources/ghosts/red_angry.png")) as path:
            orig_image_angry = pygame.transform.scale(pygame.image.load(path), (const.UNIT*2, const.UNIT*2))
        
        with as_file(files("pac_man").joinpath(f"resources/ghosts/frightened.png")) as path:
            image_frightened = pygame.transform.scale(pygame.image.load(path), (const.UNIT*2, const.UNIT*2))
        
        self.frames = ((orig_image, pygame.transform.flip(orig_image, True, False)), \
            (orig_image_angry, pygame.transform.flip(orig_image_angry, True, False))), \
            ((image_frightened, image_frightened), (image_frightened, image_frightened))
        
        self.image = self.frames[0][0][0]
    
    def update_image(self, pacman_x):
        self.image = self.frames[int(self.is_frightened)][int(self.angry)][int(self.rect.center[0] < pacman_x)]
 
    def update(self, **kwargs):
        if self.start:
            self.starting(kwargs)
            return
        
        self.angry = kwargs["num_pellets"] <= const.GHOST1_SPEEDUP_PELLET_NUM
        self.update_image(kwargs["pacman"].rect.center[0])

        if self.is_frightened:
            follow_pos = mirror_point(kwargs["pacman"].rect.center, self.rect.center)
            self.run_frightened_timer(kwargs)
        else:
            match kwargs["game_data"]["ghost_mode"]:
                case const.GhostMode.SCATTER:
                    follow_pos = (kwargs["windowsize"][0], 0)
                case const.GhostMode.CHASE:
                    follow_pos = kwargs["pacman"].rect.center
        
        for crossing_rect in kwargs["crossing_rects"]:
            if self.rect == crossing_rect:
                self.direct_follow(follow_pos, kwargs["walls_group"])
        
        self.movement(const.SPEED(kwargs["game_data"], False, self.is_frightened) + (0.6 * const.UNIT if self.angry else 0.0),
                      kwargs["windowsize"], kwargs["walls_group"], kwargs["dt"])


class Ghost2(Ghost):
    def __init__(self, start_position) -> None:
        super().__init__(start_position)
        self.load_frames("pink")
 
    def update(self, **kwargs):
        if self.start:
            self.starting(kwargs)
            return

        self.update_image(kwargs["pacman"].rect.center[0])

        if self.is_frightened:
            follow_pos = mirror_point(kwargs["pacman"].rect.center, self.rect.center)
            self.run_frightened_timer(kwargs)
        else:
            match kwargs["game_data"]["ghost_mode"]:
                case const.GhostMode.SCATTER:
                    follow_pos = (0, 0)
                case const.GhostMode.CHASE:
                    follow_pos = kwargs["pacman"].rect.center[0] + dmap[kwargs["pacman"].try_direction][0] * const.UNIT * 4, \
                        kwargs["pacman"].rect.center[1] + dmap[kwargs["pacman"].try_direction][1] * const.UNIT * 4

        for crossing_rect in kwargs["crossing_rects"]:
            if self.rect == crossing_rect:
                self.direct_follow(follow_pos, kwargs["walls_group"])

        self.movement(const.SPEED(kwargs["game_data"], False, self.is_frightened), kwargs["windowsize"],
                      kwargs["walls_group"], kwargs["dt"])


class Ghost3(Ghost):
    def __init__(self, start_position) -> None:
        super().__init__(start_position)
        self.load_frames("cyan")
 
    def update(self, **kwargs):
        if self.start:
            self.starting(kwargs)
            return

        self.update_image(kwargs["pacman"].rect.center[0])

        if self.is_frightened:
            follow_pos = mirror_point(kwargs["pacman"].rect.center, self.rect.center)
            self.run_frightened_timer(kwargs)
        else:
            match kwargs["game_data"]["ghost_mode"]:
                case const.GhostMode.SCATTER:
                    follow_pos = kwargs["windowsize"]
                case const.GhostMode.CHASE:
                    follow_pos_1 = kwargs["ghost1"].rect.center
                    follow_pos_2 = kwargs["pacman"].rect.center[0] + dmap[kwargs["pacman"].try_direction][0] * const.UNIT * 2, \
                        kwargs["pacman"].rect.center[1] + dmap[kwargs["pacman"].try_direction][1] * const.UNIT * 2

                    follow_pos = 2 * follow_pos_2[0] - follow_pos_1[0], \
                        2 * follow_pos_2[1] - follow_pos_1[1]
        
        for crossing_rect in kwargs["crossing_rects"]:
            if self.rect == crossing_rect:
                self.direct_follow(follow_pos, kwargs["walls_group"])

        self.movement(const.SPEED(kwargs["game_data"], False, self.is_frightened), kwargs["windowsize"],
                      kwargs["walls_group"], kwargs["dt"])


class Ghost4(Ghost):
    def __init__(self, start_position) -> None:
        super().__init__(start_position)
        self.load_frames("yellow")
 
    def update(self, **kwargs):
        if self.start:
            self.starting(kwargs)
            return

        self.update_image(kwargs["pacman"].rect.center[0])

        if self.is_frightened:
            follow_pos = mirror_point(kwargs["pacman"].rect.center, self.rect.center)
            self.run_frightened_timer(kwargs)
        else:
            match kwargs["game_data"]["ghost_mode"]:
                case const.GhostMode.SCATTER:
                    follow_pos = (0, kwargs["windowsize"][1])
                case const.GhostMode.CHASE:
                    follow_pos = kwargs["pacman"].rect.center
        
        for crossing_rect in kwargs["crossing_rects"]:
            if self.rect == crossing_rect:
                self.direct_follow(
                    follow_pos if
                        ((follow_pos[0] - self.rect.center[0]) ** 2 +
                        (follow_pos[1] - self.rect.center[1]) ** 2) ** 0.5
                        > const.UNIT*8
                    else (0, kwargs["windowsize"][1]),
                    kwargs["walls_group"])

        self.movement(const.SPEED(kwargs["game_data"], False, self.is_frightened), kwargs["windowsize"],
                      kwargs["walls_group"], kwargs["dt"])


class PacmanDirection(pygame.sprite.Sprite):
    "Klasse für Pfeil, die Pac-Mans beabsichtigte Richtung (try_direction) anzeigt"

    def __init__(self) -> None:
        super().__init__()

        with as_file(files("pac_man").joinpath(f"resources/pacman/direction.png")) as path:
            frame = pygame.transform.scale(pygame.image.load(path), (const.UNIT*6, const.UNIT*6))

        rotations = {'r': 0, 'u': 90, 'l': 180, 'd': 270}
        self.frames = {d: pygame.transform.rotate(frame, angle) for d, angle in rotations.items()}

        self.image = self.frames['r']
        self.rect = self.image.get_rect()
    
    def update(self, **kwargs) -> None:
        """Passt sich Pac-Mans Position und gewünschter Richtung an"""
        self.image = self.frames[kwargs["pacman"].try_direction]
        self.rect.center = kwargs["pacman"].rect.center


class Pellet(StaticSprite):
    "Elternklasse für Pellets"

    def __init__(self, position: tuple[int, int], texture: str):
        super().__init__(position, texture, (const.UNIT*2, const.UNIT*2), 0)
    
    def update(self, **kwargs):
        """Pellet updaten: Löscht sich, wenn von Pac-Man berührt"""

        if kwargs["pacman"].hitbox.collidepoint(*self.rect.center):
            kwargs["game_data"]["score"] += 10
            self.kill()


class NormalPellet(Pellet):
    "Klasse für normale Pellets"
    def __init__(self, position: tuple[int, int]):
        super().__init__(position, "pellets/0")


class PowerPellet(Pellet):
    "Klasse für Power Pellets"
    def __init__(self, position: tuple[int, int]):
        super().__init__(position, "pellets/1")

        self.image.set_alpha(255)
        self.blink_timer = 0.0
    
    def update(self, **kwargs):        
        if self.blink_timer > const.POWER_PELLET_BLINK_INTERVAL:
            match self.image.get_alpha():
                case 0:   self.image.set_alpha(255)
                case 255: self.image.set_alpha(0)

            self.blink_timer = 0.0

        self.blink_timer += kwargs["dt"]

        if kwargs["pacman"].hitbox.collidepoint(*self.rect.center):
            self.kill()


class Fruit(pygame.sprite.Sprite):
    "Klasse für Früchte"
    def __init__(self, position: tuple[int, int], level: int=0):
        super().__init__()
        self.frames = []

        for i in range(6):
            with as_file(files("pac_man").joinpath(f"resources/fruits/{i}.png")) as path:
                self.frames.append(pygame.transform.scale(pygame.image.load(path), (2*const.UNIT, 2*const.UNIT)))
        
        self.image = self.frames[level]
        self.image.set_alpha(0)
        self.rect = self.image.get_rect(topleft=(position[0]-const.UNIT/2, position[1]))
        self.active = False
        self.points = 0
        self.timer = 0.0

    def update(self, **kwargs):
        if self.timer <= 0.0: self.active = False
        else: self.timer -= kwargs["dt"]

        self.image.set_alpha(255 if self.active else 0)

        level, self.points = const.FRUIT_LEVEL_AND_POINTS(kwargs["game_data"])
        self.image = self.frames[level]
