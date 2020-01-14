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
WIDTH = 1100
HEIGHT = 400
CAPTION = 'Traffic Simulator'

speed = 0
max_speed = 1.8 #130 km\h
curr_speed = 2

class Vehicle(pygame.sprite.Sprite):

    # Constructor. Pass in the color of the Vehicle,
    # and its x and y position

    def __init__(self, ID, color, size, x, lane, speed, direction):
       # Call the parent class (Sprite) constructor
       pygame.sprite.Sprite.__init__(self)

       # Create an image of the block, and fill it with a color.
       # This could also be an image loaded from the disk.
       self.lane = lane
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

        for number_lanes in range(lanes):
            self.lanes.append(number_lanes + 1)

    def add_lane(self):
        new_lane = len(self.lanes) + 1
        self.lanes.append(new_lane)

def traffic():
    frame = pygame.display.set_mode((WIDTH, HEIGHT))
    road = Road(3,50)
    print(road.lanes)
    road.add_lane()
    print(road.lanes)

    # car1 = Vehicle((255, 0, 0), [10, 10], 100, random.randrange(0,200,1), 0, [0.2,0])
    # car2 = Vehicle((0, 255, 0), [10, 10], + 100, random.randrange(0, 200, 1), 0, [0.5,0])
    all_cars = Group()
    lane_1 = []
    lane_2 = []
    lane_3 = []
    lane_4 = []
    lanes = [50, 100, 150, 200]
    all_lanes = [lane_1, lane_2, lane_3, lane_4]

    while True:
        chance = random.uniform(0, 1)
        if chance < 0.01:
            car = Vehicle(chance, (255, 0, 0), [10, 10], 100, random.choice(lanes), 0.1 * random.randrange(1,5,1), [0.2,0])
            all_cars.add(car)
            if car.y == 50:
                lane_1.append(car)
                car.lane = 1
            elif car.y == 100:
                lane_2.append(car)
                car.lane = 2
            elif car.y == 150:
                lane_3.append(car)
                car.lane = 3
            else:
                lane_4.append(car)
                car.lane = 4

        for la in range(len(all_lanes)):
            for i in range(len(all_lanes[la])):
                to_close = False
                car = all_lanes[la][i]
                if car.x > WIDTH:
                    all_cars.remove(car)
                if i == len(all_lanes[la]) - 1:
                    next_car = None
                else:
                    next_car = all_lanes[la][i+1]
                    if abs(next_car.x - car.x) < 30:
                        car.speed = next_car.speed - 0.005
                        to_close = True
                if car.speed < max_speed and to_close is False:
                    car.speed += 0.001
                car.move()

            
# =======
#     lane1_group = pygame.sprite.Group()
#     lane2_group = Group()
#     lane3_group = Group()

#     while True:
#         chance = random.uniform(0, 1)
#         if chance < 0.3:
#             car = Vehicle(chance, (255, 0, 0), [10, 10], 100, random.choice(lanes), 0.1 * random.randrange(1,10,1), [0.2,0])
#             if car.lane == lane1:
#                 lane1_group.add(car)
#             elif car.lane == lane2:
#                 lane2_group.add(car)
#             elif car.lane == lane3:   
#                 lane3_group.add(car)  
#                 # print(lane3_group)   
#             all_cars.add(car)

#         to_close = False


#         for car in all_cars:
#             cur_lane = None
#             if lane1_group.has(car):
#                 cur_lane = lane1_group
#             elif lane2_group.has(car):
#                 cur_lane = lane2_group
#             elif lane3_group.has(car):
#                 cur_lane = lane3_group
#                 # print(car.lane, car.ID)
#                 # print(len(lane2_group))
#             # print(car.groups())
#             for c in cur_lane:
#                 # print(abs(c.x - car.x))
#                 if abs(c.x - car.x) < 10 and car.y == c.y and car.x is not c.x:
#                     if car.x < c.x:
#                         car.speed -= 0.002
#                     else:
#                         c.speed -= 0.002
#                     to_close = True
   

#             if car.speed < max_speed and to_close is False:
#                 car.speed += 0.0001
#             car.move()




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
