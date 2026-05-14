from . import const
import pygame
from typing import Optional


dmap = {
    'r': (1, 0),
    'u': (0, -1),
    'l': (-1, 0),
    'd': (0, 1),
}


def collision_with_wall_rect(rect, blocks_group) -> Optional[pygame.Rect]:
    for sprite in blocks_group:
        if sprite.rect.colliderect(rect):
            return sprite.rect

    return None


def collision_with_wall_point(point, blocks_group) -> Optional[pygame.Rect]:
    for sprite in blocks_group:
        if sprite.rect.collidepoint(point):
            return sprite.rect

    return None


class StaticSprite(pygame.sprite.Sprite):
    """Elternklasse für statische Sprites"""

    def __init__(self, position: tuple[int, int], texture: str, scale: tuple[int, int], rotate: float):
        super().__init__()
        self.image = pygame.image.load(f"{const.CWD}/textures/{texture}.png")
        self.image = pygame.transform.scale(self.image, scale)
        self.image = pygame.transform.rotate(self.image, rotate * 90)
        self.rect = self.image.get_rect(topleft=position)


class Block(StaticSprite):
    """Klasse für Blocks"""

    def __init__(self, position: tuple[int, int]) -> None:
        super().__init__(position, "blocks/0", (const.UNIT, const.UNIT), 0)


class EntitySprite(pygame.sprite.Sprite):
    """Elternklasse für bewegliche Sprites"""

    def __init__(self, start_position: tuple[int, int]) -> None:
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

        # Timer und Texturzahl für Animation
        self.texture_timer = 0
        self.texture_num = 0


    def movement(self, speed, windowsize, blocks_group, dt) -> None:
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
                    if not collision_with_wall_rect(self.rect.move(try_dx, y), blocks_group):
                        self.curr_direction = self.try_direction
                        dx = try_dx
                        dy = y
            
            # Genauso wie davor, nur mit x und y vertauscht
            elif self.try_direction in ('u', 'd'):
                for x in range(min(0, int(dx)), max(0, int(dx))+1):
                    if not collision_with_wall_rect(self.rect.move(x, try_dy), blocks_group):
                        self.curr_direction = self.try_direction
                        dy = try_dy
                        dx = x

        ########### Ausführen der gewünschten Bewegung mit dx und dy

        # Bewegung in x-Richtung
        self.float_pos.x += dx    # intern als Gleitkommazahl (tatsächliche Position)
        self.rect.left = int(self.float_pos.x)   # Als ganze Zahl (für das Zeichnen)

        # Anpassung von Abweichungen
        tile_rect = collision_with_wall_rect(self.rect, blocks_group)
        if tile_rect:
            if dx > 0:
                self.rect.right = tile_rect.left
            elif dx < 0:
                self.rect.left = tile_rect.right
            self.float_pos.x = self.rect.left

        # Bewegung in y-Richtung
        self.float_pos.y += dy    # intern als Gleitkommazahl (tatsächliche Position)
        self.rect.top = int(self.float_pos.y)   # Als ganze Zahl (für das Zeichnen)

        # Anpassung von Abweichungen
        tile_rect = collision_with_wall_rect(self.rect, blocks_group)
        if tile_rect:
            if dy > 0:
                self.rect.bottom = tile_rect.top
            elif dy < 0:
                self.rect.top = tile_rect.bottom
            self.float_pos.y = self.rect.top
    
        if self.float_pos.x > windowsize[0]:
            self.float_pos.x = -self.rect.width 
        if self.float_pos.x < -self.rect.width:
            self.float_pos.x = windowsize[0]
        
        # Neue, angepasste Position
        self.rect.topleft = (int(self.float_pos.x), int(self.float_pos.y))
        self.hitbox.center = self.rect.center

    def update(self, **kwargs):
        """Update-Funktion des Entity Sprites"""
        pass


class Pacman(EntitySprite):
    "Klasse für Pac-Man"

    def __init__(self, start_position: tuple[int, int]) -> None:
        super().__init__(start_position)

        # Frames für die Animation
        frame0 = pygame.transform.scale(pygame.image.load(f"{const.CWD}/textures/pacman/0.png"), (const.UNIT*2, const.UNIT*2))
        frame1 = pygame.transform.scale(pygame.image.load(f"{const.CWD}/textures/pacman/1.png"), (const.UNIT*2, const.UNIT*2))

        # Rotationswinkel in Grad für jede Richtung
        rotations = {'r': 0, 'u': 90, 'l': 180, 'd': 270}

        # Erstellt Texturen für jede Animationsphase und Richtung
        self.frames = [
            {d: pygame.transform.rotate(frame, angle) for d, angle in rotations.items()}
            for frame in (frame0, frame1)
        ]

        self.image = self.frames[0]['l']
    
    def update(self, **kwargs):
        ########### ANIMATION
        # Wenn der Timer überschritten wird, wechselt das Frame der Animation
        # und der Timer wird zurückgesetzt
        if self.texture_timer > 0.1:
            self.texture_timer = 0
            self.texture_num = int(not self.texture_num)

        # Auswählen der Textur innerhalb der Animation und Aktualisierung des Timers
        self.image = self.frames[self.texture_num][self.curr_direction]
        self.texture_timer += kwargs["dt"]

        ########### BEWEGUNG
        self.movement(const.PACMAN_SPEED, kwargs["windowsize"], kwargs["blocks_group"], kwargs["dt"])


