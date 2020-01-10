import pygame
import sys
import math
import random
from pygame import *
from pygame.locals import *
from pygame.sprite import *


pygame.init()


WIDTH = 1100
HEIGHT = 400
CAPTION = 'Traffic Simulator'

speed = 0
max_speed = 30
velocity = [2, 0]


class Vehicle(pygame.sprite.Sprite):

    # Constructor. Pass in the color of the Vehicle,
    # and its x and y position
    def __init__(self, ID, color, width, height, x, y):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        self.ID = ID
        # Create an image of the Vehicle, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.x = int(x)  # variable denoting x position of car
        self.y = int(y)

        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect(center=(x,y))

    def move(self, velocity, a):

        new_x = self.x + velocity[0]  # new place for the car
        new_y = self.y + velocity[1]

        # if velocity[0] > WIDTH:
        #     new_x = new_x - WIDTH
        # if velocity[0] > HEIGHT:
        #     new_y = new_y - HEIGHT
        #dista = xp-a[0]

        self.rect=self.rect.move(velocity[0],velocity[1]) # Move the car with the given velocity
        # self.rect.left = new_x  # move the car
        # self.x = new_x  # update the car position
        # self.rect.left = new_y  # move the car
        # self.y = new_y


def traffic():
    frame = pygame.display.set_mode((WIDTH, HEIGHT))
    # car1 = Vehicle((255, 0, 0), 10, 10, velocity[0] + 100, random.randrange(0,200,1))
    all_cars = Group()

    while True:
        chance = random.uniform(0, 1)
        if chance < 0.07:
            car = Vehicle(chance, (255, 0, 0), 10, 10, velocity[0] + 0, random.randrange(5,400,35))
            all_cars.add(car)
        for m in all_cars:
            m.move(velocity, [100, 100])
        # car1.move(velocity, [100, 100])
        # if velocity[0] > 10:
        #     velocity[0] = -2
        # else:
        #     velocity[0] += 1

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
