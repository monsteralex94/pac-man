import const
import pygame
from typing import Optional
import sys

class StaticSprite(pygame.sprite.Sprite):
    """Elternklasse für statische Sprites"""

    def __init__(self, position: tuple[int, int], texture: str, scale: tuple[int, int], rotate: float):
        super().__init__()
        self.image = pygame.image.load(f"textures/{texture}.png")
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

        # TODO: texture allgemein machen

        # Frames für die Animation
        frame0 = pygame.transform.scale(pygame.image.load("textures/pacman/0.png"), (const.UNIT*2, const.UNIT*2))
        frame1 = pygame.transform.scale(pygame.image.load("textures/pacman/1.png"), (const.UNIT*2, const.UNIT*2))

        # Rotationswinkel in Grad für jede Richtung
        rotations = {'r': 0, 'u': 90, 'l': 180, 'd': 270}

        # Erstellt Texturen für jede Animationsphase und Richtung
        self.frames = [
            {d: pygame.transform.rotate(frame, angle) for d, angle in rotations.items()}
            for frame in (frame0, frame1)
        ]

        # Aktuelles Frame
        self.image = self.frames[0]['l']

        # Rect (Position und Größe) des Sprites als Ganzzahlen für das Zeichnen auf den Bildschirm
        self.rect = self.image.get_rect(topleft=start_position)

        # Tatsächliche Position des Sprites als Gleitkommazahlen (linke obere Ecke)
        self.float_pos = pygame.Vector2(start_position)

        # Timer und Textur für Animation
        self.texture_timer = 0
        self.texture_num = 0

        # Richtung, in die Pac-Man gerade geht
        self.curr_direction = 'l'
        # Richtung, in die Pac-Man gehen will (wegen Benutzereingabe)
        self.try_direction = 'l'

        self.stuck = False


    def collision_with_wall(self, rect, mapblocks) -> Optional[pygame.Rect]:
        """Falls das Sprite eine Wand berührt, wird der Rect des berührten Blocks zurückgegeben"""

        # Durchgehen aller Blöcke der Map
        for y in range(len(mapblocks)):
            for x in range(len(mapblocks[0])):
                if not mapblocks[y][x]:
                    continue

                # Bestimmen der Position und Größe des aktuellen Blocks
                tile_rect = pygame.Rect(x * const.UNIT, y * const.UNIT, const.UNIT, const.UNIT)

                # Prüfen, ob dieser berührt wird
                if tile_rect.colliderect(rect):
                    # Rückgabe des Rect
                    return tile_rect
        
        # Keine Rückgabe
        return None

    def movement(self, windowsize, mapblocks, dt) -> None:
        """Kontrolliert die Steuerung mit curr_direction und try_direction"""

        # Animation: Wenn der Timer überschritten wird, wechselt das Frame der Animation
        # und der Timer wird zurückgesetzt
        if self.texture_timer > 0.2:
            self.texture_timer = 0
            self.texture_num = int(not self.texture_num)
        
        old_pos = self.float_pos.copy()

        # Bewegung in jede Richtung für den aktuellen Frame (x- und y-Komponenten)
        dmap = {
            'r': (const.SPEED * dt, 0),
            'u': (0, -const.SPEED * dt),
            'l': (-const.SPEED * dt, 0),
            'd': (0, const.SPEED * dt),
        }

        # Bewegung in Richtung curr_direction (aktuelle Richtung) und
        # try_direction (ab der nächsten Kreuzung)
        dx, dy = dmap[self.curr_direction]
        try_dx, try_dy = dmap[self.try_direction]

        ########### Anpassen von dx und dy anhand der Wände auf der Map

        # Prüfen, ob Sprite sich noch im Screen befindet
        if self.rect.right < windowsize[0] and self.rect.left > 0:

            # Nächste Bewegung in x-Richtung?
            if self.try_direction in ('l', 'r'):
                for y in range(min(0, int(dy)), max(0, int(dy))+1):
                    new_rect = self.rect.move(try_dx, y)
                    tile_rect = self.collision_with_wall(new_rect, mapblocks)
                    if not tile_rect:
                        self.curr_direction = self.try_direction
                        dx = try_dx
                        dy = y
            
            # Nächste Bewegung in y-Richtung?
            elif self.try_direction in ('u', 'd'):
                for x in range(min(0, int(dx)), max(0, int(dx))+1):
                    new_rect = self.rect.move(x, try_dy)
                    tile_rect = self.collision_with_wall(new_rect, mapblocks)
                    if not tile_rect:
                        self.curr_direction = self.try_direction
                        dy = try_dy
                        dx = x

        ########### Ausführen der gewünschten Bewegung mit dx und dy

        # Bewegung in x-Richtung
        self.float_pos.x += dx    # intern als Gleitkommazahl (tatsächliche Position)
        self.rect.left = int(self.float_pos.x)   # Als ganze Zahl (für das Zeichnen)

        # Anpassung von kleinen Abweichungen von dem Gitter
        tile_rect = self.collision_with_wall(self.rect, mapblocks)
        if tile_rect:
            if dx > 0:
                self.rect.right = tile_rect.left
            elif dx < 0:
                self.rect.left = tile_rect.right
            self.float_pos.x = self.rect.left

        # Bewegung in y-Richtung
        self.float_pos.y += dy    # intern als Gleitkommazahl (tatsächliche Position)
        self.rect.top = int(self.float_pos.y)   # Als ganze Zahl (für das Zeichnen)

        # Anpassung von kleinen Abweichungen von dem Gitter
        tile_rect = self.collision_with_wall(self.rect, mapblocks)
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

        self.stuck = old_pos == self.float_pos

        # Auswählen der Textur innerhalb der Animation und Aktualisierung des Timers
        self.image = self.frames[self.texture_num][self.curr_direction]
        self.texture_timer += dt
    
    def update(self, **kwargs):
        """Update-Funktion des Entity Sprites"""

        # Bewegung wird ausgeführt
        self.movement(kwargs["windowsize"], kwargs["mapblocks"], kwargs["dt"])


class Pacman(EntitySprite):
    "Klasse für Pac-Man"

    def __init__(self, start_position: tuple[int, int]) -> None:
        super().__init__(start_position)


class Ghost(EntitySprite):
    "Klasse für Geist"

    def __init__(self, start_position: tuple[int, int]) -> None:
        super().__init__(start_position)
    
    def update(self, **kwargs):
        # TODO: create ai
        # ...
        self.movement(kwargs["windowsize"], kwargs["mapblocks"], kwargs["dt"])


class PacmanDirection(pygame.sprite.Sprite):
    "Klasse für Pfeil, die Pac-Mans beabsichtigte Richtung (try_direction) anzeigt"

    def __init__(self) -> None:
        super().__init__()
        frame = pygame.transform.scale(pygame.image.load(f"textures/pacman/direction.png"), (const.UNIT*6, const.UNIT*6))

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
    
    def update(self, pacman: Pacman):
        """Pellet updaten: Löscht sich, wenn von Pac-Man berührt"""

        if pacman.rect.collidepoint(*self.rect.center):
            self.kill()


class NormalPellet(Pellet):
    "Klasse für normale Pellets"
    def __init__(self, position: tuple[int, int]):
        super().__init__(position, "pellets/0")


class PowerPellet(Pellet):
    "Klasse für Power Pellets"
    def __init__(self, position: tuple[int, int]):
        super().__init__(position, "pellets/1")
