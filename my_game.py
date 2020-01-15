import pygame
import sys
import math as Math
import random
import time as tijd
from pygame import *
from pygame.locals import *
from pygame.sprite import *


pygame.init()

clock = pygame.time.Clock()
clock.tick(60)

# lanes = [lane1, lane2, lane3]
random.seed(2)

WIDTH = 4000 # 8 km?
HEIGHT = 450
road_length = 12
CAPTION = 'Traffic Simulator'

max_speed = 130
 #130 km\h

def meter_to_pixel(distance):
    one_m = WIDTH/(road_length * 1000)
    dist = distance*one_m
    return dist

def pixel_to_meter(pixels):
    one_p = (road_length * 1000)/WIDTH
    dist = pixels*one_p
    return dist

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
       self.size = size

       # Fetch the rectangle object that has the dimensions of the image
       # Update the position of this object by setting the values of rect.x and rect.y
       self.rect = self.image.get_rect(center=(x,lane))
       self.rect.size = (size[0] + 10, size[1])


    def desired_gap(self, v, d_v):
        """
        s_0 is minimum bumper to bumper gap -> 2m
        a is acceleration in every day traffic -> 0.3m/s^2
        b is comfortable (breaking) deceleration in everyday traffic -> 3.0m/s^2
        delta is acceleration exponent -> 4
        T is desired safety time -> 1.5 s
        s is current gap
        """
        s_0 = 200  # minimum gap between cars
        a = 0.3
        b = 3
        T = 1.5
        des_gap = s_0 + max(0, v*T + ((v*d_v)/ (2*Math.sqrt(a*b))))
        return des_gap

    def comp_acc(self, s, lead_speed):
        a = 0.3
        v_0 = max_speed
        v = self.speed
        d = 4
        d_v = abs(v - lead_speed)
        a_free = a*(1-(v/v_0)**d)
        a_int = a*((self.desired_gap(v, d_v) / s)**2)

        acc =  a_free - a_int
        return acc

    def move(self):
        new_x = self.x + meter_to_pixel(self.speed) # new place for the car
        new_y = self.y + self.direction[1]

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
    # print(road.lanes, road.pos_lanes)
    road.add_lane()
    # print(road.lanes, road.pos_lanes)
    road.delete_lane(all_cars)
    # print(road.lanes)




    while True:
        tijd.sleep(0.05)
        chance = random.uniform(0, 1)

        if chance < 0.2:
            car = Vehicle(chance, (255, 0, 0), [10, 10], 100, random.choice(road.pos_lanes), 30 + random.randrange(-10,10,2), [0.2,0])
            all_cars.add(car)

            # put car in the right lane and keep track of which lane the car is
            for number in range(len(road.pos_lanes)):
                if car.y == road.pos_lanes[number]:
                    road.lanes[number].append(car)
                    # print(car.lane)

        for car in all_cars:
            for c in all_cars:

                # Only check cars that are in same lane and in front of car
                if car.y == c.y and car.x < c.x:
                    gap = pixel_to_meter(c.x - car.x)
                    car.speed += car.comp_acc(gap, c.speed)

                    # prevent cars from going backwards.

                    if car.speed < 0:
                        car.speed = 0
                # If there is no car in front of current car.
                else:
                    gap = 1000000
                    car.speed += car.comp_acc(gap, car.speed)

                    if car.speed < 0:
                        car.speed = 0

            car.move()
            if car.x > WIDTH:
                all_cars.remove(car)

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
