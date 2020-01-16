# from .dir import Dir
import pygame
import sys
import math as Math
import random
import time as tijd
from pygame import *
from pygame.locals import *
from pygame.sprite import *
from Vehicle import Vehicle
from road import Road

# from Vehicle import Vehicle

pygame.init()

clock = pygame.time.Clock()
clock.tick(60)

# lanes = [lane1, lane2, lane3]
random.seed(2)

WIDTH = 1100 # 8 km?
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

        if chance < 0.3:
            car = Vehicle(chance, (255, 0, 0), [10, 10], 100, random.choice(road.pos_lanes), 50 + random.randrange(-10,10,2), [0.2,0])
            all_cars.add(car)

            # put car in the right lane and keep track of which lane the car is
            for number in range(len(road.pos_lanes)):
                if car.y == road.pos_lanes[number]:
                    road.lanes[number].append(car)

        for car in all_cars:
            change_lanes = random.uniform(0, 1)

            if change_lanes < 0.01:
                car.switch = True

            if car.switch is True:
                if car.y in road.pos_lanes:
                    car.left_or_right = random.uniform(0, 1)
                    if car.lane * 50 == road.pos_lanes[0]:
                        car.left_or_right = 1
                        
                    if car.lane * 50 == road.pos_lanes[-1]:
                        car.left_or_right = 0

                if car.left_or_right < 0.5:
                    car.left_right = -1 
                elif car.left_or_right >= 0.5:
                    car.left_right = 1   

                car.y += car.left_right

                if car.y in road.pos_lanes:
                    car.lane = car.y / 50
                    car.switch = False


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

        # if len(road.lanes[-1]) >= 2:
        #     road.delete_lane(all_cars)
        #     road.add_lane()
        #     road.add_lane()

        # quit pygame

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        frame.fill((255, 255, 255))

        # Draw the lanes
        pygame.draw.line(frame, (0, 0, 0), (0, road.pos_lanes[0] - 25), (WIDTH, road.pos_lanes[0] - 25))
        for lane in road.pos_lanes:
            pygame.draw.line(frame, (0, 0, 0), (0, lane + 25), (WIDTH, lane + 25))
        
        all_cars.draw(frame)
        display.update()
        pygame.display.flip()


if __name__ == '__main__':
    traffic()
