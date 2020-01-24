# from .dir import Dir
import pygame
import sys
import os
import math as Math
import numpy as np
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

# background 2 or 3 lanes
# background_image = pygame.image.load("2baans.png")
background_image = pygame.image.load("3baans.png")

# lanes = [lane1, lane2, lane3]
# random.seed(2)

WIDTH = 1920 # 12 km?
HEIGHT = 100
road_length = 12
# CAPTION = 'Traffic Simulator'
pygame.display.set_caption('Traffic Simulator')

# a_thres is used during lane switching to check if the new follow doesn't have to brake to much. a_thresh must be lower than the lowest acceleration of all vehicles.
a_thres = 0.2



def meter_to_pixel(distance):
    # hoeveel pixels in meter
    one_m = WIDTH/(road_length * 1000)
    dist = distance* one_m
    return dist

def pixel_to_meter(pixels):
    # meters in een pixel zitten
    one_p = (road_length * 1000)/WIDTH
    dist = one_p*pixels
    return dist


def vehicle_spawn(road, all_cars, max_speed, car_density):
    chance = random.uniform(0, 1)

    if chance < car_density:
        truck_chance = random.uniform(0,1)
        if truck_chance < 0.80:
            vehicle = Vehicle(chance, 'car', max_speed, (255, 0, 0), [24/2, 12/2], 10, random.choice(road.pos_lanes), 100 + random.randrange(-10,10,2), [0.2,0])
            

        else:
            choice = random.choices(population = road.pos_lanes, weights = [0, 0.01, 0.1, 0.85])
            vehicle = Vehicle(chance, 'truck', max_speed, (0, 0, 255), [98/2, 14/2], 10, choice[0], 80 + random.randrange(-5,5,1), [0.2,0])

        if not spritecollideany(vehicle, all_cars):

            all_cars.add(vehicle)

            # put car in the right lane and keep track of which lane the car is
            for number in range(len(road.pos_lanes)):
                if vehicle.y == road.pos_lanes[number]:
                    road.lanes[number].insert(0, vehicle)

    return all_cars

def lane_switching(car, road, all_cars):

    if car.y in road.pos_lanes:
        car.left_or_right = random.uniform(0, 1)
        # exception if most left lane or most right lane
        if car.lane * 10 + 29 == road.pos_lanes[0]:
            car.left_or_right = 1

        if car.lane * 10 + 29 == road.pos_lanes[-1]:
            car.left_or_right = 0

    # Which lane switch,  -1 is naar boven
    if car.left_or_right < 0.3:
        car.left_right = -1
    else:
        car.left_right = 1

    # get the x positions of cars in the lane where the car is going to
    if car.left_right == 1 or car.left_right == -1:
        cars_x_positions = ([x_pos.x for x_pos in road.lanes[int(car.lane + car.left_right)-1]])
        index = bisect.bisect(cars_x_positions, car.x)
        next_car = None
        prev_car = None

        # Find the previous and the next car in the switching lane
        for check_car in all_cars:

            # If the cars has a leader.
            if index is not len(cars_x_positions):
                if check_car.x == cars_x_positions[index]:
                    next_car = check_car

            # If the car has a follower.
            if index is not 0:
                if check_car.x == cars_x_positions[index - 1]:
                    prev_car = check_car

        # The gap is big enough
        if (prev_car is not None and next_car is not None):

            if compute_gap(car, next_car) > car.gap_want and compute_gap(prev_car, car) > car.gap_want:

                # leader and follower in current lane.
                leader, follower = neighbour_cars(road, car)

                if leader == None:
                    current_gap = 10000
                    current_acc = car.comp_acc(current_gap, car.max_speed)
                else:
                    current_gap = compute_gap(car, leader)
                    current_acc = car.comp_acc(current_gap, leader.speed)

                # Check if new follower does not have to break to much
                prev_gap = compute_gap(prev_car, car)
                prev_acc = prev_car.comp_acc(prev_gap, car.speed)

                # Check if there is an increase in acc
                switch_gap = compute_gap(car, next_car)
                switch_acc = car.comp_acc(switch_gap, next_car.speed)
                

                if switch_acc > (current_acc + a_thres) and prev_acc > -4 :
                    car.can_switch = True
                    car.image.fill((0, 255, 0))

                    if car in road.lanes[int(car.lane-1)]:
                        road.lanes[int(car.lane - 1)].remove(car)
        return(index)


# Returns gap from bumper to bumper in meters.
def compute_gap(follower, leader):
    follower_bumper = follower.x + (follower.size[0] / 2)
    leader_bumper = leader.x - (leader.size[0] / 2)
    if leader.model == 'truck' or follower.model == 'truck':
        gap = leader_bumper - follower_bumper - 20
    else:
        gap = leader_bumper - follower_bumper
    if gap < 0:
        gap = 0.00000001
    return pixel_to_meter(gap)

def neighbour_cars(road, car):
    next_car = None
    prev_car = None

    if car.can_switch == False:
        find_index = road.lanes[int(car.lane - 1)].index(car)

        if find_index + 1 is not len(road.lanes[int(car.lane - 1)]):
            next_car = road.lanes[int(car.lane - 1)][find_index+1]
        if find_index is not 0:
            prev_car = road.lanes[int(car.lane - 1)][find_index-1]

    return next_car, prev_car

