# from .dir import Dir
import pygame
import sys
import os
import math as Math
import random
import bisect  
import time as tijd
from pygame import *
from pygame.locals import *
from pygame.sprite import *
from Vehicle import Vehicle
from road import Road

# from Vehicle import Vehicle
os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'

pygame.init()

clock = pygame.time.Clock()
clock.tick(60)

# background 2 or 3 lanes

# background_image = pygame.image.load("2baans.png")
background_image = pygame.image.load("3baans.png")

# lanes = [lane1, lane2, lane3]
random.seed(2)

WIDTH = 1920 # 8 km?
HEIGHT = 100
road_length = 12
# CAPTION = 'Traffic Simulator'
pygame.display.set_caption('Traffic Simulator')

 

def meter_to_pixel(distance):
    # hoeveel pixels in meter
    one_m = WIDTH/(road_length * 1000)
    dist = distance*one_m
    return dist

def pixel_to_meter(pixels):
    # meters in een pixel zitten
    one_p = (road_length * 1000)/WIDTH
    dist = pixels*one_p
    return dist

def vehicle_spawn(road, all_cars):
    chance = random.uniform(0, 1)

    if chance < 0.3:
        truck_chance = random.uniform(0,1)
        if truck_chance < 0.80:
            vehicle = Vehicle(chance, 'car', (255, 0, 0), [24/2, 12/2], -30, random.choice(road.pos_lanes), 50 + random.randrange(-10,10,2), [0.2,0])
            all_cars.add(vehicle)
        else:
            choice = random.choices(population = road.pos_lanes, weights = [0.02, 0.04, 0.1, 0.84])
            vehicle = Vehicle(chance, 'truck', (0, 0, 255), [98/2, 14/2], -30, choice[0], 10 + random.randrange(-5,5,1), [0.2,0])
            all_cars.add(vehicle)

        # put car in the right lane and keep track of which lane the car is
        for number in range(len(road.pos_lanes)):
            if vehicle.y == road.pos_lanes[number]:
                road.lanes[number].append(vehicle)

    return all_cars

def lane_switching(car, road, all_cars):

    car.image.fill((0,255,0))
    if car.y in road.pos_lanes:
        car.left_or_right = random.uniform(0, 1)
        # exception if most left lane or most right lane
        if car.lane * 10 + 29 == road.pos_lanes[0]:
            car.left_or_right = 1
            
        if car.lane * 10 + 29 == road.pos_lanes[-1]:
            car.left_or_right = 0

    # Which lane switch,  -1 is naar boven
    if car.left_or_right < 0.5:
        car.left_right = -1 
    elif car.left_or_right >= 0.5:
        car.left_right = 1   

    # get the x positions of cars in the lane where the car is going to
    if car.left_right == 1 or car.left_right == -1:
        # going_lane = road.pos_lanes[int(car.lane + car.left_right) - 1]
        cars_x_positions = ([x_pos.x for x_pos in road.lanes[int(car.lane + car.left_right)-1]])
        cars_x_positions.reverse()
        index = bisect.bisect(cars_x_positions, car.x)

        next_car = None
        prev_car = None
        # Find the previous and the next car in the switching lane
        for check_car in all_cars:
            if index is not len(cars_x_positions):
                if check_car.x == cars_x_positions[index]:
                    next_car = check_car
            if index is not 0:
                if check_car.x == cars_x_positions[index - 1]:
                    prev_car = check_car

        # The gap is big enough
        if (prev_car is not None and next_car is not None) and abs((next_car.x - car.x)) > car.gap_want and abs((prev_car.x - car.x)) > car.gap_want:
            car.can_switch = True

def traffic():
    frame = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

    all_cars = Group()
    # Make the road
    road = Road(4,50)
    # print(road.lanes, road.pos_lanes)
    road.add_lane()
    # print(road.lanes, road.pos_lanes)
    road.delete_lane(all_cars)
    # print(road.lanes)

    while True:
        tijd.sleep(0.000005)


        all_cars = vehicle_spawn(road, all_cars)

        for car in all_cars:
            change_lanes = random.uniform(0, 1)

            if change_lanes < 0.005:
                car.switch = True

            # print(road.lanes)
            # print(road.lanes[1][0].speed)
            # find_index = road.lanes[int(car.lane - 1)].index(car)
            # print(road.lanes[1][find_index].speed)
            # print('----------------------------------------')
            # print()



            # car, road, all_cars
            if car.switch is True:


                lane_switching(car, road, all_cars)

                        

                # Y changing from the car to new lane
                if car.can_switch == True:
                    car.y += car.left_right
                elif car.can_switch == False and car.y in road.pos_lanes:
                    car.switch = False
                    
                # lane switch complete
                if car.y in road.pos_lanes:
                    car.lane = (car.y-29) / 10
                    car.switch = False
                    car.image.fill((255,0,0))

            for c in all_cars:
                # Only check cars that are in same lane and in front of car
                if car.y == c.y and car.x < c.x:
                    # gap in lane tussen volgende auto in x
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
                # print(car.speed)
                all_cars.remove(car)
        # tijd.sleep(1)
        # quit pygame
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()


        # make pygame
        frame.blit(background_image, [0, 0])
        all_cars.draw(frame)
        display.update()
        pygame.display.flip()


if __name__ == '__main__':
    traffic()
