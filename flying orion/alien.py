import pygame
from pygame.sprite import Sprite

class Alien(Sprite):
    """a class to represent a single alien in fleet"""
    def __init__(self, ai_game):
        """initialize alien and set starting position"""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        #load the alien image and set its rect atribute
        self.image = pygame.image.load("images/alien.bmp")
        self.rect = self.image.get_rect()

        #start each new alien near the top of the screen
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        #store the aliens exact horizontal position
        self.x = float(self.rect.x)
    def check_edges(self):
        """return true if alien is at the edge of screen """
        screen_rect = self.screen.get_rect()
        return (self.rect.right >= screen_rect.right) or (self.rect.left <= 0)
    

    def update(self):
        """move the alien to the right or left"""
        self.x += self.settings.alien_speed * self.settings.fleet_direction
        self.rect.x = self.x
    

        