def traffic(max_speed, car_density):
    pygame.init()

    clock = pygame.time.Clock()
    clock.tick(60)
    frame = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

    all_cars = Group()
    # Make the road
    road = Road(4,50)
    road.add_lane()
    road.delete_lane(all_cars)
    start_ticks=pygame.time.get_ticks()
    traf_count = 0
    traf_counts = []
    timestamps = []
    # graph time interval
    t = 2


    while True:
        tijd.sleep(0.00000000000000000000000000000000000000000000000000000005)
        seconds=(pygame.time.get_ticks()-start_ticks)/1000


        if int(seconds) % t == 0 and int(seconds) not in timestamps:
            print(int(seconds))
            timestamps.append(int(seconds))
            traf_counts.append(traf_count)
            traf_count = 0

        all_cars = vehicle_spawn(road, all_cars, max_speed, car_density)

        for car in all_cars:
            # if car.x > WIDTH - 10:
                # print(car.speed)
            change_lanes = random.uniform(0, 1)

            if change_lanes < 0.9:
                car.switch = True

            next_car, prev_car = neighbour_cars(road, car)

            if car.switch is True:
                index = lane_switching(car, road, all_cars)

                # Y changing from the car to new lane
                if car.can_switch == True:
                    car.y += car.left_right

                # lane switch complete
                if car.can_switch == True:
                    if car.y in road.pos_lanes:
                        car.lane = (car.y-29) / 10
                        road.lanes[int(car.lane-1)].insert(index, car)
                        car.switch = False
                        car.can_switch = False

                        if car.model == 'car':
                            car.image.fill((255,0,0))
                        else:
                            car.image.fill((0, 0, 255))

            if next_car is not None:
                gap = compute_gap(car, next_car)
                acc = car.comp_acc(gap, next_car.speed)
                car.speed += acc

                # prevent cars from going backwards.
                if car.speed < 0:
                    car.speed = 0
            else:
                gap = 10000
                car.speed += car.comp_acc(gap, car.max_speed)

                if car.speed < 0:
                    car.speed = 0

            car.move()
            if car.x > WIDTH:
                # print(seconds)
                # print(car.speed)
                traf_count += 1
                # print('car has exited', car.speed, car.max_speed)
                road.lanes[int(car.lane - 1)].pop()
                all_cars.remove(car)


        # quit pygame
        if seconds > 30:
            pygame.quit()
            trafficflow = (np.sum(traf_counts) / seconds) *t
            return trafficflow, traf_counts , timestamps



        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()

            if event.type == pygame.QUIT:
                pygame.quit()
                # total average number of vehicles per time interval
                trafficflow = (np.sum(traf_counts) / seconds) *t
                return trafficflow, traf_counts , timestamps

        # make pygame
        frame.blit(background_image, [0, 0])
        all_cars.draw(frame)
        display.update()
        pygame.display.flip()




if __name__ == '__main__':
    intervals1 = np.array([0] * 16)
    intervals2 = np.array([0] * 16)
    intervals3 = np.array([0] * 16)
    tf80 = []
    tf100 = []
    tf130 = []


    for i in range(10):
        tf_l, interval_l, time_l = traffic(80, 0.3)
        tf80.append(tf_l)
        intervals1 = np.add(intervals1, np.array(interval_l))

        tf_l, interval_l, time_l = traffic(100, 0.3)
        tf100.append(tf_l)
        intervals2 = np.add(intervals2, np.array(interval_l))

        tf_l, interval_l, time_l = traffic(130, 0.3)
        tf130.append(tf_l)
        intervals3 = np.add(intervals3, np.array(interval_l))

    plt.figure(figsize=(20,10))
    plt.plot(time_l, intervals1 / 10, label="Trafficflow per time unit %i, %i" % (80, 0.3), c="green")
    plt.plot(time_l, [np.mean(tf80)] * len(time_l), label="Average trafficflow %i, %i" % (80, 0.3), c="lightgreen")

    plt.plot(time_l, intervals2 / 10, label="Trafficflow per time unit %i, %i" % (100, 0.3), c="blue")
    plt.plot(time_l, [np.mean(tf100)] * len(time_l), label="Average trafficflow %i, %i" % (100, 0.3), c="lightblue")

    plt.plot(time_l, intervals3 / 10, label="Trafficflow per time unit %i, %i" % (130, 0.3), c="red")
    plt.plot(time_l, [np.mean(tf130)]  * len(time_l), label="Average trafficflow %i, %i" % (130, 0.3), c="pink")

    plt.xlabel("Time in seconds")
    plt.ylabel("Number of vehicles")
    plt.title("Traffic flow")
    plt.legend()
    plt.show()

    plt.plot(time_l, np.cumsum(intervals1), label="Cummulative trafficflow %i, %i" % (80, 0.3), c="lightgreen")
    plt.plot(time_l, np.cumsum(intervals2), label="Cummulative trafficflow %i, %i" % (100, 0.3), c="lightblue")
    plt.plot(time_l, np.cumsum(intervals3), label="Cummulative trafficflow %i, %i" % (130, 0.3), c="pink")
    plt.legend()
    plt.show()