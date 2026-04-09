import const
import pygame

class Block(pygame.sprite.Sprite):
    def __init__(self, position: tuple[int, int], walls: list[bool], *groups: pygame.sprite.AbstractGroup) -> None:
        super().__init__(*groups)

        # select image        
        num_walls = sum(walls)
        if num_walls == 0:
            self.image = pygame.image.load("textures/blocks/0.png").convert()
        elif num_walls == 1:
            self.image = pygame.image.load("textures/blocks/1.png").convert()
            self.image = pygame.transform.rotate(self.image, walls.index(True) * 90)
        elif num_walls == 2:
            first_wall = walls.index(True)
            second_wall = walls.index(True, first_wall + 1)

            dif = second_wall - first_wall

            if dif == 1:
                self.image = pygame.image.load("textures/blocks/2.1.png").convert()
                self.image = pygame.transform.rotate(self.image, first_wall * 90)
            elif dif == 2:
                self.image = pygame.image.load("textures/blocks/3.png").convert()
                self.image = pygame.transform.rotate(self.image, first_wall * 90)
            elif dif == 3:
                self.image = pygame.image.load("textures/blocks/2.1.png").convert()
                self.image = pygame.transform.rotate(self.image, -90)

        elif num_walls == 3:
            self.image = pygame.image.load("textures/blocks/4.png").convert()
            self.image = pygame.transform.rotate(self.image, walls.index(False) * 90)
        elif num_walls == 4:
            self.image = pygame.image.load("textures/blocks/5.png").convert()
        
        self.image = pygame.transform.scale(self.image, (const.UNIT*8, const.UNIT*8))
        
        self.rect = self.image.get_rect(topleft=position)
