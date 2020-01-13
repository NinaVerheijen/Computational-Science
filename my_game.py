import pygame
import sys
import math
import random
import time
from pygame import *
from pygame.locals import *
from pygame.sprite import *


pygame.init()

random.seed(2)
WIDTH = 1100
HEIGHT = 400
CAPTION = 'Traffic Simulator'

speed = 0
max_speed = 2 #130 km\h
curr_speed = 2

class Vehicle(pygame.sprite.Sprite):

    # Constructor. Pass in the color of the Vehicle,
    # and its x and y position

    def __init__(self, ID, color, size, x, y, speed, direction):
       # Call the parent class (Sprite) constructor
       pygame.sprite.Sprite.__init__(self)

       # Create an image of the block, and fill it with a color.
       # This could also be an image loaded from the disk.
       self.ID = ID
       self.image = pygame.Surface(size)
       self.image.fill(color)
       self.speed  = speed
       self.x = int(x)  # variable denoting x position of car
       self.y = int(y)
       self.direction = direction

       # Fetch the rectangle object that has the dimensions of the image
       # Update the position of this object by setting the values of rect.x and rect.y
       self.rect = self.image.get_rect(center=(x,y))

    def move(self):

        new_x = self.x + self.speed  # new place for the car
        new_y = self.y + self.direction[1]

        # if direction[0] > WIDTH:
        #     new_x = new_x - WIDTH
        # if direction[0] > HEIGHT:
        #     new_y = new_y - HEIGHT
        #dista = xp-a[0]


        # self.rect=self.rect.move(direction[0],direction[1]) # Move the car with the given direction
        self.rect.right = new_x  # move the car
        self.x = new_x  # update the car position
        self.rect.bottom = new_y  # move the car
        self.y = new_y


def traffic():
    frame = pygame.display.set_mode((WIDTH, HEIGHT))


    # car1 = Vehicle((255, 0, 0), [10, 10], 100, random.randrange(0,200,1), 0, [0.2,0])
    # car2 = Vehicle((0, 255, 0), [10, 10], + 100, random.randrange(0, 200, 1), 0, [0.5,0])
    all_cars = Group()

    while True:
        chance = random.uniform(0, 1)
        if chance < 0.02:
            car = Vehicle(chance, (255, 0, 0), [10, 10], 100, random.randrange(10,200,35), 0.1 * random.randrange(1,10,1), [0.2,0])
            all_cars.add(car)

        to_close = False
        for car in all_cars:
            for c in all_cars:
                if abs(c.x - car.x) < 8 and car.y == c.y and car.x is not c.x:
                    if car.x < c.x:
                        car.speed -= 0.02
                    else:
                        c.speed -= 0.002
                    to_close = True
                    

            if car.speed < max_speed and to_close is False:
                car.speed += 0.0001
            car.move()
            



        # if direction[0] > 10:
        #     direction[0] = -2

        # else:
        #     direction[0] += 1

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
