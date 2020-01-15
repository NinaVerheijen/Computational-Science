import pygame
import sys
import math
import random
import time as tijd
from pygame import *
from pygame.locals import *
from pygame.sprite import *


pygame.init()
lane1 = 40
lane2 = 80
lane3 = 120

lanes = [lane1, lane2, lane3]
random.seed(2)
WIDTH = 3000
HEIGHT = 1000
CAPTION = 'Traffic Simulator'

speed = 0
max_speed = 20 #130 km\h
curr_speed = 2

class Vehicle(pygame.sprite.Sprite):

    # Constructor. Pass in the color of the Vehicle,
    # and its x and y position

    def __init__(self, ID, color, size, x, lane, speed, direction):
       # Call the parent class (Sprite) constructor
       pygame.sprite.Sprite.__init__(self)

       # Create an image of the block, and fill it with a color.
       # This could also be an image loaded from the disk.
       self.ID = ID
       self.image = pygame.Surface(size)
       self.image.fill(color)
       self.speed  = speed
       self.x = int(x)  # variable denoting x position of car
       self.y = int(lane)
       self.direction = direction
       self.lane = lane / 50

       # Fetch the rectangle object that has the dimensions of the image
       # Update the position of this object by setting the values of rect.x and rect.y
       self.rect = self.image.get_rect(center=(x,lane))
       self.rect.size = (size[0] + 10, size[1])


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


class Road:

    def __init__(self, lanes, max_speed):

        self.lanes = []
        self.max_speed = max_speed
        self.pos_lanes = []
        
        # Initialize the starting lanes
        for number_lanes in range(lanes):
            self.lanes.append([])
            self.pos_lanes.append(50 * (number_lanes+1))

    # Add new lane to the road
    def add_lane(self):
        self.lanes.append([])
        self.pos_lanes.append(50 * (len(self.lanes)))

    # Delete the last lane and delete all cars on that lane
    def delete_lane(self, all_cars):
        for delete_cars in all_cars:
            if delete_cars.y == self.pos_lanes[-1]:
                all_cars.remove(delete_cars)
        self.lanes.pop()
        self.pos_lanes.pop()



def traffic():
    frame = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

    all_cars = Group()
    # Make the road
    road = Road(5,50)
    print(road.lanes, road.pos_lanes)
    road.add_lane()
    print(road.lanes, road.pos_lanes)
    road.delete_lane(all_cars)
    print(road.lanes)
    


    while True:
        chance = random.uniform(0, 1)
        if chance < 0.1:
            car = Vehicle(chance, (255, 0, 0), [10, 10], 100, random.choice(road.pos_lanes), 0.5 * random.randrange(1,5,1), [0.2,0])
            all_cars.add(car)

            # put car in the right lane and keep track of which lane the car is
            for number in range(len(road.pos_lanes)):
                if car.y == road.pos_lanes[number]:
                    road.lanes[number].append(car)
                    print(car.lane)

        for la in range(len(road.lanes)):
            for i in range(len(road.lanes[la])):
                to_close = False
                car = road.lanes[la][i]
                if car.x > WIDTH:
                    all_cars.remove(car)
                if i == len(road.lanes[la]) - 1:
                    next_car = None
                else:
                    next_car = road.lanes[la][i+1]
                    if abs(next_car.x - car.x) < 30:
                        car.speed = next_car.speed - 0.005
                        to_close = True
                if car.speed < max_speed and to_close is False:
                    car.speed += 0.001
                car.move()

        if len(road.lanes[-1]) >= 2:
            road.delete_lane(all_cars)
            road.add_lane()
            road.add_lane()

        # quit pygame
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
            
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        frame.fill((255, 255, 255))
        all_cars.draw(frame)
        display.update()
        pygame.display.flip()


if __name__ == '__main__':
    traffic()
