import pygame
import sys
import math
from pygame import *
from pygame.locals import *
from pygame.sprite import *


pygame.init()


WIDTH = 1100
HEIGHT = 400
CAPTION = 'Traffic Simulator'

speed = 0
max_speed = 30
velocity = [0.5, 0.5]


class Block(pygame.sprite.Sprite):

    # Constructor. Pass in the color of the block,
    # and its x and y position
    def __init__(self, color, width, height, x, y):
       # Call the parent class (Sprite) constructor
       pygame.sprite.Sprite.__init__(self)

       # Create an image of the block, and fill it with a color.
       # This could also be an image loaded from the disk.
       self.image = pygame.Surface([width, height])
       self.image.fill(color)
       self.x = int(x)  # variable denoting x position of car
       self.y = int(y)

       # Fetch the rectangle object that has the dimensions of the image
       # Update the position of this object by setting the values of rect.x and rect.y
       self.rect = self.image.get_rect()

    def move(self, velocity, a):

        new_x = self.x + velocity[0]  # new place for the car
        new_y = self.y + velocity[1]

        if velocity[0] > WIDTH:
            new_x = new_x - WIDTH
        if velocity[0] > HEIGHT:
            new_y = new_y - HEIGHT
        #dista = xp-a[0]

        self.rect.left = new_x  # move the car
        self.x = new_x  # update the car position
        # self.rect.right = new_y  # move the car
        # self.y = new_y


def traffic():
    frame = pygame.display.set_mode((WIDTH, HEIGHT))
    car1 = Block((255, 0, 0), 10, 10, velocity[0] + 500, 600)
    all_cars = Group(car1)

    while True:
        car1.move(velocity, [200, 200])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        frame.fill((255, 255, 255))
        all_cars.draw(frame)
        display.update()
        pygame.display.flip()


if __name__ == '__main__':
    traffic()