class Ghost1(EntitySprite):
    "Klasse für Geist"

    def __init__(self, start_position: tuple[int, int]) -> None:
        super().__init__(start_position)
        self.frames = \
            pygame.transform.scale(pygame.image.load(f"{const.CWD}/textures/ghosts/red0.png"), (const.UNIT*2, const.UNIT*2)), \
            pygame.transform.scale(pygame.image.load(f"{const.CWD}/textures/ghosts/red1.png"), (const.UNIT*2, const.UNIT*2))
        
        self.image = self.frames[0]
        self.dir_switch_timer = 0.0
 
    def update(self, **kwargs):
        self.image = self.frames[int(self.rect.center[0] < kwargs["pacman"].rect.center[0])]

        follow_pos = kwargs["pacman"].rect.center
        min_distance = float('inf')
        min_direction = 'l'

        for direction_let, direction_num in dmap.items():
            new_x = self.rect.center[0] + direction_num[0] * (const.UNIT + 1)
            new_y = self.rect.center[1] + direction_num[1] * (const.UNIT + 1)

            if collision_with_wall_point((new_x, new_y), kwargs["blocks_group"]):
                continue
            
            distance = ((follow_pos[0] - new_x)**2
                        + (follow_pos[1] - new_y)**2) ** 0.5

            if distance < min_distance:
                min_distance = distance
                min_direction = direction_let

        if self.dir_switch_timer > 0.3:
            self.dir_switch_timer = 0
            self.try_direction = min_direction
        else:
            self.dir_switch_timer += kwargs["dt"]

        self.movement(const.GHOST_SPEED, kwargs["windowsize"], kwargs["blocks_group"], kwargs["dt"])


class Ghost2(EntitySprite):
    "Klasse für Geist"

    def __init__(self, start_position: tuple[int, int]) -> None:
        super().__init__(start_position)
        self.frames = \
            pygame.transform.scale(pygame.image.load(f"{const.CWD}/textures/ghosts/pink0.png"), (const.UNIT*2, const.UNIT*2)), \
            pygame.transform.scale(pygame.image.load(f"{const.CWD}/textures/ghosts/pink1.png"), (const.UNIT*2, const.UNIT*2))
        
        self.image = self.frames[0]
        self.dir_switch_timer = 0.0
 
    def update(self, **kwargs):
        self.image = self.frames[int(self.rect.center[0] < kwargs["pacman"].rect.center[0])]

        follow_pos = kwargs["pacman"].rect.center[0] + dmap[kwargs["pacman"].try_direction][0] * const.UNIT * 4, \
            kwargs["pacman"].rect.center[1] + dmap[kwargs["pacman"].try_direction][1] * const.UNIT * 4
        
        min_distance = float('inf')
        min_direction = 'l'

        for direction_let, direction_num in dmap.items():
            new_x = self.rect.center[0] + direction_num[0] * (const.UNIT + 1)
            new_y = self.rect.center[1] + direction_num[1] * (const.UNIT + 1)

            if collision_with_wall_point((new_x, new_y), kwargs["blocks_group"]):
                continue
            
            distance = ((follow_pos[0] - new_x)**2
                        + (follow_pos[1] - new_y)**2) ** 0.5

            if distance < min_distance:
                min_distance = distance
                min_direction = direction_let

        if self.dir_switch_timer > 0.3:
            self.dir_switch_timer = 0
            self.try_direction = min_direction
        else:
            self.dir_switch_timer += kwargs["dt"]

        self.movement(const.GHOST_SPEED, kwargs["windowsize"], kwargs["blocks_group"], kwargs["dt"])


class PacmanDirection(pygame.sprite.Sprite):
    "Klasse für Pfeil, die Pac-Mans beabsichtigte Richtung (try_direction) anzeigt"

    def __init__(self) -> None:
        super().__init__()
        frame = pygame.transform.scale(pygame.image.load(f"{const.CWD}/textures/pacman/direction.png"), (const.UNIT*6, const.UNIT*6))

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
