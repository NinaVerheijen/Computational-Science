# from .dir import Dir
import pygame
import sys
import os
import math as Math
import random
import bisect  
import time as tijd
import matplotlib.pyplot as plt
from pygame import *
from pygame.locals import *
from pygame.sprite import *
from Vehicle import Vehicle
from road import Road

# from Vehicle import Vehicle
os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'

# pygame.init()

# clock = pygame.time.Clock()
# clock.tick(60)

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

def traffic(maxspeed):
    pygame.init()

    clock = pygame.time.Clock()
    clock.tick(60)
    frame = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

    all_cars = Group()
    # Make the road
    road = Road(4,50)
    # print(road.lanes, road.pos_lanes)
    road.add_lane()
    # print(road.lanes, road.pos_lanes)
    road.delete_lane(all_cars)
    # print(road.lanes)
    start_ticks=pygame.time.get_ticks()
    trafficcount = 0
    trafficcountie = 0
    graphie = []
    graphieint = []
    timie = []
    # graphtime interval
    t = 2
    while True:
        tijd.sleep(0.000000000000000000000000000000000000000000000000000000001)
        chance = random.uniform(0, 1)
        seconds=(pygame.time.get_ticks()-start_ticks)/1000


        if int(seconds) % t == 0 and int(seconds) not in timie:
            print(int(seconds))
            graphie.append(trafficcount)
            graphieint.append(trafficcountie)
            trafficcountie = 0
            timie.append(int(seconds))
        # else:
        #     print(int(seconds), seconds, trafficcount, trafficcountie)

        if chance < 0.3:
            truck_chance = random.uniform(0,1)
            if truck_chance < 0.80:
                vehicle = Vehicle(chance, 'car', maxspeed, (255, 0, 0), [24/2, 12/2], -50, random.choice(road.pos_lanes), 50 + random.randrange(-10,10,2), [0.2,0])
                all_cars.add(vehicle)
            else:
                choice = random.choices(population = road.pos_lanes, weights = [0.02, 0.04, 0.1, 0.84])
                vehicle = Vehicle(chance, 'truck', maxspeed, (0, 0, 255), [98/2, 14/2], -50, choice[0], 10 + random.randrange(-5,5,1), [0.2,0])
                all_cars.add(vehicle)

            # put car in the right lane and keep track of which lane the car is
            for number in range(len(road.pos_lanes)):
                if vehicle.y == road.pos_lanes[number]:
                    road.lanes[number].append(vehicle)

        for car in all_cars:
            change_lanes = random.uniform(0, 1)

            if change_lanes < 0.005:
                car.switch = True

            if car.switch is True:
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
                    going_lane = road.pos_lanes[int(car.lane + car.left_right) - 1]
                    cars_x_positions = ([x_pos.x for x_pos in road.lanes[int(car.lane + car.left_right)-1]])
                    cars_x_positions.reverse()
                    index = bisect.bisect(cars_x_positions, car.x)

                    # Find the previous and the next car in the switching lane
                    for check_car in all_cars:
                        if index is not len(cars_x_positions):
                            if check_car.x == cars_x_positions[index]:
                                next_car = check_car
                        else:
                            next_car = None
                        if index is not 0:
                            if check_car.x == cars_x_positions[index - 1]:
                                prev_car = check_car
                        else:
                            prev_car = None

                    # The gap is big enough
                    if (prev_car is not None and next_car is not None) and abs((next_car.x - car.x)) > car.gap_want and abs((prev_car.x - car.x)) > car.gap_want:
                        car.can_switch = True
                        

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
                trafficcount += 1
                trafficcountie += 1
                all_cars.remove(car)

        # quit pygame
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()

            if event.type == pygame.QUIT:
                # total average number of vehicles per time interval
                trafficflow = (trafficcount / seconds) *t
                pygame.quit()
                return trafficflow, graphie, graphieint, timie


        # make pygame
        frame.blit(background_image, [0, 0])
        all_cars.draw(frame)
        display.update()
        pygame.display.flip()




if __name__ == '__main__':
    # run traffic lower speed
    average_tf_l, cummulative_tf_l, interval_tf_l, timeline_l = traffic(100)
    # run traffic higher speed
    average_tf_h, cummulative_tf_h, interval_tf_h, timeline_h = traffic(130)

    # print(timie, graphieint, graphie)
    # print(timie1, graphieint1, graphie1)
    # plt.plot(timie, graphie, label="100 cumm")
    # plt.plot(timie, graphieint, label="100 int")
    # plt.legend()
    # # plt.show()
    # plt.plot(timie1, graphie1, label="130 cumm")
    # plt.plot(timie1, graphieint1, label="130 int")
    # plt.legend()
    # plt.show()
    # maxspeed = 130
    # timeinterval = 2
    # print(traffic(maxspeed, timeinterval))
    # print(traffic(120, timeinterval))



    # plt.plot(timeline, cummulative_tf, label="Cummulative trafficflow", c="#7F98FF")
    # plt.plot(timeline, interval_tf, label="Trafficflow per time unit", c="#3152D4")
    # plt.plot(timeline, [average_tf] * len(timeline), label="Average trafficflow", c="#001F9A")
    plt.plot(timeline_l, cummulative_tf_l, label="Cummulative trafficflow", c="lightblue")
    plt.plot(timeline_l, interval_tf_l, label="Trafficflow per time unit", c="blue")
    plt.plot(timeline_l, [average_tf_l] * len(timeline_l), label="Average trafficflow", c="darkblue")
    plt.legend()
    plt.show()
    
